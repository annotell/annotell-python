from annotell.core.kpi import util
from datetime import datetime
import time
import json

import annotell.core.kpi.Result as Result


def _human_readable(posix_time):
    return datetime.utcfromtimestamp(posix_time).strftime('%Y-%m-%dT%H:%M:%SZ')


class KPI:
    def __init__(self, kpi_id):

        if not util.valid_kpi_type(kpi_type):
            raise ValueError('Invalid KPI type')
        self.kpi_type = kpi_type

        if not isinstance(kpi_id, int):
            raise ValueError('Invalid KPI ID, needs to be an integer')
        self.kpi_id = kpi_id

        self.tags = tags
        self.tags = groups
        self.created = str(datetime.now())
        self.results = []

    def add_result(self, result: Result):
        result.set_kpi_id(self.kpi_id)
        self.results.append(result)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
