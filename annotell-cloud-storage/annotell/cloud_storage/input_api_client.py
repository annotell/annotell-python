import requests
import logging
from typing import List, Mapping, Optional
from pathlib import Path
import mimetypes
from . import __version__
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST

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
            "User-Agent": f"annotell-cloud-storage:{__version__}"
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

    def get_upload_urls(self, files: List[str]):
        """Get upload urls to cloud storage"""
        url = f"{self.host}/v1/inputs/upload-urls"
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
                headers = {"Content-Type": content_type}
                resp = self.session.put(upload_url, data=f, headers=headers)
                try:
                    resp.raise_for_status()
                except requests.HTTPError as e:
                    log.error(f"Got {resp.status_code} error calling cloud bucket upload, "
                              f"got response\n{resp.content}")

    def create_inputs(self, files: List[str], job_id: str):
        """Create inputs from uploaded files"""
        log.info(f"Creating inputs for files with job_id={job_id}")
        url = f"{self.host}/v1/inputs"
        js = dict(files=files, jobId=job_id)
        resp = self.session.post(url, json=js, headers=self.headers)
        self._raise_on_error(resp)

    def create_inputs_for_files(self, folder: Path, files: List[str]):
        """Upload files in folder to an input"""
        resp = self.get_upload_urls(files)
        items = resp['items']
        job_id = resp['jobId']
        files = list(items.keys())
        self.upload_files(folder, items)
        self.create_inputs(files, job_id)
        return job_id
