from typing import Optional
from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


class Project(Response):
    def __init__(self, id: int, created: datetime, title: str, description: str,
                 deadline: Optional[str], status: str, external_id: str):
        self.id = id
        self.created = created
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status
        self.external_id = external_id

    @staticmethod
    def from_json(js: dict):
        return Project(int(js["id"]), ts_to_dt(js["created"]), js["title"],
                       js["description"], js.get("deadline"), js["status"], js["externalId"])

    def __repr__(self):
        return f"<Project(" + \
            f"id={self.id}, " + \
            f"created={self.created}, " + \
            f"title={self.title}, " + \
            f"description={self.description}, " + \
            f"deadline={self.deadline}, " + \
            f"status={self.status}, " + \
            f"external_id={self.external_id})>"
