from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.model.enums import InputBatchStatus
from annotell.input_api.util import ts_to_dt


class InputBatch(Response):
    def __init__(self, id: int, project_id: int, external_id: str, title: str, status: InputBatchStatus,  created: datetime, updated: datetime):
        self.id = id
        self.project_id = project_id
        self.external_id = external_id
        self.title = title
        self.status = status
        self.created = created
        self.updated = updated

    @staticmethod
    def from_json(js: dict):
        return InputBatch(int(js["id"]), int(js["projectId"]), js["externalId"], js["title"], js["status"],
                          ts_to_dt(js["created"]), ts_to_dt(js["created"]))

    def __repr__(self):
        return f"<InputBatch(" + \
            f"id={self.id}, " + \
            f"project_id={self.project_id}, " + \
            f"external_id={self.external_id}, " + \
            f"title={self.title}, " + \
            f"status={self.status}, " + \
            f"created={self.created}, " + \
            f"updated={self.updated})>"
