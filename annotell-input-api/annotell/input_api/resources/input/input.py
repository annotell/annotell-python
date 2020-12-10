from typing import List, Mapping, Optional, Dict

import logging

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource

log = logging.getLogger(__name__)

class InputResource(InputAPIResource):
    """
    Class exposing Annotell Inputs
    """

    def get_input_jobs_status(self, internal_ids: Optional[List[str]] = None,
                              external_ids: Optional[List[str]] = None
                              ) -> List[IAM.InputJob]:
        """
        Returns a list of input jobs, either:
        * All input jobs connected to the given lists of internal and external ids
        * All input jobs connected to the user organization, if no ids were given

        :param internal_ids: List of internal ids
        :param external_ids: List of external ids
        :return List: List containing InputJob objects
        """

        if internal_ids is None:
            internal_ids = []
        if external_ids is None:
            external_ids = []

        js = dict(
            internalIds=internal_ids,
            externalIds=external_ids
        )
        json_resp = self.client.post("v1/inputs/job-status", json=js)

        return [IAM.InputJob.from_json(js) for js in json_resp]

    def count_inputs_for_external_ids(self, external_ids: List[str]) -> Dict[str, int]:
        """
        For each external id, returns a count of how many inputs exists with that external id.

        :param external_ids: List of external ids
        :return Dict: Dictionary which maps an external id to a count of inputs with that external id
        """

        if len(external_ids) == 0:
            log.error("You need to specify a list of external ids.")
            return

        external_ids_csv = ",".join(external_ids)
        json_resp = self.client.get("v1/inputs/count-for-ids", params={
            "externalIds": external_ids_csv
        })
        return json_resp

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

    def remove_inputs_from_input_list(self, input_list_id: int, input_ids: List[int]):
        """
        Removes inputs from specified input list, without invalidating the input

        :param input_list_id: The input list id where the inputs should be removed
        :param input_ids: The input ids to remove
        :return RemovedInputsResponse: Class containing what inputs were removed
        """
        removed_json = dict(inputListId=input_list_id, inputIds=input_ids)
        resp_json = self.client.post("v1/inputs/remove", json=removed_json)
        return IAM.RemovedInputsResponse.from_json(resp_json)

    def get_inputs(self, project_id: int, invalidated: bool = False) -> List[IAM.Input]:
        """
        Gets inputs for project, with option to filter for invalidated inputs

        :param project_id: Project id to filter
        :param invalidated: Returns invalidated inputs if True, otherwise valid inputs
        :return List: List of Inputs
        """

        json_resp = self.client.get("v1/inputs", params={
            "projectId": project_id,
            "invalidated": invalidated
        })
        return [IAM.Input.from_json(js) for js in json_resp]
