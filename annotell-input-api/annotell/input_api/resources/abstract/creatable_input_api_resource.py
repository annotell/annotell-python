from typing import Optional

from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.model import (CreateInputJobResponse, FilesToUpload,
                                      UploadUrlsResponse)


class CreateableInputAPIResource(FileResourceClient):

    def __init__(self, client: HttpClient, file_resource_client: FileResourceClient):
        self.client = client
        self.file_resource_client = file_resource_client

    def post_input_request(self, resource_path: str,
                           input_request: dict,
                           project: Optional[str],
                           batch: Optional[str],
                           input_list_id: Optional[int],
                           dryrun: bool = False) -> Optional[CreateInputJobResponse]:
        """
        Send input to Input API. if not dryrun is true, only validation is performed
        Otherwise, returns `CreateInputJobResponse`
        """
        if input_list_id is not None:
            input_request['inputListId'] = input_list_id

        request_url = self._resolve_request_url(resource_path, project, batch)
        json_resp = self.client.post(request_url, json=input_request)
        if not dryrun:
            return CreateInputJobResponse.from_json(json_resp)

    @staticmethod
    def _resolve_request_url(resource_path: str,
                             project: Optional[str] = None,
                             batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = f"v1/inputs/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path

        return url

    def get_upload_urls(self, files_to_upload: FilesToUpload):
        """Get upload urls to cloud storage"""
        json_resp = self.client.get("v1/inputs/upload-urls", json=files_to_upload.to_dict())
        return UploadUrlsResponse.from_json(json_resp)
