from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from annotell.input_api.util import ts_to_dt


@dataclass
class Project:
    id: int
    created: datetime
    title: str
    description: str
    deadline: Optional[str]
    status: str
    external_id: str

    @ staticmethod
    def from_json(js: dict):
        return Project(int(js["id"]), ts_to_dt(js["created"]), js["title"],
                       js["description"], js.get("deadline"), js["status"], js["externalId"])
