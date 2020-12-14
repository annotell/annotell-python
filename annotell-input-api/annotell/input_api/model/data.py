from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from annotell.input_api.util import ts_to_dt


@dataclass
class Data:
    id: int
    external_id: str
    source: Optional[str]
    created: datetime

    @staticmethod
    def from_json(js: dict):
        return Data(
            int(js["id"]),
            js.get("externalId"),
            js.get("source"),
            ts_to_dt(js["created"])
        )
