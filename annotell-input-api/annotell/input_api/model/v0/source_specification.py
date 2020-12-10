
from typing import Optional, List, Dict
from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import RequestCall
from annotell.input_api.util import ts_to_dt


class SourceSpecification(RequestCall):
    def __init__(self, source_to_pretty_name: Optional[Dict[str, str]] = None,
                 source_order: Optional[List[str]] = None):

        self.source_to_pretty_name = source_to_pretty_name
        self.source_order = source_order

    def to_dict(self):
        as_dict = {}
        if self.source_to_pretty_name is not None:
            as_dict['sourceToPrettyName'] = self.source_to_pretty_name
        if self.source_order is not None:
            as_dict['sourceOrder'] = self.source_order

        return as_dict