import argparse
import atexit
import datetime
import inspect
import json
import logging
import os
import sys
import uuid

import requests
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql import utils as sql_utils
from pyspark.sql.functions import col

from annotell.core.kpi.Result import Result

parser = argparse.ArgumentParser(description='handles execution manager arguments')

API_VERSION = '/v1'

## Setup Logging
FORMAT = '%(asctime)-15s %(levelname)-5s [%(name)-40s] %(message)s'
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)
logging.basicConfig(format=FORMAT, stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


class ExecutionManager:
    def __init__(self, project_id, dataset_id, kpi_host='https://kpi.annotell.com', auth_host=DEFAULT_AUTH_HOST):
        parser.add_argument('--session-id', type=str, help='Session id')
        parser.add_argument("--filter-file", type=str, help="JSON filter from file")
        parser.add_argument("--filter-json", type=str, help="JSON string version of filter")
        parser.add_argument("--script-hash", type=str, help="Hash of file in current state")
        parser.add_argument("--client-id", type=str, help="Client ID used for authentication")
        parser.add_argument("--client-secret", type=str, help="Client secret used for authentication")
        parser.add_argument("--execution-mode", type=str, help="How is this script being run?")
        args = parser.parse_args()

        ## Each execution run has necessary core information
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.session_id = args.session_id or str(uuid.uuid4())
        self.script_hash = args.script_hash or 'local_execution_mode'
        self.execution_mode = args.execution_mode or 'local_testing'
        self.kpi_host = kpi_host
        self.client_id = args.client_id or ""
        self.client_secret = args.client_secret or None

        self.filter_file = args.filter_file or None
        self.filter_json = args.filter_json or None
        self.filter_dict = None
        self.filter_id = ""

        if self.client_secret:
            log.debug(f"authenticating using client_id={self.client_id} client_secret={self.client_secret}")
            self.oauth_session = AuthSession(host=auth_host,
                                             client_id=self.client_id,
                                             client_secret=self.client_secret)
        else:
            log.info('authentication using credentials from environment')
            self.oauth_session = AuthSession(host=auth_host)

        self.session = self.oauth_session.session

        if self.filter_json:
            self.filter_dict = json.loads(self.filter_json)
            self.filter_id = self.filter_dict['filter_id']
            self.submit_event('filter_added', f'will use filter_id={self.filter_id}')

        self.data_path = str(self.execution_mode) + '/' + \
                         str(self.project_id) + '/' + \
                         str(self.dataset_id) + "/*"
        abs_path = os.path.abspath((inspect.stack()[1])[1])
        self.root_dir = os.path.dirname(abs_path)
        self.absolute_data_path = os.path.join(self.root_dir, self.data_path)
        self.app_name = 'execution_mode=' + self.execution_mode + \
                        ':project_id=' + str(self.project_id) + \
                        ':dataset_id=' + str(self.dataset_id) + \
                        ':session_id=' + str(self.session_id)
        atexit.register(self.script_completed)
        log.debug(self.app_name)
        self.submit_event('initialized', context=f'started app_name={self.app_name} to {self.kpi_host}')

    def load_data(self):
        config = SparkConf()
        spark_context = SparkContext(appName=self.app_name, master="local[*]", conf=config)
        spark_context.setLogLevel("ERROR")
        spark_sql_context = SQLContext(spark_context)
        log.debug(f"absolut_data_path={self.absolute_data_path}")
        try:
            data_frame = spark_sql_context.read.parquet(self.absolute_data_path)
        except sql_utils.AnalysisException:
            self.submit_event(type='data_loading_failed',
                              context=f"absolute_data_path={self.absolute_data_path}")
            raise Exception(f"absolute_data_path={self.absolute_data_path} did not exist")
        self.submit_event(type='data_loaded',
                          context=f"absolute_data_path={self.absolute_data_path}")
        if self.filter_dict:
            column_filters = self.filter_dict['content']['column_filters']
            for col_filter in column_filters:
                try:
                    log.debug(f"filtered column={col_filter['column']} to match values={col_filter['values']}")
                    data_frame = data_frame.filter(col(col_filter['column']).isin(col_filter['values']))
                    self.submit_event(type='data_filtered',
                                      context=f"column={col_filter['column']} limited to values={col_filter['values']}")
                except sql_utils.AnalysisException:
                    log.error(f"column {col_filter['column']} not found in DataFrame")
            return data_frame, spark_context
        else:
            return data_frame, spark_context

    def script_completed(self):
        self.submit_event("script_completed", "you deserve some coffee now! ☕️")

    def submit_event(self, type: str, context: str, created=None):
        event = {
            "session_id": self.session_id,
            "type": type,
            "context": context,
            "created": created or str(datetime.datetime.now())
        }
        log.debug(f"sending event={json.dumps(event)}")
        try:
            return self.session.post(url=self.kpi_host + API_VERSION + "/event", data=json.dumps(event))
        except requests.exceptions.ConnectionError:
            log.error(f"Cannot submit event, the server={self.kpi_host} probably did not respond")
            return None

    def submit_kpi_results(self, results):
        """
        Used to report results to results database once KPI script has executed.
        All results submitted need to be of type Result.

        Parameters
        ----------
        :param results:
        """
        for result in results:
            if isinstance(result, Result):
                result.set_session_id(session_id=self.session_id)
                result.set_project_id(project_id=self.project_id)
                result.set_dataset_id(dataset_id=self.dataset_id)
                result.set_script_hash(script_hash=self.script_hash)
                result.set_filter_id(filter_id=self.filter_id)
                result.set_execution_mode(execution_mode=self.execution_mode)

                log.debug(f"sending {result.toJSON()}")
                try:
                    response_json = self.session.post(url=self.kpi_host + API_VERSION + "/result", data=result.toJSON())
                except requests.exceptions.ConnectionError:
                    log.error(f"Cannot submit result, the server={self.kpi_host} probably did not respond")
                    self.submit_event('result_submit_failed', f'the server={self.kpi_host} probably did not respond')
                    return None
                if response_json.status_code in [200, 201]:
                    self.submit_event('result_submitted', f'api response {response_json.status_code}')
                else:
                    self.submit_event('result_submit_failed', f'api response {response_json.status_code}')
            else:
                self.submit_event('result_submit_failed', f'tried to submit something which is not a result')
