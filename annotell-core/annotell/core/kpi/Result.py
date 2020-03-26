import json
from datetime import datetime

class Result:
    def __init__(self, content, result_type, kpi_id=None, session_id=None, created=None, script_hash=None):
        self.content = content
        self.session_id = session_id
        self.created = created
        self.kpi_id = kpi_id
        self.result_type = result_type
        self.script_hash = script_hash
        if not created:
            self.created = str(datetime.now())
        else:
            self.created = created

    def set_kpi_id(self, kpi_id):
        self.kpi_id = kpi_id

    def set_session_id(self, session_id):
        self.session_id = session_id

    def set_script_hash(self, script_hash):
        self.script_hash = script_hash

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
