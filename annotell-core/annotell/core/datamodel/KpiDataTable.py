from typing import List, Union

class KpiDataTable:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'A KpiDataTable named %s' % self.name

    @property
    def columns(self):
        return ["test1", "test2"]
