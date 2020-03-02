import json
import os
import time
import requests

from pyspark import SparkContext
from pyspark.sql import SQLContext

from annotell.core.kpi.kpi import KPI


class ExecutionManager:
    def __init__(self, root_directory, kpi_manager_host='http://localhost:5000'):
        self.session_id = 'test_session_id'
        self.host = kpi_manager_host
        self.root_dir = root_directory
        self.submit_event('initialized', '')

    def load_data(self, project_name: str):
        sample_data_dir = os.path.join(self.root_dir, 'sample_data')
        parquet_path = os.path.join(sample_data_dir, project_name + '_latest.parquet')
        sc = SparkContext(appName=project_name, master="local")
        sql_context = SQLContext(sc)
        data_frame = sql_context.read.parquet(parquet_path)
        self.submit_event(type='data_loaded', context='na')
        return data_frame, sc, sql_context

    def submit_event(self, type: str, context: str, event_time=int(time.time())):
        event = {}
        event['session_id'] = self.session_id
        event['type'] = type
        event['context'] = context
        event['time'] = event_time
        return requests.post(url=self.host + "/v1/events", data=json.dumps(event))

    def submit_kpi_results(self, kpis):
        """
        Used to report results to results database once KPI script has executed.
        All results submitted need to be of type Kpi.

        Parameters
        ----------
        :param kpis:
        """

        for kpi in kpis:
            if not isinstance(kpi, KPI):
                raise ValueError("Trying to submit something which is not a result: {}".format(result))

            requests.post("http://localhost:5000/v1/result", data=kpi.toJSON())
