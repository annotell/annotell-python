"""Client for communicating with the Annotell platform."""
import requests
import logging
from typing import List, Mapping, Optional, Union, Dict
from pathlib import Path
import mimetypes
from PIL import Image
from . import __version__
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST
from . import input_api_model as IAM

DEFAULT_HOST = "https://input.annotell.com"

log = logging.getLogger(__name__)


class InputApiClient:
    """Creates Annotell inputs from local files."""

    def __init__(self, *,
                 auth: None,
                 host: str = DEFAULT_HOST,
                 auth_host: str = DEFAULT_AUTH_HOST,
                 client_organization_id: int = None):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id. Only works with an Annotell user.
        """

        self.host = host

        self.oauth_session = AuthSession(host=auth_host, auth=auth)

        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": f"annotell-cloud-storage:{__version__}"
        }
        self.dryrun_header = {"X-Dryrun": ""}

        if client_organization_id is not None:
            self.headers["X-Organization-Id"] = str(client_organization_id)
            log.info(f"WARNING: You will now act as if you are part of organization: {client_organization_id}. "
                     f"This will not work unless you are an Annotell user.")

    @property
    def session(self):
        return self.oauth_session.session

    @staticmethod
    def _raise_on_error(resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(
                f"Got {resp.status_code} error calling url={resp.url}, got response:\n{resp.content}")
            raise
        return resp

    def _get_upload_urls(self, files_to_upload: IAM.FilesToUpload):
        """Get upload urls to cloud storage"""
        url = f"{self.host}/v1/inputs/upload-urls"
        resp = self.session.get(url, json=files_to_upload.to_dict(), headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.UploadUrlsResponse.from_json(json_resp)

    @staticmethod
    def _set_images_dimensions(folder: Path, images: List[IAM.Image]):

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

    def _upload_files(self, folder: Path, url_map: Mapping[str, str]):
        """Upload all files to cloud storage"""
        for (file, upload_url) in url_map.items():
            fi = folder.joinpath(file).expanduser()
            log.info(f"Uploading file={fi}")
            with fi.open('rb') as f:
                content_type = mimetypes.guess_type(file)[0]
                # Needed for pcd
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
                if not content_type:
                    content_type = 'application/octet-stream'
                headers = {"Content-Type": content_type}
                resp = self.session.put(upload_url, data=f, headers=headers)
                try:
                    resp.raise_for_status()
                except requests.HTTPError as e:
                    log.error(f"Got {resp.status_code} error calling cloud bucket upload, "
                              f"got response\n{resp.content}")

    def _create_inputs_point_cloud_with_images(self, point_clouds_with_images: IAM.PointCloudsWithImages,
                                               job_id: str,
                                               input_list_id: int,
                                               metadata: IAM.CalibratedSceneMetaData):

        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.host}/v1/inputs/pointclouds-with-images"
        js = dict(
            files=point_clouds_with_images.to_dict(),
            internalId=job_id,
            inputListId=input_list_id,
            metadata=metadata.to_dict())

        resp = self.session.post(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.CreateInputJobResponse.from_json(json_resp)

    def create_inputs_point_cloud_with_images(self, folder: Path,
                                              point_clouds_with_images: IAM.PointCloudsWithImages,
                                              input_list_id: int,
                                              metadata: IAM.CalibratedSceneMetaData) -> IAM.CreateInputJobResponse:
        """
        Upload files and create an input of type 'point_cloud_with_image'.

        :param folder: path to folder containing files
        :param point_clouds_with_images: class containing images and pointclouds that constitute the input
        :param input_list_id: input list to add input to
        :param metadata:

        The files are uploaded to annotell GCS and an input_job is submitted to the inputEngine.
        In order to increase annotation tool performance the supplied pointcloud-file is converted
        into potree after upload (server side). Supported fileformats for pointcloud files are
        currently .csv & .pcd (more information about formatting can be found in the readme.md).
        The job is successful once it converts the pointcloud file into potree, at which time an
        input of type 'point_cloud_with_image' is created for the designated `input_list_id`.
        If the input_job fails (cannot perform conversion) the input is not added. To see if
        conversion was successful please see the method `get_input_jobs_status`.
        """

        files_on_disk = [image.filename for image in point_clouds_with_images.images] + \
                        [pc.filename for pc in point_clouds_with_images.point_clouds]

        upload_urls_response = self._get_upload_urls(IAM.FilesToUpload(files_on_disk))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_on_disk) == set(files_in_response)

        self._upload_files(folder, upload_urls_response.files_to_url)
        self._set_images_dimensions(folder, point_clouds_with_images.images)

        create_input_response = self._create_inputs_point_cloud_with_images(point_clouds_with_images,
                                                                            upload_urls_response.internal_id,
                                                                            input_list_id,
                                                                            metadata)
        return create_input_response

    def create_slam_input_job(self, slam_files: IAM.SlamFiles,
                              metadata: IAM.SlamMetaData,
                              input_list_id: int,
                              dryrun=False):
        """
        Creates a slam input job, then sends a message to inputEngine which will request for a SLAM job to be
        started.

        :param slam_files: class containing files necessary for SLAM.
        :param metadata: class containing metadata necessary for SLAM.
        :param input_list_id: ID of the input list the new input, when created, will be added to.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreatedMessage: Class containing id of the created input job, or nothing if dryrun.
        """
        if dryrun:
            headers = {**self.headers, **self.dryrun_header}
        else:
            headers = {**self.headers}

        url = f"{self.host}/v1/inputs/slam"
        slam_json = dict(files=slam_files.to_dict(), metadata=metadata.to_dict(), inputListId=input_list_id)
        resp = self.session.post(url, json=slam_json, headers=headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())

        if not dryrun:
            return IAM.CreateInputJobResponse.from_json(json_resp)

    def upload_and_create_images_input_job(self, folder: Path,
                                           images_files: IAM.ImagesFiles,
                                           metadata: IAM.SceneMetaData,
                                           input_list_id: int,
                                           dryrun: bool = False):
        """
        Verifies the images and metadata given and then uploads images to Google Cloud Storage and
        creates an input job.
        :param folder: Absolute path to directory containing all images.
        :param images_files: List containing all images for the input.
        :param metadata: class containing metadata necessary for creating input from images.
        :param input_list_id: ID of the input list the new input, when created, will be added to.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreatedMessage: Class containing id of the created input job, or None if dryrun.
        """

        self._set_images_dimensions(folder, images_files.images)

        filenames = [image.filename for image in images_files.images]
        upload_url_resp = self._get_upload_urls(IAM.FilesToUpload(filenames))

        internal_id = upload_url_resp.internal_id
        self._create_images_input_job(images_files=images_files,
                                      metadata=metadata,
                                      input_list_id=input_list_id,
                                      internal_id=internal_id,
                                      dryrun=True)

        files_in_response = upload_url_resp.files_to_url.keys()
        assert set(filenames) == set(files_in_response)

        if not dryrun:
            self._upload_files(folder, upload_url_resp.files_to_url)
            input_job_created_message = self._create_images_input_job(images_files=images_files,
                                                                      metadata=metadata,
                                                                      input_list_id=input_list_id,
                                                                      internal_id=internal_id)
            log.info(f"Creating input for images with internal_id={input_job_created_message.internal_id}")
            return input_job_created_message

    def _create_images_input_job(self, images_files: IAM.ImagesFiles,
                                 metadata: IAM.SceneMetaData,
                                 input_list_id: int,
                                 internal_id: str = None,
                                 dryrun: bool = False):
        """
        Creates an input job for an image input

        :param images_files: Contains all images, with their dimensions
        :param metadata: Contains necessary metadata in order to create and validate inputs
        :param input_list_id: ID of the input list the new input, when created, will be added to.
        :param internal_id: When created, the input will use this internal id.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreatedMessage: Class containing id of the created input job, or None if dryrun
        """

        if dryrun:
            headers = {**self.headers, **self.dryrun_header}
        else:
            headers = {**self.headers}

        create_input_job_url = f"{self.host}/v1/inputs/images"
        create_input_job_json = dict(files=images_files.to_dict(),
                                     metadata=metadata.to_dict(),
                                     inputListId=input_list_id,
                                     internalId=internal_id)

        resp = self.session.post(create_input_job_url, json=create_input_job_json, headers=headers)
        json_resp = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        if not dryrun:
            return IAM.CreateInputJobResponse.from_json(json_resp)

    def update_completed_slam_input_job(self, pointcloud_uri: str,
                                        trajectory: IAM.Trajectory,
                                        job_id: str):
        """
        Updates an input job with data about the created SLAM, then sends a message to inputEngine which
        will create an input.

        :param pointcloud_uri: URI pointing to a SLAM:ed pointcloud in either s3 or gs cloud storage.
        :param trajectory: class containing the trajectory of the SLAM:ed pointcloud.
        :param job_id: UUID for the input job.
        :returns SlamJobUpdated: Class with boolean describing if the update was successful or not.
        """
        url = f"{self.host}/v1/inputs/progress"
        update_json = dict(files=dict(pointClouds=pointcloud_uri),
                           metadata=dict(trajectory=trajectory.to_dict()),
                           jobId=job_id)
        resp = self.session.post(url, json=update_json, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return json_resp

    def update_failed_slam_input_job(self, job_id: str, message: str):
        """
        Updates an input job with an error message, then sends a message to inputEngine which will
        notify the responsible party about the failed input job.

        :param job_id: UUID for the input job.
        :param message: String with the error message.
        :returns SlamJobUpdated: Class with boolean describing if the update was successful or not.
        """
        url = f"{self.host}/v1/inputs/progress"
        update_json = dict(jobId=job_id, message=message)
        resp = self.session.post(url, json=update_json, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return json_resp

    def get_internal_ids_for_external_ids(self, external_ids: List[str]) -> Dict[str, List[str]]:
        url = f"{self.host}/v1/inputs/"
        js = external_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def mend_input_data(self):
        """Not yet implemented."""
        url = f"{self.host}/v1/inputs/mend-input-metadata"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def invalidate_inputs(self, input_ids: List[int], invalidated_reason: IAM.InvalidatedReasonInput):
        """
        Invalidates inputs, and removes them from all input lists

        :param input_ids: The input IDs to invalidate
        :param invalidated_reason: Description why inputs were invalidate
        :return InvalidatedInputsResponse: Class containing what inputs were invalidated
        """
        url = f"{self.host}/v1/inputs/invalidate"
        invalidated_json = dict(inputIds=input_ids, invalidatedReason=invalidated_reason)
        resp = self.session.post(url, json=invalidated_json, headers=self.headers)
        resp_json = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return IAM.InvalidatedInputsResponse.from_json(resp_json)

    def remove_inputs_from_input_list(self, input_list_id: int, input_ids: List[int]):
        """
        Removes inputs from specified input list, without invalidating the input

        :param input_list_id: The input list where inputs should be removed
        :param input_ids: The input IDs to remove
        :return RemovedInputsResponse: Class containing what inputs were removed
        """
        url = f"{self.host}/v1/inputs/remove"
        removed_json = dict(inputListId=input_list_id, inputIds=input_ids)
        resp = self.session.post(url, json=removed_json, headers=self.headers)
        resp_json = self._unwrap_enveloped_json(self._raise_on_error(resp).json())
        return IAM.RemovedInputsResponse.from_json(resp_json)

    def list_projects(self) -> List[IAM.Project]:
        url = f"{self.host}/v1/inputs/projects"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAM.Project.from_json(js) for js in json_resp]

    def list_input_lists(self, project_id: int) -> List[IAM.InputList]:
        url = f"{self.host}/v1/inputs/input-lists?projectId={project_id}"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAM.InputList.from_json(js) for js in json_resp]

    def get_calibration_data(self, id: Optional[int] = None, external_id: Optional[str] = None
                             ) -> Union[List[IAM.CalibrationNoContent], List[IAM.CalibrationWithContent]]:
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
        else:
            return [IAM.CalibrationWithContent.from_json(js) for js in json_resp]

    def create_calibration_data(self, calibration: IAM.Calibration, external_id: str
                                ) -> IAM.CalibrationNoContent:
        url = f"{self.host}/v1/inputs/calibration-data"
        js = dict(
            externalId=external_id,
            calibration=calibration.to_dict()
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.CalibrationNoContent.from_json(json_resp)

    def get_requests_for_request_ids(self, request_ids: List[int]) -> Dict[int, IAM.Request]:
        url = f"{self.host}/v1/inputs/requests"
        js = request_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        dict_resp = dict()
        for k, v in json_resp.items():
            dict_resp[int(k)] = IAM.Request.from_json(v)
        return dict_resp

    def get_requests_for_input_lists(self, input_list_id: int) -> List[IAM.Request]:
        url = f"{self.host}/v1/inputs/requests?inputListId={input_list_id}"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAM.Request.from_json(js) for js in json_resp]

    def get_input_lists_for_inputs(self, internal_ids: List[str]) -> Dict[str, IAM.InputList]:
        url = f"{self.host}/v1/inputs/input-lists"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        dict_resp = dict()
        for k, v in json_resp.items():
            dict_resp[k] = IAM.InputList.from_json(v)
        return dict_resp

    def get_input_status(self, internal_ids: List[str]) -> Dict[str, Dict[int, bool]]:
        """
        Returns a nested dictionary, the outmost key is the internal_id, which points to a
        dictionary whose keys are the request_ids for the requests where the input is included
        (via the inputList). The key is a boolean denoting if the input is ready for export (true)
        or not (false).
        """
        url = f"{self.host}/v1/inputs/export-status"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        for k, v in json_resp.items():
            inner_dict_resp = dict()
            for kk, vv in v.items():
                inner_dict_resp[int(kk)] = vv
            json_resp[k] = inner_dict_resp

        return json_resp

    def download_annotations(self, internal_ids: List[str], request_id=None
                             ) -> Dict[str, Union[Dict[int, IAM.ExportAnnotation], IAM.ExportAnnotation]]:
        base_url = f"{self.host}/v1/inputs/export"
        if request_id:
            url = base_url + f"?requestId={request_id}"
        else:
            url = base_url
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()

        if base_url == url:
            for k, v in json_resp.items():
                inner_dict_resp = dict()
                for kk, vv in v.items():
                    inner_dict_resp[int(kk)] = IAM.ExportAnnotation.from_json(vv)
                json_resp[k] = inner_dict_resp
            return json_resp

        else:
            for k, v in json_resp.items():
                json_resp[k] = IAM.ExportAnnotation.from_json(v)
            return json_resp

    def get_view_links(self, internal_ids: List[str]) -> Dict[str, str]:
        base_url = f"{self.host}/v1/inputs/view-links"
        js = internal_ids
        resp = self.session.get(base_url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return json_resp

    def get_input_jobs_status(self, internal_ids: List[str] = None,
                              external_ids: List[str] = None) -> List[IAM.InputJob]:
        if internal_ids is None:
            internal_ids = []
        if external_ids is None:
            external_ids = []

        base_url = f"{self.host}/v1/inputs/job-status"
        js = dict(
            internalIds=internal_ids,
            externalIds=external_ids
        )
        resp = self.session.post(base_url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()

        return [IAM.InputJob.from_json(js) for js in json_resp]

    def get_requests_for_project_id(self, project_id: int) -> List[IAM.Request]:
        base_url = f"{self.host}/v1/inputs/requests?projectId={project_id}"
        resp = self.session.get(base_url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAM.Request.from_json(js) for js in json_resp]

    def get_datas_for_inputs_by_internal_ids(self, internal_ids: List[str]) -> Mapping[IAM.Input, List[IAM.Data]]:
        base_url = f"{self.host}/v1/inputs/datas-internal-id"
        js = internal_ids
        resp = self.session.get(base_url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()

        new_dict = {}
        for (k, v) in json_resp:
            new_key = IAM.Input.from_json(k)
            new_values = [IAM.Data.from_json(vv) for vv in v]
            new_dict[new_key] = new_values

        return new_dict

    def get_datas_for_inputs_by_external_ids(self, external_ids: List[str]) -> Mapping[IAM.Input, List[IAM.Data]]:
        base_url = f"{self.host}/v1/inputs/datas-external-id"
        js = external_ids
        resp = self.session.get(base_url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()

        new_dict = {}
        for (k, v) in json_resp:
            new_key = IAM.Input.from_json(k)
            new_values = [IAM.Data.from_json(vv) for vv in v]
            new_dict[new_key] = new_values

        return new_dict
