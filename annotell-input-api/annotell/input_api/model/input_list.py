from dataclasses import dataclass
from datetime import datetime
from annotell.input_api.util import ts_to_dt


@dataclass
class InputList:
    id: int
    project_id: int
    name: str
    created: datetime

    @staticmethod
    def from_json(js: dict):
        return InputList(int(js["id"]), int(js["projectId"]), js["name"], ts_to_dt(js["created"]))
