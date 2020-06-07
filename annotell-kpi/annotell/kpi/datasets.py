import requests
import json

from annotell.kpi.logging import get_logger
from annotell.auth.authsession import AuthSession

log = get_logger()

headers = {'Content-Type': 'application/json'}


class DatasetManager:
    def __init__(self, auth_session: AuthSession, job_id: str, kpi_host: str, kpi_manager_version: str):
        self.auth_session = auth_session
        self.host = kpi_host
        self.job_id = job_id
        self.kpi_manager_version = kpi_manager_version

    def update_metadata(self, project_id: int, dataset_id: int, key: str, value: dict):
        """Update metadata attached to a specific dataset
        """
        dataset = self.get_dataset(project_id, dataset_id)
        dataset['dataset']['metadata'][key] = value
        try:
            return self.auth_session.post(
                url=self.host + self.kpi_manager_version + "/dataset/update",
                data=json.dumps(dataset['dataset']),
                headers=headers
            )
        except requests.exceptions.ConnectionError:
            log.error(f"Cannot submit event, the server={self.host} probably did not respond")
            return "cannot submit event"

    def get_dataset(self, project_id, dataset_id):
        try:
            response = self.auth_session.get(
                url=self.host + self.kpi_manager_version \
                    + f"/dataset?project_id={project_id}&dataset_id={dataset_id}",
                headers=headers
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            log.error(f"Failed to get existing dataset info, the server={self.host} probably did not respond")
            return None
