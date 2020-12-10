from typing import List
from annotell.input_api.model.abstract.abstract_models import Response


class InvalidatedInputsResponse(Response):
    def __init__(self, invalidated_input_ids: List[int], not_found_input_ids: List[int], already_invalidated_input_ids: List[int]):
        self.invalidated_input_ids = invalidated_input_ids
        self.not_found_input_ids = not_found_input_ids
        self.already_invalidated_input_ids = already_invalidated_input_ids

    @staticmethod
    def from_json(js: dict):
        return InvalidatedInputsResponse(js["invalidatedInputIds"],
                                         js["notFoundInputIds"],
                                         js["alreadyInvalidatedInputIds"])

    def __repr__(self):
        return f"<InvalidatedInputsResponse(" + \
               f"invalidated_input_ids={self.invalidated_input_ids}, " + \
               f"not_found_input_ids={self.not_found_input_ids}, " + \
               f"already_invalidated_input_ids={self.already_invalidated_input_ids})>"
