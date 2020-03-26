import requests
import os
import logging
from typing import List, Mapping, Optional, Union, Dict
from pathlib import Path
import mimetypes
from PIL import Image
# from . import __version__
# from . import __version__
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST
import input_api_model as IAP

DEFAULT_HOST = "https://input.annotell.com"

log = logging.getLogger(__name__)


class InputApiClient:
    """Creates Annotell inputs from local files"""

    def __init__(self, *,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 api_token: Optional[str] = None,
                 host: str = DEFAULT_HOST,
                 auth_host: str = DEFAULT_AUTH_HOST):
        """
        :param client_id: client id for authentication
        :param client_secret: client secret for authentication
        :param api_token: legacy api token for authentication.
        :param host: override for input api url
        :param auth_host: override for authentication url
        """

        self.host = host

        self.oauth_session = AuthSession(host=auth_host,
                                         api_token=api_token,
                                         client_id=client_id,
                                         client_secret=client_secret)

        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": f"annotell-cloud-storage:0.2.0"  # FIXME {__version__}
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
                                               pointcloud_files: List[str], job_id: str, input_list_id: int,
                                               metadata: dict):
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
            metadata=metadata
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAP.CreateInputResponse.from_json(json_resp)

    def create_inputs_point_cloud_with_images(self, folder: Path, files: Mapping[str, List[str]],
                                              input_list_id: int,
                                              metadata: dict) -> IAP.CreateInputResponse:
        """Upload files in folder to an input"""
        resp = self._get_upload_urls(files)

        images_with_settings = dict()
        for image in files['images']:
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

    def mend_input_data(self):
        url = f"{self.host}/v1/inputs/mend-input-metadata"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def invalidate_input(self):
        url = f"{self.host}/v1/inputs/invalidate"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def list_projects(self) -> List[IAP.Project]:
        url = f"{self.host}/v1/inputs/projects"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAP.Project.from_json(js) for js in json_resp]

    def list_input_lists(self, project_id: int) -> List[IAP.InputList]:
        url = f"{self.host}/v1/inputs/input-lists?projectId={project_id}"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAP.InputList.from_json(js) for js in json_resp]

    def get_calibration_data(self, id: Optional[int] = None, external_id: Optional[str] = None
                             ) -> Union[List[IAP.CalibrationNoContent], List[IAP.CalibrationWithContent]]:
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
            return [IAP.CalibrationNoContent.from_json(js) for js in json_resp]
        else:
            return [IAP.CalibrationWithContent.from_json(js) for js in json_resp]

    def create_calibration_data(self, calibration: dict, external_id: str
                                ) -> IAP.CalibrationNoContent:
        url = f"{self.host}/v1/inputs/calibration-data"
        js = dict(
            externalId=external_id,
            calibration=calibration
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return IAP.CalibrationNoContent.from_json(json_resp)

    def get_requests_for_request_ids(self, request_ids: List[int]) -> Dict[int, IAP.Request]:
        url = f"{self.host}/v1/inputs/requests"
        js = request_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        dict_resp = dict()
        for k, v in json_resp.items():
            dict_resp[int(k)] = IAP.Request.from_json(v)
        return dict_resp

    def get_requests_for_input_lists(self, input_list_id: int) -> List[IAP.Request]:
        url = f"{self.host}/v1/inputs/requests?inputListId={input_list_id}"
        resp = self.session.get(url, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        return [IAP.Request.from_json(js) for js in json_resp]

    def get_input_lists_for_inputs(self, internal_ids: List[str]) -> Dict[str, IAP.InputList]:
        url = f"{self.host}/v1/inputs/input-lists"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        json_resp = self._raise_on_error(resp).json()
        dict_resp = dict()
        for k, v in json_resp.items():
            dict_resp[k] = IAP.InputList.from_json(v)
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
                             ) -> Dict[str, Union[Dict[int, IAP.ExportAnnotation], IAP.ExportAnnotation]]:
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
                    inner_dict_resp[int(kk)] = IAP.ExportAnnotation.from_json(vv)
                json_resp[k] = inner_dict_resp
            return json_resp

        else:
            for k, v in json_resp.items():
                json_resp[k] = IAP.ExportAnnotation.from_json(v)
            return json_resp
