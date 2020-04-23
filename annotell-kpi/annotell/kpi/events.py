import requests
import datetime
import json

from annotell.kpi.logging import get_logger
from annotell.auth.authsession import AuthSession

log = get_logger()


class EventManager:
    def __init__(self, auth_session: AuthSession, session_id, host, kpi_manager_version):
        self.auth_session = auth_session
        self.host = host
        self.session_id = session_id
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
            "session_id": self.session_id,
            "event_type": event_type,
            "context": context,
            "created": str(datetime.datetime.now())
        }
        log.info(f"event_type={event_type} context={context}")

        headers = {'Content-Type': 'application/json'}
        try:
            return self.auth_session.post(
                url=self.host + self.kpi_manager_version + "/event",
                data=json.dumps(event),
                headers=headers
            )
        except requests.exceptions.ConnectionError:
            log.error(f"Cannot submit event, the server={self.host} probably did not respond")
            return None

    def script_initialized(self, app_name: str):
        self.submit(event_type=self.EVENT_SCRIPT_INITIALIZED,
                    context=f"app_name={app_name} with host={self.host}")

    def script_completed(self):
        self.submit(event_type=self.EVENT_SCRIPT_COMPLETED,
                    context="You deserve some coffee now! ☕️")
