import requests
import logging
from typing import List, Mapping, Optional
from pathlib import Path
import mimetypes
<<<<<<< HEAD
from PIL import Image
# from . import __version__
=======
from . import __version__
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST
>>>>>>> d5068cdca616cfadacafd6127d56fe9a96ea6907

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
            log.error(f"Got {resp.status_code} error calling url={resp.url}, got response:\n{resp.content}")
            raise
        return resp

    def get_upload_urls(self, files: Mapping[str, List[str]]):
        """Get upload urls to cloud storage"""
<<<<<<< HEAD
        url = f"{self.base_url}/v1/inputs/upload-urls"
        #js = dict(files=files)
        resp = self.session.get(url, json=files, headers=self.headers)
=======
        url = f"{self.host}/v1/inputs/upload-urls"
        js = dict(files=files)
        resp = self.session.get(url, json=js, headers=self.headers)
>>>>>>> d5068cdca616cfadacafd6127d56fe9a96ea6907
        return self._raise_on_error(resp).json()

    def upload_files(self, folder: Path, url_map: Mapping[str, str]):
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

<<<<<<< HEAD
    def create_inputs(self, image_files: Mapping[str, Mapping[str, str]],
                      pointcloud_files: List[str], job_id: str, input_list_id: int,
                      metadata: dict):
        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.base_url}/v1/inputs"
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
=======
    def create_inputs(self, files: List[str], job_id: str):
        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.host}/v1/inputs"
        js = dict(files=files, jobId=job_id)
>>>>>>> d5068cdca616cfadacafd6127d56fe9a96ea6907
        resp = self.session.post(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def create_inputs_for_files(self, folder: Path, files: Mapping[str, List[str]],
                                input_list_id: int, metadata: dict):
        """Upload files in folder to an input"""
        resp = self.get_upload_urls(files)

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
        #files = list(items.keys())
        self.upload_files(folder, items)
<<<<<<< HEAD
        resp = self.create_inputs(
            images_with_settings, pointcloud_files, job_id, input_list_id, metadata
        )
        return resp

    def mend_input_data(self):
        url = f"{self.base_url}/v1/inputs/mend-input-metadata"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def invalidate_input(self):
        url = f"{self.base_url}/v1/inputs/invalidate"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def list_projects(self):
        url = f"{self.base_url}/v1/inputs/projects"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def list_input_lists(self, project_id: int):
        url = f"{self.base_url}/v1/inputs/input-lists?projectId={project_id}"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def get_calibration_data(self, id: Optional[int] = None, external_id: Optional[str] = None):
        url = f"{self.base_url}/v1/inputs/calibration-data"
        if id:
            url += f"?id={id}"
        elif external_id:
            url += f"?externalId={external_id}"

        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def create_calibration_data(self, calibration: dict, external_id: str):
        url = f"{self.base_url}/v1/inputs/calibration-data"
        js = dict(
            externalId=external_id,
            calibration=calibration
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def get_requests_for_request_ids(self, request_ids: List[int]):
        url = f"{self.base_url}/v1/inputs/requests"
        js = request_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def get_requests_for_input_lists(self, input_list_id: int):
        url = f"{self.base_url}/v1/inputs/requests?inputListId={input_list_id}"
        resp = self.session.get(url, headers=self.headers)
        return self._raise_on_error(resp).json()

    def get_input_lists_for_inputs(self, internal_ids: List[str]):
        url = f"{self.base_url}/v1/inputs/input-lists"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def get_input_status(self, internal_ids: List[str]):
        url = f"{self.base_url}/v1/inputs/export-status"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def download_annotations(self, internal_ids: List[str], request_id=None):
        url = f"{self.base_url}/v1/inputs/export"
        if request_id:
            url += f"?requestId={request_id}"
        js = internal_ids
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()
=======
        self.create_inputs(files, job_id)
        return job_id
>>>>>>> d5068cdca616cfadacafd6127d56fe9a96ea6907
