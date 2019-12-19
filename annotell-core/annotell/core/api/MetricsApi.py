"""
Metrics API client
"""
import requests
import json

from apiclients.AnnotellLogger import AnnotellLogger
from apiclients.BaseApi import BaseApi
from apiclients.DataModel.DataModelBase import data_model_factory
from apiclients.DataModel import DataModelAnnotation


logger = AnnotellLogger.get_logger(__name__)


class MetricsApi(BaseApi):
    """ Metrics API client """

    def __init__(self, token, session=requests.session(), base_url="http://annotell.org:8005/v1/"):
        logger.debug("starting " + str(__name__))
        super().__init__(session, token, base_url)

    # --- methods in MetricRoute ---

    def get_active_working_time_per_day(self, user_id, days_back):
        if user_id is None or days_back is None:
            raise TypeError('you have to specify user id and days back')
        else:
            active_working_time_with_infos_json = self._api_get("metric/active-working-time?userId=" + str(user_id) + "&daysBack=" + str(days_back))
            response = json.loads(active_working_time_with_infos_json)['content']['activeWorkingTimeWithInfos']
            return [
                data_model_factory(DataModelAnnotation.ActiveWorkingTimeWithInfo, {'active_working_time_with_info': awtwi_json}) for awtwi_json in response['activeWorkingTimeWithInfos']
            ]
