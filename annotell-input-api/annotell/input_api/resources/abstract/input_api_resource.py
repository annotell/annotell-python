from typing import Optional

from annotell.input_api.http_client import HttpClient
from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.model import CreateInputJobResponse, FilesToUpload, UploadUrlsResponse

class InputAPIResource(FileResourceClient):

    def __init__(self, client: HttpClient):
        self.client = client    