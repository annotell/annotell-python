from typing import Optional
from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


class InputJob(Response):
    def __init__(self, id: int, internal_id: str, external_id: str, filename: str,
                 status: str, added: datetime, error_message: Optional[str]):
        self.id = id
        self.internal_id = internal_id
        self.external_id = external_id
        self.filename = filename
        self.status = status
        self.added = added
        self.error_message = error_message

    @staticmethod
    def from_json(js: dict):
        return InputJob(int(js["id"]), js["jobId"], js["externalId"], js["filename"],
                        bool(js["status"]), ts_to_dt(js["added"]), js.get("errorMessage"))

    def __repr__(self):
        return f"<InputJob(" + \
            f"id={self.id}, " + \
            f"internal_id={self.internal_id}, " + \
            f"external_id={self.external_id}, " + \
            f"filename={self.filename}, " + \
            f"status={self.status}, " + \
            f"added={self.added}, " + \
            f"error_message={self.error_message})>"


class CreateInputJobResponse(Response):
    def __init__(self, internal_id: int):
        self.internal_id = internal_id

    @staticmethod
    def from_json(js: dict):
        return CreateInputJobResponse(js["internalId"])

    def __repr__(self):
        return f"<CreateInputJobResponse(" + \
               f"internal_id={self.internal_id})>"
