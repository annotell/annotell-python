import os

import requests
import logging
from typing import List, Mapping, Optional
from pathlib import Path
import mimetypes
# from . import __version__

BASE_URL = "https://input.annotell.com"

log = logging.getLogger(__name__)

class InputApiClient:
    """Creates Annotell inputs from local files"""

    def __init__(self, base_url, api_token=None):
        self.api_token = api_token or os.getenv("ANNOTELL_API_TOKEN")
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": f"annotell-cloud-storage:0.2.0"  # FIXME {__version__}
        }

    def _raise_on_error(self, resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(f"Got {resp.status_code} error calling url={resp.url}, got response:\n{resp.content}")
            raise
        return resp

    def get_upload_urls(self, files: List[str]):
        """Get upload urls to cloud storage"""
        url = f"{self.base_url}/v1/inputs/upload-urls"
        js = dict(files=files)
        resp = self.session.get(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def upload_files(self, folder: Path, url_map: Mapping[str, str]):
        """Upload all files to cloud storage"""
        for (file, upload_url) in url_map.items():
            fi = folder.joinpath(file)
            log.info(f"Uploading file={fi}")
            with fi.open('rb') as f:
                content_type = mimetypes.guess_type(file)[0]
                # Hack deluxe
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

    def create_inputs(self, files: List[str], job_id: str, input_list_id: int, metadata: dict):
        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.base_url}/v1/inputs"
        js = dict(
            files=files,
            internalId=job_id,
            inputListId=input_list_id,
            metadata=metadata
        )
        resp = self.session.post(url, json=js, headers=self.headers)
        return self._raise_on_error(resp).json()

    def create_inputs_for_files(self, folder: Path, files: List[str], input_list_id: int, metadata: dict):
        """Upload files in folder to an input"""
        resp = self.get_upload_urls(files)
        items = resp['items']
        job_id = resp['jobId']
        files = list(items.keys())
        self.upload_files(folder, items)
        resp = self.create_inputs(files, job_id, input_list_id, metadata)
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
