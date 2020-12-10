"""Client for communicating with the Annotell platform."""
import logging
import random
import time
from pathlib import Path
from typing import Mapping, Dict, BinaryIO, Optional

import requests

from annotell.input_api.util import get_content_type

log = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = [408, 429, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 598, 599]


class FileResourceClient:

    def __init__(self,
                 max_upload_retry_attempts: int = 23,
                 max_upload_retry_wait_time: int = 60):
        """
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """
        self.MAX_NUM_UPLOAD_RETRIES = max_upload_retry_attempts
        self.MAX_RETRY_WAIT_TIME = max_upload_retry_wait_time  # seconds

    def _get_wait_time(self, upload_attempt: int) -> int:
        """
        Calculates the wait time before attempting another file upload to GCS

        :param upload_attempt: How many attempts to upload that have been made
        :return: int: The time to wait before retrying upload
        """
        max_wait_time = pow(2, upload_attempt - 1)
        wait_time = random.random() * max_wait_time
        wait_time = wait_time if wait_time < self.MAX_RETRY_WAIT_TIME else self.MAX_RETRY_WAIT_TIME
        return wait_time

    #  Using similar retry strategy as gsutil
    #  https://cloud.google.com/storage/docs/gsutil/addlhelp/RetryHandlingStrategy
    def _upload_file(self, upload_url: str, file: BinaryIO, headers: Dict[str, str], upload_attempt: int = 1) -> None:
        """
        Upload the file to GCS, retries if the upload fails with some specific status codes.
        """
        log.info(f"Uploading file={file.name}")
        resp = requests.put(upload_url, data=file, headers=headers)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(f"On upload attempt ({upload_attempt}/{self.MAX_NUM_UPLOAD_RETRIES}) to GCS "
                      f"got response:\n{resp.status_code}: {resp.content}")

            if upload_attempt < self.MAX_NUM_UPLOAD_RETRIES and resp.status_code in RETRYABLE_STATUS_CODES:
                wait_time = self._get_wait_time(upload_attempt)
                log.info(f"Waiting {int(wait_time)} seconds before retrying")
                time.sleep(wait_time)
                self._upload_file(upload_url, file, headers, upload_attempt + 1)
            else:
                raise e

        except Exception as e:
            raise e

    def upload_files(self, url_map: Mapping[str, str], folder: Optional[Path] = None) -> None:
        """
        Upload all files to cloud storage

        :param url_map: map between filename and GCS signed URL
        :param folder: Optional base path, will join folder and each filename in map if provided
        """
        for (filename, upload_url) in url_map.items():
            file_path = folder.joinpath(filename).expanduser() if folder else Path(filename).expanduser()
            with file_path.open('rb') as file:
                content_type = get_content_type(filename)
                headers = {"Content-Type": content_type}
                self._upload_file(upload_url, file, headers)
