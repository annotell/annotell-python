from typing import Dict
from dataclasses import dataclass
from annotell.input_api.model.abstract.abstract_models import Response


@dataclass
class UploadUrlsResponse:
    files_to_url: Dict[str, str]
    internal_id: int

    @staticmethod
    def from_json(js: dict):
        return UploadUrlsResponse(
            # property names does not match.
            files_to_url=js["files"],
            internal_id=js["jobId"]
        )
