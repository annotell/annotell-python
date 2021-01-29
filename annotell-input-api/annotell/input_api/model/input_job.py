from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime
from annotell.input_api.util import ts_to_dt


@dataclass
class InputJob:
    internal_id: str
    external_id: str
    filename: str
    status: str
    added: datetime
    error_message: Optional[str]

    @staticmethod
    def from_json(js: dict):
        return InputJob(js["jobId"], js["externalId"], js["filename"],
                        js["status"], ts_to_dt(js["added"]), js.get("errorMessage"))


@dataclass
class CreateInputJobResponse:
    internal_id: int
    files: Dict[str, str]

    @staticmethod
    def from_json(js: dict):
        return CreateInputJobResponse(js["internalId"], js["files"])
