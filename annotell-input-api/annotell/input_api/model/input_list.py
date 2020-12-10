from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt

class InputList(Response):
    def __init__(self, id: int, project_id: int, name: str, created: datetime):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.created = created

    @staticmethod
    def from_json(js: dict):
        return InputList(int(js["id"]), int(js["projectId"]), js["name"],
                         ts_to_dt(js["created"]))

    def __repr__(self):
        return f"<InputList(" + \
            f"id={self.id}, " + \
            f"project_id={self.project_id}, " + \
            f"name={self.name}, " + \
            f"created={self.created})>"
