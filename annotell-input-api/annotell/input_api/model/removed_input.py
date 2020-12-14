from dataclasses import dataclass
from typing import List


@dataclass
class RemovedInputsResponse:
    removed_input_ids: List[int]
    not_found_input_ids: List[int]
    already_removed_input_ids: List[int]

    @staticmethod
    def from_json(js: dict):
        return RemovedInputsResponse(js["removedInputIds"],
                                     js["notFoundInputIds"],
                                     js["alreadyRemovedInputIds"])
