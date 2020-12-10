from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.http_client import HttpClient


class InputAPIResource(FileResourceClient):

    def __init__(self, client: HttpClient):
        self.client = client
