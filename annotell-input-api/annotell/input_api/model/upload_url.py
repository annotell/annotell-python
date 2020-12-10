from typing import Dict
from annotell.input_api.model.abstract.abstract_models import Response


class UploadUrlsResponse(Response):
    def __init__(self, files_to_url: Dict[str, str], internal_id: int):
        self.files_to_url = files_to_url
        self.internal_id = internal_id

    @staticmethod
    def from_json(js: dict):
        return UploadUrlsResponse(js["files"], js["jobId"])

    def __repr__(self):
        return f"<UploadUrlsResponse(" + \
               f"files_to_url={self.files_to_url}, " + \
               f"internal_id={self.internal_id})>"
