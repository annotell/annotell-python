from annotell.core.kpi import util
from datetime import datetime
import time
import json


def _human_readable(posix_time):
    return datetime.utcfromtimestamp(posix_time).strftime('%Y-%m-%dT%H:%M:%SZ')


class KPI:
    def __init__(self, kpi_type, kpi_id, name):
        if not util.valid_kpi_type(kpi_type):
            raise ValueError('Invalid KPI type')
        self.kpi_type = kpi_type
        self.name = name
        self.kpi_id = kpi_id
        self.created = int(time.time())
        self.results = []

    def add_result(self, result, created=int(time.time())) -> None:
        if not isinstance(result, dict):
            raise ValueError('Please provide dict of result')
        keys = result.keys()
        result['created'] = created
        if self.kpi_type == 'fraction':
            expected_keys = ['numerator', 'denominator', 'threshold', 'created']
            if not util.valid_result_keys(keys, expected_keys):
                raise ValueError("Invalid result keys: {}, expected: {}".format(keys, expected_keys))
            else:
                self.results.append(result)
        if self.kpi_type == 'histogram':
            expected_keys = ['splits', 'items', 'created']
            if not util.valid_result_keys(keys, expected_keys):
                raise ValueError("Invalid result keys: {}, expected: {}".format(keys, expected_keys))
            else:
                for item in result['items']:
                    expected_keys = ['bin', 'value', 'count']
                    item_keys = item.keys()
                    if not util.valid_result_keys(item_keys, expected_keys):
                        raise ValueError("Invalid result keys: {}, expected: {}".format(item_keys, expected_keys))
                self.results.append(result)

    def get_results(self):
        return self.results

    def print_kpi_results(self):
        if len(self.results) == 0:
            print("No KPI results added yet for kpiId={}".format(self.kpi_id))
        print("KPI Results for kpiId={}\n".format(self.kpi_id))
        for kpiResult in self.results:
            if self.kpi_type == 'fraction':
                print("kpiId:\t\t {}\n"
                      "Result:\t\t {}\n"
                      "Threshold:\t {}\n"
                      "Created:\t {}\n".format(self.kpi_id,
                                               kpiResult['result'],
                                               kpiResult['threshold'],
                                               _human_readable(kpiResult['created'])))
            else:
                raise NotImplementedError('Printing results for this KPI type is not implemented yet')

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
