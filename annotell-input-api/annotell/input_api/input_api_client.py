"""Client for communicating with the Annotell platform."""
import logging
import mimetypes
import random
from pathlib import Path
from typing import List, Mapping, Optional, Union, Dict, BinaryIO
from uuid import uuid4 as uuid
from annotell.input_api.util import filter_none

import requests
import time
from PIL import Image
from annotell.auth.authsession import (
    FaultTolerantAuthRequestSession, DEFAULT_HOST as DEFAULT_AUTH_HOST
)

from . import input_api_model as IAM

DEFAULT_HOST = "https://input.annotell.com"

log = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = [408, 429, 500, 501, 502, 503,
                          504, 505, 506, 507, 508, 509, 510, 511, 598, 599]


class InputApiClient:
    """Creates Annotell inputs from local files."""

    def __init__(self, *,
                 auth=None,
                 host: str = DEFAULT_HOST,
                 auth_host: str = DEFAULT_AUTH_HOST,
                 client_organization_id: int = None,
                 max_upload_retry_attempts: int = 23,
                 max_upload_retry_wait_time: int = 60):
        """
        :param auth: auth credentials, see
        https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id.
        Only works with an Annotell user.
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """

        self.host = host
        self._auth_req_session = FaultTolerantAuthRequestSession(host=auth_host, auth=auth)
        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json"
        }
        self.dryrun_header = {"X-Dryrun": ""}

        self.MAX_NUM_UPLOAD_RETRIES = max_upload_retry_attempts
        self.MAX_RETRY_WAIT_TIME = max_upload_retry_wait_time  # seconds
        if client_organization_id is not None:
            self.headers["X-Organization-Id"] = str(client_organization_id)
            c_org_id = client_organization_id
            log.info(f"WARNING: You will now act as if you are part of organization: {c_org_id}. "
                     f"This will not work unless you are an Annotell user.")

    @property
    def session(self):
        return self._auth_req_session

    @staticmethod
    def _raise_on_error(resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as exception:
            if (exception.response is not None and exception.response.status_code == 400):
                message = ""
                try:
                    message = exception.response.json()["message"]
                except ValueError:
                    message = exception.response.text
                raise RuntimeError(message) from exception

            raise exception from None
        return resp

    def _get_upload_urls(self, files_to_upload: IAM.FilesToUpload):
        """Get upload urls to cloud storage"""
        url = f"{self.host}/v1/inputs/upload-urls"
        resp = self.session.get(url, json=files_to_upload.to_dict(), headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.UploadUrlsResponse.from_json(json_resp)

    @staticmethod
    def _set_images_dimensions(folder: Path, images: List[IAM.Image]) -> None:
        def _is_image_missing_dimensions(img: IAM.Image):
            return img.width is None or img.height is None

        for image in images:
            if _is_image_missing_dimensions(image):
                fi = folder.joinpath(image.filename).expanduser()
                with Image.open(fi) as im:
                    width, height = im.size
                    image.height = height
                    image.width = width

    @staticmethod
    def _unwrap_enveloped_json(js: dict) -> dict:
        if js.get(IAM.ENVELOPED_JSON_TAG) is not None:
            return js[IAM.ENVELOPED_JSON_TAG]
        return js

    @staticmethod
    def _get_content_type(filename: str) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
        if filename.split(".")[-1] == "csv":
            content_type = "text/csv"
        else:
            ct = mimetypes.guess_type(filename)[0]
            content_type = ct if ct is not None else 'application/octet-stream'

        return content_type

    def _get_wait_time(self, upload_attempt: int) -> int:
        """
        Calculates the wait time before attempting another file upload to GCS

        :param upload_attempt: How many attempts to upload that have been made
        :return: int: The time to wait before retrying upload
        """
        max_wait_time = pow(2, upload_attempt - 1)
        wait_time = random.random()*max_wait_time
        wait_time = wait_time if wait_time < self.MAX_RETRY_WAIT_TIME else self.MAX_RETRY_WAIT_TIME
        return wait_time

    #  Using similar retry strategy as gsutil
    #  https://cloud.google.com/storage/docs/gsutil/addlhelp/RetryHandlingStrategy
    def _upload_file(
            self, upload_url: str, file: BinaryIO, headers: Dict[str, str],
            upload_attempt: int = 1) -> None:
        """
        Upload the file to GCS, retries if the upload fails with some specific status codes.
        """
        log.info(f"Uploading file={file.name}")
        resp = self.session.put(upload_url, data=file, headers=headers)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(f"On upload attempt ({upload_attempt}/{self.MAX_NUM_UPLOAD_RETRIES}) to GCS "
                      f"got response:\n{resp.status_code}: {resp.content}")

            attempt_cond = upload_attempt < self.MAX_NUM_UPLOAD_RETRIES
            status_code_cond = resp.status_code in RETRYABLE_STATUS_CODES

            if attempt_cond and status_code_cond:
                wait_time = self._get_wait_time(upload_attempt)
                log.info(f"Waiting {int(wait_time)} seconds before retrying")
                time.sleep(wait_time)
                self._upload_file(upload_url, file, headers, upload_attempt + 1)
            else:
                raise e

        except Exception as e:
            raise e

    def _upload_files(self, folder: Path, url_map: Mapping[str, str]) -> None:
        """Upload all files to cloud storage"""
        for (filename, upload_url) in url_map.items():
            file_path = folder.joinpath(filename).expanduser()
            with file_path.open('rb') as file:
                content_type = self._get_content_type(filename)
                headers = {"Content-Type": content_type}
                self._upload_file(upload_url, file, headers)

    def _resolve_request_url(self,
                             resource_path: str,
                             project: Optional[str] = None,
                             batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = f"{self.host}/v1/inputs/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path

        return url

    def _post_input_request(self, resource_path: str,
                            input_request: dict,
                            project: Optional[str],
                            batch: Optional[str],
                            input_list_id: Optional[int],
                            dryrun: bool = False):
        if dryrun:
            headers = {**self.headers, **self.dryrun_header}
        else:
            headers = {**self.headers}

        if (input_list_id is not None):
            input_request['inputListId'] = input_list_id

        request_url = self._resolve_request_url(resource_path, project, batch)
        resp = self.session.post(request_url, json=input_request, headers=headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        if not dryrun:
            return IAM.CreateInputJobResponse.from_json(json_resp)

    def _create_inputs_point_cloud_with_images(
            self, point_clouds_with_images: IAM.PointCloudsWithImages,
            internal_id: str,
            metadata: IAM.CalibratedSceneMetaData,
            project: Optional[str],
            batch: Optional[str],
            input_list_id: Optional[int],
            dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """Create point cloud with images"""

        js = dict(
            files=point_clouds_with_images.to_dict(),
            internalId=internal_id,
            metadata=metadata.to_dict())

        resp = self._post_input_request(
            'pointclouds-with-images',
            js,
            project=project,
            batch=batch,
            input_list_id=input_list_id,
            dryrun=dryrun
        )
        return resp

    def _create_inputs_point_clouds(self, point_clouds: IAM.PointCloudFiles,
                                    internal_id: str,
                                    metadata: IAM.SceneMetaData,
                                    project: Optional[str],
                                    batch: Optional[str],
                                    input_list_id: Optional[int],
                                    dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """Create point clouds"""

        js = dict(
            files=point_clouds.to_dict(),
            internalId=internal_id,
            metadata=metadata.to_dict())

        resp = self._post_input_request(
            'pointclouds',
            js,
            project=project,
            batch=batch,
            input_list_id=input_list_id,
            dryrun=dryrun
        )
        return resp

    def _create_images_input_job(self, images_files: IAM.ImagesFiles,
                                 metadata: IAM.SceneMetaData,
                                 internal_id: str,
                                 project: Optional[str],
                                 batch: Optional[str],
                                 input_list_id: Optional[int],
                                 dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Creates an input job for an image input

        :param images_files: Contains all images, with their dimensions
        :param metadata: Contains necessary metadata in order to create and validate inputs
        :param input_list_id: input list id which the new input will be added to
        :param internal_id: When created, the input will use this internal id.
        :param dryrun: If True the files/metadata will be validated but no input job will
        be created.
        :returns CreateInputJobResponse: Class containing id of the created input job, or None
        if dryrun
        """

        create_input_job_json = dict(files=images_files.to_dict(),
                                     metadata=metadata.to_dict(),
                                     internalId=internal_id)
        resp = self._post_input_request(
            'images', create_input_job_json, project=project, batch=batch,
            input_list_id=input_list_id, dryrun=dryrun
        )
        return resp

    def create_inputs_images(
            self, folder: Path,
            images_files: IAM.ImagesFiles,
            metadata: IAM.SceneMetaData = IAM.SceneMetaData(external_id=str(uuid())),
            project: Optional[str] = None,
            batch: Optional[str] = None,
            input_list_id: Optional[int] = None,
            dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Verifies the images and metadata given and then uploads images to Google Cloud Storage and
        creates an input job.
        :param folder: Absolute path to directory containing all images.
        :param images_files: List containing all images for the input.
        :param metadata: class containing metadata necessary for creating input from images.
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job
        will be created.
        :returns InputJobCreatedMessage: Class containing id of the created input job,
        or None if dryrun.
        """

        self._set_images_dimensions(folder, images_files.images)

        filenames = [image.filename for image in images_files.images]
        upload_url_resp = self._get_upload_urls(IAM.FilesToUpload(filenames))

        internal_id = upload_url_resp.internal_id
        self._create_images_input_job(images_files=images_files,
                                      metadata=metadata,
                                      internal_id=internal_id,
                                      project=project,
                                      batch=batch,
                                      input_list_id=input_list_id,
                                      dryrun=True)

        files_in_response = upload_url_resp.files_to_url.keys()
        assert set(filenames) == set(files_in_response)

        if not dryrun:
            self._upload_files(folder, upload_url_resp.files_to_url)
            input_job_created_message = self._create_images_input_job(images_files=images_files,
                                                                      metadata=metadata,
                                                                      internal_id=internal_id,
                                                                      project=project,
                                                                      batch=batch,
                                                                      input_list_id=input_list_id
                                                                      )
            if input_job_created_message:
                int_id = input_job_created_message.internal_id
                log.info(
                    f"Creating input for images with internal_id={int_id}")
            return input_job_created_message
        return None

    def create_inputs_point_clouds(
            self, folder: Path,
            point_clouds: IAM.PointCloudFiles,
            metadata: IAM.SceneMetaData = IAM.SceneMetaData(external_id=str(uuid())),
            project: Optional[str] = None,
            batch: Optional[str] = None,
            input_list_id: Optional[int] = None,
            dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Upload files and create an input of type 'point_cloud'.

        :param folder: path to folder containing files
        :param point_clouds: list of pointclouds that constitute the input
        :param metadata: Class containing metadata necessary for point cloud
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job will
        be created.
        :returns CreateInputJobResponse: Class containing id of the created input job,
        or None if dryrun.

        The files are uploaded to annotell GCS and an input_job is submitted to the inputEngine.
        In order to increase annotation tool performance the supplied pointcloud-file is converted
        into potree after upload (server side). Supported fileformats for pointcloud files are
        currently .csv & .pcd (more information about formatting can be found in the readme.md).
        The job is successful once it converts the pointcloud file into potree, at which time an
        input of type 'point_cloud' is created for the designated `project` `batch` or
        `input_list_id`. If the input_job fails (cannot perform conversion) the input is not added.
        To see if conversion was successful please see the method `get_input_jobs_status`.
        """

        files_on_disk = [pc.filename for pc in point_clouds.point_clouds]

        upload_urls_response = self._get_upload_urls(IAM.FilesToUpload(files_on_disk))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_on_disk) == set(files_in_response)

        self._create_inputs_point_clouds(point_clouds,
                                         upload_urls_response.internal_id,
                                         metadata,
                                         project=project,
                                         batch=batch,
                                         input_list_id=input_list_id,
                                         dryrun=True)
        if not dryrun:
            # self._upload_files(folder, upload_urls_response.files_to_url)

            create_input_response = self._create_inputs_point_clouds(
                point_clouds,
                upload_urls_response.internal_id,
                metadata,
                project=project,
                batch=batch,
                input_list_id=input_list_id,
            )
            if create_input_response:
                log.info(
                    f"Creating inputs for files with job_id={create_input_response.internal_id}"
                )
            return create_input_response
        return None

    def create_inputs_point_cloud_with_images(
            self, folder: Path,
            point_clouds_with_images: IAM.PointCloudsWithImages,
            metadata: IAM.CalibratedSceneMetaData,
            project: Optional[str] = None,
            batch: Optional[str] = None,
            input_list_id: Optional[int] = None,
            dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Upload files and create an input of type 'point_cloud_with_image'.

        :param folder: path to folder containing files
        :param point_clouds_with_images: class containing images and pointclouds that
        constitute the input
        :param metadata: Class containing metadata necessary for point cloud with images
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job will be
        created.
        :returns CreateInputJobResponse: Class containing id of the created input job,
        or None if dryrun.

        The files are uploaded to annotell GCS and an input_job is submitted to the inputEngine.
        In order to increase annotation tool performance the supplied pointcloud-file is converted
        into potree after upload (server side). Supported fileformats for pointcloud files are
        currently .csv & .pcd (more information about formatting can be found in the readme.md).
        The job is successful once it converts the pointcloud file into potree, at which time an
        input of type 'point_cloud_with_image' is created for the designated `project` `batch` or
        `input_list_id`. If the input_job fails (cannot perform conversion) the input is not added.
        To see if conversion was successful please see the method `get_input_jobs_status`.
        """

        files_on_disk = [image.filename for image in point_clouds_with_images.images] + \
                        [pc.filename for pc in point_clouds_with_images.point_clouds]

        upload_urls_response = self._get_upload_urls(IAM.FilesToUpload(files_on_disk))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_on_disk) == set(files_in_response)

        self._set_images_dimensions(folder, point_clouds_with_images.images)
        self._create_inputs_point_cloud_with_images(point_clouds_with_images,
                                                    upload_urls_response.internal_id,
                                                    metadata,
                                                    project=project,
                                                    batch=batch,
                                                    input_list_id=input_list_id,
                                                    dryrun=True)
        if not dryrun:
            self._upload_files(folder, upload_urls_response.files_to_url)

            create_input_response = self._create_inputs_point_cloud_with_images(
                point_clouds_with_images,
                upload_urls_response.internal_id,
                metadata,
                project=project,
                batch=batch,
                input_list_id=input_list_id,
            )

            if create_input_response:
                log.info(
                    f"Creating inputs for files with job_id={create_input_response.internal_id}"
                )
            return create_input_response
        return None

    def create_slam_input_job(self, slam_files: IAM.SlamFiles,
                              metadata: IAM.SlamMetaData,
                              project: Optional[str] = None,
                              batch: Optional[str] = None,
                              input_list_id: Optional[int] = None,
                              dryrun=False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Creates a slam input job, then sends a message to inputEngine which will request for a
        SLAM job to be started.

        :param slam_files: class containing files necessary for SLAM.
        :param metadata: class containing metadata necessary for SLAM.
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but
        no input job will be created.
        :returns CreateInputJobResponse: Class containing id of the created input job,
        or None if dryrun.
        """

        slam_json = dict(files=slam_files.to_dict(),
                         metadata=metadata.to_dict(), inputListId=input_list_id)

        resp = self._post_input_request(
            'slam',
            slam_json,
            project=project,
            batch=batch,
            input_list_id=input_list_id,
            dryrun=dryrun
        )
        return resp

    def update_completed_slam_input_job(self, pointcloud_uri: str,
                                        trajectory: IAM.Trajectory,
                                        job_id: str) -> None:
        """
        Updates an input job with data about the created SLAM, then sends a message to inputEngine
        which will create an input. The method will throw an error if the operation was
        unsuccessful.

        :param pointcloud_uri: URI pointing to a SLAM:ed pointcloud in either s3 or gs cloud
        storage.
        :param trajectory: class containing the trajectory of the SLAM:ed pointcloud.
        :param job_id: UUID for the input job.
        :returns None
        """
        url = f"{self.host}/v1/inputs/progress"
        update_json = dict(files=dict(pointClouds=pointcloud_uri),
                           metadata=dict(trajectory=trajectory.to_dict()),
                           jobId=job_id)
        resp = self.session.post(url, json=update_json, headers=self.headers)
        self._raise_on_error(resp).json()

    def update_failed_slam_input_job(self, job_id: str, message: str) -> None:
        """
        Updates an input job with an error message, then sends a message to inputEngine which will
        notify the responsible party about the failed input job. The method will throw an error if
        the operation was unsuccessful.

        :param job_id: UUID for the input job.
        :param message: String with the error message.
        :returns None
        """
        url = f"{self.host}/v1/inputs/progress"
        update_json = dict(jobId=job_id, message=message)
        resp = self.session.post(url, json=update_json, headers=self.headers)
        self._raise_on_error(resp).json()

    def get_inputs(self,
                   project: str,
                   batch: Optional[str] = None,
                   external_ids: Optional[List[str]] = None,
                   include_invalidated: bool = False) -> List[IAM.Input]:
        """
        Gets inputs for project, with option to include invalidated inputs in the list
        (by default invalidated inputs are omitted)

        :param project: Project to filter
        :param batch: Batch to filter, if omitted inputs from all batches are included.
        :param invalidated: If true, includes invalidated inputs in the response
        :return List: List of Inputs
        """

        url = f"{self.host}/v1/inputs"
        external_ids_query_string = ",".join(external_ids) if external_ids is not None else None
        params = {
            "project": project,
            "batch": batch,
            "externalIds": external_ids_query_string,
            "invalidated": include_invalidated
        }

        resp = self.session.get(url, params=filter_none(params), headers=self.headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return [IAM.Input.from_json(js) for js in json_resp]

    def invalidate_inputs(self,
                          input_internal_ids: List[str],
                          invalidated_reason: IAM.InvalidatedReasonInput) -> IAM.InvalidatedInputsResponse:
        """
        Invalidates inputs, and removes them from all input lists

        :param input_internal_ids: The input internal ids to invalidate
        :param invalidated_reason: An Enum describing why inputs were invalidated
        :return InvalidatedInputsResponse: Class containing what inputs were invalidated
        """
        url = f"{self.host}/v1/inputs/invalidate"
        invalidated_json = dict(inputIds=input_internal_ids, invalidatedReason=invalidated_reason)
        resp = self.session.post(url, json=invalidated_json, headers=self.headers)
        resp_json = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return IAM.InvalidatedInputsResponse.from_json(resp_json)

    def get_projects(self) -> List[IAM.Project]:
        """
        Returns all projects connected to the users organization.

        :return List: List containing all projects connected to the user
        """
        url = f"{self.host}/v1/projects"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return [IAM.Project.from_json(js) for js in json_resp]

    def get_project_batches(self, project: str) -> List[IAM.InputBatch]:
        """
        Returns all `batches` for the `project`.

        :param project: Project identifier
        :return List: List containing all batches
        """
        url = f"{self.host}/v1/projects/{project}/batches"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return [IAM.InputBatch.from_json(js) for js in json_resp]

    def get_calibration_data(
        self, id: Optional[int] = None, external_id: Optional[str] = None
    ) -> List[Union[IAM.CalibrationNoContent, IAM.CalibrationWithContent]]:
        """
        Queries the Input API for either:
        * A list containing a specific calibration (of only the id is given)
        * A list of calibrations connected to an external_id (if only the external_id is given)
        * A list of calibrations connected to the users organization.
        Note that both id and external_id cannot be given at the same time.

        :param id: The id of the calibration to get
        :param external_id: The external id of the calibration(s) to get
        :return List: A list of CalibrationNoContent if an id or external id was given, or a
        list of CalibrationWithContent otherwise.
        """
        base_url = f"{self.host}/v1/inputs/calibration-data"
        if id:
            url = base_url + f"?id={id}"
        elif external_id:
            url = base_url + f"?externalId={external_id}"
        else:
            url = base_url

        resp = self.session.get(url, headers=self.headers)

        json_resp = self._raise_on_error(resp).json()
        if base_url == url:
            return [IAM.CalibrationNoContent.from_json(js) for js in json_resp]
        elif id is not None:
            return [IAM.CalibrationWithContent.from_json(json_resp)]
        else:
            return [IAM.CalibrationWithContent.from_json(js) for js in json_resp]

    def create_calibration_data(
        self, calibration_spec: IAM.CalibrationSpec
    ) -> IAM.CalibrationNoContent:
        """
        Creates a new calibration, given the CalibrationSpec
        :param calibration_spec: A CalibrationSpec instance containing everything to
        create a calibration.
        :return CalibrationNoContent: Class containing the calibration id, external id and
        time of creation.
        """
        url = f"{self.host}/v1/inputs/calibration-data"
        resp = self.session.post(url, json=calibration_spec.to_dict(), headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.CalibrationNoContent.from_json(json_resp)

    def download_annotations(
        self, internal_ids: List[str]
    ) -> Dict[str, List[IAM.ExportAnnotation]]:
        """
        Returns the export ready annotations for each input (via the internal id).

        :param internal_ids: List with internal ids
        :return Dict: A dictionary, with each key corresponding internal_id, and value
        corresponding to a list of the ready annotations for the associated input.
        """
        url = f"{self.host}/v1/inputs/export"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()

        for k, v in json_resp.items():
            inner_list = list()
            for kk, vv in v.items():
                inner_list.append(IAM.ExportAnnotation.from_json(vv))
            json_resp[k] = inner_list
        return json_resp

    def get_view_links(self, internal_ids: List[str]) -> Dict[str, str]:
        """
        For each given internal id returns an URL where the input can be viewed in the web app.

        :param internal_ids: List with internal ids
        :return Dict: Dictionary mapping each internal id with an URL to view the input.
        """
        view_dict = dict()
        for internal_id in internal_ids:
            view_dict[internal_id] = f"https://app.annotell.com/input-view/{internal_id}"

        return view_dict
