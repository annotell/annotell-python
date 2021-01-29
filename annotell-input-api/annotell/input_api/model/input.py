from dataclasses import dataclass
from typing import Optional
from annotell.input_api.model.enums import InputStatus


@dataclass
class Input:
    internal_id: str
    external_id: str
    batch_id: str
    input_type: str
    status: InputStatus
    error_message: Optional[str]

    @staticmethod
    def from_json(js: dict):
        return Input(
            js["internalId"],
            js["externalId"],
            js["batchId"],
            js["inputType"],
            js["status"],
            js.get("errorMessage")
        )
