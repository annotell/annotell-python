import time
import json


class ReportDescription:
    def __init__(self, author, project):
        self.author = author
        self.project = project
        self.created = int(time.time())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Report:
    def __init__(self, report_description, kpi_results):
        self.reportDescription = report_description
        self.kpiResults = kpi_results

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
