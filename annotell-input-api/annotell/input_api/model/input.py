from dataclasses import dataclass
from typing import Optional
from annotell.input_api.model.enums import InvalidatedReasonInput


@dataclass
class Input:
    internal_id: Optional[str]
    external_id: Optional[str]
    input_type: str
    invalidated: Optional[str]
    invalidated_reason: Optional[InvalidatedReasonInput]

    @staticmethod
    def from_json(js: dict):
        return Input(
            js.get("internalId"),
            js.get("externalId"),
            js["inputType"],
            js["invalidated"],
            js["invalidatedReason"]
        )
