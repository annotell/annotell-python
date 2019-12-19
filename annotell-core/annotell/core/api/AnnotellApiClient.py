"""
Annotell api client gathered in one, using object orient
"""
import os

from utilities.AnnotellLogger import AnnotellLogger
from api.UserApi import UserApi
from api.EngineApi import EngineApi
from api.StorageApi import StorageApi
from api.EventApi import EventApi
from api.MetricsApi import MetricsApi

from datamodel import DataModelUsers

logger = AnnotellLogger.get_logger(__name__)

try:
    default_email = os.environ['API_CLIENTS_EMAIL']
    default_password = os.environ['API_CLIENTS_PASSWORD']
except KeyError:
    default_email = None
    default_password = None


class AnnotellApiClient:
    def __init__(self, email=default_email, password=default_password, connect_to_prod=False):
        if connect_to_prod:
            user_url = "https://user.annotell.com/v1/"
            engine_url = "https://engine.annotell.com/v1/"
            storage_url = "https://storage.annotell.com/v1/"
            metrics_url = "https://metrics.annotell.com/v1/"
            event_url = "https://event.annotell.com/v1/"
        else:
            user_url = "http://annotell.org:8001/v1/"
            engine_url = "http://annotell.org:8002/v1/"
            storage_url = "http://annotell.org:8004/v1/"
            metrics_url = "http://annotell.org:8005/v1/"
            event_url = "http://annotell.org:8006/v1/"
        self.user_api_admin = UserApi(email=email, password=password, base_url=user_url)
        self.engine_api = EngineApi(None, session=self.session, base_url=engine_url)
        self.storage_api = StorageApi(None, session=self.session, base_url=storage_url)
        self.metrics_api = MetricsApi(None, session=self.session, base_url=metrics_url)
        self.event_api = EventApi(None, session=self.session, base_url=event_url)

    @property
    def session(self):
        return self.user_api_admin.session
