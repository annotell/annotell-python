import json
from datetime import datetime


class Result:
    def __init__(self,
                 kpi_id,
                 content,
                 project_id=None,
                 dataset_id=None,
                 job_id=None,
                 created=None,
                 script_hash=None,
                 filter_id=None,
                 result_type="undefined",
                 execution_mode=None):
        self.content = content
        self.job_id = job_id
        self.created = created
        self.kpi_id = kpi_id
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.result_type = result_type
        self.script_hash = script_hash
        self.filter_id = filter_id
        self.execution_mode = execution_mode
        if not created:
            self.created = str(datetime.now())
        else:
            self.created = created

    def set_kpi_id(self, kpi_id):
        self.kpi_id = kpi_id

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_dataset_id(self, dataset_id):
        self.dataset_id = dataset_id

    def set_execution_mode(self, execution_mode):
        self.execution_mode = execution_mode

    def set_job_id(self, job_id):
        self.job_id = job_id

    def set_script_hash(self, script_hash):
        self.script_hash = script_hash

    def set_filter_id(self, filter_id):
        self.filter_id = filter_id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
