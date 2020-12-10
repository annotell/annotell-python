from typing import Optional
from datetime import datetime

from annotell.input_api.model.abstract.abstract_models import Response
from annotell.input_api.util import ts_to_dt


class Data(Response):
    def __init__(self, id: int, external_id: str, source: Optional[str], created: datetime):
        self.id = id
        self.external_id = external_id
        self.source = source
        self.created = created

    @staticmethod
    def from_json(js: dict):
        return Data(
            int(js["id"]),
            js.get("externalId"),
            js.get("source"),
            ts_to_dt(js["created"])
        )

    def __repr__(self):
        return f"<Data(" + \
            f"id={self.id}, " + \
            f"external_id={self.external_id}, " + \
            f"source={self.source}, " + \
            f"created={self.created})>"
