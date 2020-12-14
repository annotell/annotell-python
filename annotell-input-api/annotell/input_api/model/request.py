from dataclasses import dataclass
from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


@dataclass
class Request(Response):
    id: int
    created: datetime
    project_id: int
    title: str
    description: str
    input_list_id: int
    input_batch_id: int
    external_id: str

    @staticmethod
    def from_json(js: dict):
        return Request(int(js["id"]), ts_to_dt(js["created"]), int(js["projectId"]),
                       js["title"], js["description"], int(js["inputListId"]), int(js["inputBatchId"]), js["externalId"])
