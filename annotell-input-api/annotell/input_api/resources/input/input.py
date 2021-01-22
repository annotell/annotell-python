import logging
from typing import List, Optional, Dict

from annotell.input_api import model as IAM
from annotell.input_api.util import filter_none
from annotell.input_api.resources.abstract import InputAPIResource

log = logging.getLogger(__name__)


class InputResource(InputAPIResource):
    """
    Class exposing Annotell Inputs
    """

    def get_internal_ids_for_external_ids(self, external_ids: List[str]) -> Dict[str, List[str]]:
        """
        For each external id returns a list of internal ids, connected to the external id.

        :param external_ids: List of external ids
        :return Dict: Dictionary mapping each external id to a list of internal ids
        """
        js = external_ids
        return self.client.get("v1/inputs/", json=js)

    def invalidate_inputs(self, input_ids: List[str], invalidated_reason: IAM.InvalidatedReasonInput):
        """
        Invalidates inputs, and removes them from all input lists

        :param input_ids: The input internal ids to invalidate
        :param invalidated_reason: An Enum describing why inputs were invalidated
        :return InvalidatedInputsResponse: Class containing what inputs were invalidated
        """
        invalidated_json = dict(inputIds=input_ids, invalidatedReason=invalidated_reason)
        resp_json = self.client.post("v1/inputs/invalidate", json=invalidated_json)
        return IAM.InvalidatedInputsResponse.from_json(resp_json)

    def get_inputs(self, project: str, batch: str, invalidated: bool = False, external_id: Optional[str] = None) -> List[IAM.Input]:
        """
        Gets inputs for project, with option to filter for invalidated inputs

        :param project: Project (identifier) to filter
        :param batch: Batch (identifier) to filter
        :param invalidated: Returns invalidated inputs if True, otherwise valid inputs
        :param external_id: External ID to filter input on
        :return List: List of Inputs
        """

        json_resp = self.client.get("v1/inputs", params=filter_none({
            "project": project,
            "batch": batch,
            "invalidated": invalidated,
            "externalId": external_id
        }))
        return [IAM.Input.from_json(js) for js in json_resp]
