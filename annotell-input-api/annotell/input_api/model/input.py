from typing import Optional
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.model.enums import InvalidatedReasonInput


class Input(Response):
    def __init__(self, internal_id: Optional[str], external_id: Optional[str], input_type: str, invalidated: Optional[str], invalidated_reason: Optional[InvalidatedReasonInput]):
        self.internal_id = internal_id
        self.external_id = external_id
        self.input_type = input_type
        self.invalidated = invalidated
        self.invalidated_reason = invalidated_reason

    @staticmethod
    def from_json(js: dict):
        return Input(
            js.get("internalId"),
            js.get("externalId"),
            js["inputType"],
            js["invalidated"],
            js["invalidatedReason"]
        )

    def __repr__(self):
        return f"<Input(" + \
            f"internal_id={self.internal_id}, " + \
            f"external_id={self.external_id}, " + \
            f"external_id={self.input_type}, " + \
            f"external_id={self.invalidated}, " + \
            f"input_type={self.invalidated_reason})>"
