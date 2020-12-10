from typing import List
from annotell.input_api.model.abstract.abstract_models import Response


class RemovedInputsResponse(Response):
    def __init__(self, removed_input_ids: List[int], not_found_input_ids: List[int], already_removed_input_ids: List[int]):
        self.removed_input_ids = removed_input_ids
        self.not_found_input_ids = not_found_input_ids
        self.already_removed_input_ids = already_removed_input_ids

    @staticmethod
    def from_json(js: dict):
        return RemovedInputsResponse(js["removedInputIds"],
                                         js["notFoundInputIds"],
                                         js["alreadyRemovedInputIds"])

    def __repr__(self):
        return f"<RemovedInputsResponse(" + \
               f"removed_input_ids={self.removed_input_ids}, " + \
               f"not_found_input_ids={self.not_found_input_ids}, " + \
               f"already_removed_input_ids={self.already_removed_input_ids})>"