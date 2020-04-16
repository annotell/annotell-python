"""Client for communicating with the Annotell platform."""
import requests
import os
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
                 auth_host: str = DEFAULT_AUTH_HOST):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        """

        self.host = host

        self.oauth_session = AuthSession(host=auth_host, auth=auth)

        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": f"annotell-cloud-storage:{__version__}"
        }

    @property
    def session(self):
        return self.oauth_session.session

    def _raise_on_error(self, resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(
                f"Got {resp.status_code} error calling url={resp.url}, got response:\n{resp.content}")
            raise
        return resp

    def _get_upload_urls(self, files: Mapping[str, List[str]]):
        """Get upload urls to cloud storage"""
        url = f"{self.host}/v1/inputs/upload-urls"
        #js = dict(files=files)
        resp = self.session.get(url, json=files, headers=self.headers)
        return self._raise_on_error(resp).json()

    def _upload_files(self, folder: Path, url_map: Mapping[str, str]):
        """Upload all files to cloud storage"""
        for (file, upload_url) in url_map.items():
            fi = folder.joinpath(file)
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

    def _create_inputs_point_cloud_with_images(self, image_files: Mapping[str, Mapping[str, str]],
                                               pointcloud_files: List[str], job_id: str,
                                               input_list_id: int, metadata: IAM.Metadata):
        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.host}/v1/inputs"
        files_js = dict(
            imagesWithSettings=image_files,
            pointclouds=pointcloud_files
        )
        js = dict(
            files=files_js,
            internalId=job_id,
            inputListId=input_list_id,
            metadata=metadata.to_dict()
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAM.CreateInputResponse.from_json(json_resp)

    def create_inputs_point_cloud_with_images(self, folder: Path,
                                              files: IAM.FilesPointCloudWithImages,
                                              input_list_id: int,
                                              metadata: IAM.Metadata) -> IAM.CreateInputResponse:
        """
        Upload files and create an input of type 'point_cloud_with_image'.

        :param folder: path to folder containing files
        :param files: class containing images and pointclouds that constitute the input
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
        resp = self._get_upload_urls(files.to_dict())

        images_with_settings = dict()
        for image in files.images:
            with Image.open(os.path.join(folder, image)) as im:
                width, height = im.size
            images_with_settings[image] = dict(
                width=width,
                height=height
            )

        images_on_disk = list(images_with_settings.keys())
        images_in_response = list(resp['images'].keys())
        assert set(images_on_disk) == set(images_in_response)
        pointcloud_files = list(resp['pointclouds'].keys())
        job_id = resp['jobId']

        items = {**resp['images'], **resp['pointclouds']}
        self._upload_files(folder, items)
        create_input_response = self._create_inputs_point_cloud_with_images(
            images_with_settings, pointcloud_files, job_id, input_list_id, metadata
        )
        return create_input_response

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

    def invalidate_input(self):
        """Not yet implemented."""
        url = f"{self.host}/v1/inputs/invalidate"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

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

    def create_calibration_data(self, calibration: dict, external_id: str
                                ) -> IAM.CalibrationNoContent:
        url = f"{self.host}/v1/inputs/calibration-data"
        js = dict(
            externalId=external_id,
            calibration=calibration
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

    def get_input_jobs_status(self, internal_ids: List[str] = [],
                              external_ids: List[str] = []) -> List[IAM.InputJob]:
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
