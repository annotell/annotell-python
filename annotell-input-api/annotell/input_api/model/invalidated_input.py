from dataclasses import dataclass
from typing import List


@dataclass
class InvalidatedInputsResponse:
    invalidated_input_ids: List[int]
    not_found_input_ids: List[int]
    already_invalidated_input_ids: List[int]

    @staticmethod
    def from_json(js: dict):
        return InvalidatedInputsResponse(js["invalidatedInputIds"],
                                         js["notFoundInputIds"],
                                         js["alreadyInvalidatedInputIds"])
