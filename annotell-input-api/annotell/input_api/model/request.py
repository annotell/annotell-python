from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


class Request(Response):
    def __init__(self, id: int, created: datetime, project_id: int, title: str, description: str,
                 input_list_id: int, input_batch_id: int, external_id: str):
        self.id = id
        self.created = created
        self.project_id = project_id
        self.title = title
        self.description = description
        self.input_list_id = input_list_id
        self.input_batch_id = input_batch_id
        self.external_id = external_id

    @staticmethod
    def from_json(js: dict):
        return Request(int(js["id"]), ts_to_dt(js["created"]), int(js["projectId"]),
                       js["title"], js["description"], int(js["inputListId"]), int(js["inputBatchId"]), js["externalId"])

    def __repr__(self):
        return f"<Request(" + \
            f"id={self.id}, " + \
            f"created={self.created}, " + \
            f"project_id={self.project_id}, " + \
            f"title={self.title}, " + \
            f"description={self.description}, " + \
            f"input_list_id={self.input_list_id}, " + \
            f"input_batch_id={self.input_batch_id}, " + \
            f"external_id={self.external_id})>"
