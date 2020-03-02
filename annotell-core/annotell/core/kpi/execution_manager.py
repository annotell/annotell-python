import requests
import time
import os

from model import Event
from annotell.core.kpi.kpi import KPI

from pyspark import SparkContext
from pyspark.sql import SQLContext

class ExecutionManager:
    def __init__(self, kpi_manager_host):
        self.session_id = 'test_session_id'
        self.host = kpi_manager_host

    def load_data(self, project_name: str):
        # compute absolute paths to the data
        pardir = os.path.dirname(os.path.abspath(__file__))
        sampleDataDir = os.path.join(pardir, 'sample_data')
        parquetObjectsPath = os.path.join(sampleDataDir, '10km_fixed_offset.parquet')
        sc = SparkContext(appName="object_detection", master="local")
        sqlContext = SQLContext(sc)
        data_frame = sqlContext.read.parquet(parquetObjectsPath)
        self.submit_event(session_id=123, event_type='data_load',
                          event_context='na', event_time=int(time.time()))
        return data_frame

    def submit_event(self, session_id: int, event_type: str, event_context: str, event_time: int):
        event = Event(session_id, event_type, event_context, event_time)
        r = requests.post(url=self.host + "/event", data=event)
        return r

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

            for result in kpi.get_results():
                print(
                    "stub for submitting results, this will be done via HTTPS calls to result storage API once deployed")
                print("result: {}".format(result))
                r = requests.get("http://localhost:5000/submit_result")
                print(r.status_code)
                print(r.headers)
                print(r.content)
