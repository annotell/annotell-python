import requests

from annotell.kpi.models import Result
from annotell.kpi.events import EventManager
from annotell.kpi.logging import get_logger
from annotell.auth.authsession import AuthSession

from typing import List

log = get_logger()


class ResultManager:
    def __init__(self,
                 auth_session: AuthSession,
                 host: str,
                 kpi_manager_version: str,
                 execution_mode: str,
                 script_hash: str,
                 job_id: str,
                 project_id: str,
                 dataset_id: str,
                 filter_id: str,
                 event_manager: EventManager):

        self.session = auth_session
        self.host = host
        self.kpi_manager_version = kpi_manager_version
        self.script_hash = script_hash
        self.job_id = job_id
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.filter_id = filter_id
        self.execution_mode = execution_mode
        self.event_manager = event_manager

    def submit_result(self, result: Result):
        """ Submit a result of a KPI calculation to the KPI Manager

        Will send the json representation of the KPI result to the KPI Manager for storage.
        """
        result.set_job_id(job_id=self.job_id)
        result.set_project_id(project_id=self.project_id)
        result.set_dataset_id(dataset_id=self.dataset_id)
        result.set_script_hash(script_hash=self.script_hash)
        result.set_filter_id(filter_id=self.filter_id)
        result.set_execution_mode(execution_mode=self.execution_mode)
        headers = {'Content-Type': 'application/json'}

        try:
            response_json = self.session.post(url=self.host + self.kpi_manager_version + "/result/create",
                                              data=result.toJSON(),
                                              headers=headers)
        except requests.exceptions.ConnectionError:
            log.error(f"Cannot submit result, the server={self.host} probably did not respond")
            self.event_manager.submit(event_type=self.event_manager.EVENT_RESULT_SUBMIT_FAILED,
                                      context=f'the server={self.host} probably did not respond')
            return None

        if response_json.status_code in [200, 201]:
            self.event_manager.submit(event_type=self.event_manager.EVENT_RESULT_SUBMIT_SUCCEEDED,
                                      context=f'api_status_code={response_json.status_code}')
        else:
            self.event_manager.submit(event_type=self.event_manager.EVENT_RESULT_SUBMIT_FAILED,
                                      context=f'api_status_code={response_json.status_code}')

    def submit_results(self, results: List[Result]):
        """ Submit a list of results from KPI calculations to the KPI Manager

        Will send the json representation of the KPI results to the KPI Manager for storage.
        """
        for result in results:
            self.submit_result(result)
