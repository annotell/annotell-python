import json
import os
import time
import requests
import uuid
import json
import datetime
import argparse
import logging
import sys

from pyspark import SparkContext
from pyspark.sql import SQLContext
from annotell.core.kpi.Kpi import KPI

parser = argparse.ArgumentParser(description='execution manager app arguments')

API_VERSION = '/v1'

log = logging.getLogger(__name__)


class ExecutionManager:
    def __init__(self, root_directory, username, password, host='http://localhost:5005'):
        parser.add_argument('--session-id', type=str, help='Session id')
        parser.add_argument("--filter", type=argparse.FileType('r'), help="JSON file with test config")
        parser.add_argument("--script-hash", type=str, help="Hash of file in current state")
        parser.add_argument("--source", type=str, help="Tells the backend who generate results")

        args = parser.parse_args()

        session_id = args.session_id
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())

        filter = args.filter
        if filter:
            self.filter = json.loads(filter.read())

        script_hash = args.script_hash
        if script_hash:
            self.script_hash = str(script_hash)
        else:
            self.script_hash = 'localmode'

        source = args.source
        if source:
            self.source = str(source)
        else:
            self.source = 'localhost'

        self.host = host
        self.root_dir = root_directory
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.submit_event('initialized', context='connected to {HOST}'.format(HOST=host))

    def load_data(self, project_name: str):
        sample_data_dir = os.path.join(self.root_dir, 'sample_data')
        parquet_path = os.path.join(sample_data_dir, project_name + '_latest.parquet')
        spark_context = SparkContext(appName=project_name, master="local[4]")
        spark_sql_context = SQLContext(spark_context)
        data_frame = spark_sql_context.read.parquet(parquet_path)
        self.submit_event(type='data_loaded', context='')
        return data_frame, spark_context, spark_sql_context

    def script_completed(self):
        self.submit_event("script_completed", "you deserve some coffee now!")

    def create_kpi(self, kpi_id, kpi_type, kpi_tags=None, kpi_groups=None):
        kpi = {}
        kpi['kpi_id'] = int(kpi_id)
        kpi['kpi_type'] = kpi_type
        kpi['kpi_tags'] = kpi_tags
        kpi['kpi_groups'] = kpi_groups
        kpi_json = json.dumps(kpi)
        log.info(kpi_json)
        response = self.session.post(url=self.host + API_VERSION + "/kpi", data=kpi_json)
        return response


    def submit_event(self, type: str, context: str, created=None):
        event = {}
        event['session_id'] = self.session_id
        event['type'] = type
        event['context'] = context
        if created == None:
            event['created'] = str(datetime.datetime.now())
        log.info(json.dumps(event))
        try:
            return self.session.post(url=self.host + API_VERSION + "/events", data=json.dumps(event))
        except requests.exceptions.ConnectionError:
            log.warn(requests.exceptions)
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
            result.set_session_id(session_id=self.session_id)
            result.set_script_hash(script_hash=self.script_hash)
            result.set_source(source=self.source)
            to_json = result.toJSON()
            response_json = self.session.post(url=self.host + API_VERSION + "/result", data=to_json)
            response_code = response_json.status_code
            if response_code in [200, 201]:
                response = json.loads(response_json.content)
                self.submit_event('result_submitted', 'API response {}'.format(response_code))
            else:
                self.submit_event('result_submit_failed', 'API response {}'.format(response_code))
