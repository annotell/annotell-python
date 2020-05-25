import requests
import datetime
import json

from annotell.kpi.logging import get_logger
from annotell.auth.authsession import AuthSession

log = get_logger()


class EventManager:
    def __init__(self, auth_session: AuthSession, job_id: str, host, kpi_manager_version):
        self.auth_session = auth_session
        self.host = host
        self.job_id = job_id
        self.kpi_manager_version = kpi_manager_version

    EVENT_SCRIPT_INITIALIZED = 'script_initialized'
    EVENT_SCRIPT_COMPLETED = 'script_completed'
    EVENT_DATA_LOADED = 'data_loaded'
    EVENT_DATA_LOADING_FAILED = 'data_loading_failed'
    EVENT_DATA_FILTERED = 'data_filtered'
    EVENT_RESULT_SUBMIT_FAILED = 'result_submit_failed'
    EVENT_RESULT_SUBMIT_SUCCEEDED = 'result_submit_succeeded'

    def submit(self, event_type: str, context: str):
        """Sends events while script is running to help with debugging and progress tracking.

        Args:
            event_type:     Event types are used for grouping events.
            context:        String that provides information about event context.
        """
        event = {
            "job_id": self.job_id,
            "event_type": event_type,
            "context": context,
            "created": str(datetime.datetime.now())
        }
        event_type_padded = "{:<20}".format(event_type)
        log.info(f"[{event_type_padded}] {context}")

        headers = {'Content-Type': 'application/json'}
        try:
            return self.auth_session.post(
                url=self.host + self.kpi_manager_version + "/event/create",
                data=json.dumps(event),
                headers=headers
            )
        except requests.exceptions.ConnectionError:
            log.error(f"Cannot submit event, the server={self.host} probably did not respond")
            return None

    def script_initialized(self, organization_id: int, project_id: int, dataset_id: int, user_id: int):
        self.submit(event_type=self.EVENT_SCRIPT_INITIALIZED,
                    context=f"org_id={organization_id} user_id={user_id} project_id={project_id} dataset_id={dataset_id}")

    def script_completed(self):
        self.submit(event_type=self.EVENT_SCRIPT_COMPLETED,
                    context="You deserve some coffee now! ☕️")
