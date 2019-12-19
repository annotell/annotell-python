"""
Event API client
"""
import requests

from apiclients.AnnotellLogger import AnnotellLogger
from apiclients.BaseApi import BaseApi

logger = AnnotellLogger.get_logger(__name__)


class EventApi(BaseApi):
    """ Event API client """

    def __init__(self, token, session=requests.session(), base_url="http://annotell.org:8006/v1/"):
        logger.debug("starting " + str(__name__))
        super().__init__(session, token, base_url)

    # --- methods in WorkingTimeRoute ---

    def aggregate_active_working_time(self, assignment_ids):
        return_params = self._api_post("working-time/update", assignment_ids)
        return return_params
