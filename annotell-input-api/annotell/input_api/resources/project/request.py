from typing import List, Dict

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


# TODO: Remove Request resource, not part of Input Domain..


class RequestResource(InputAPIResource):
    """
    Class exposing Annotell Requests
    """

    def get_requests_for_request_ids(self, request_ids: List[int]) -> Dict[int, IAM.Request]:
        """
        Returns a list of request objects, given a list of request ids

        :param request_ids: List of request ids
        :return Dict: Dictionary mapping a request id to a Request object
        """
        js = request_ids
        json_resp = self.client.get("v1/inputs/requests", json=js)
        dict_resp = dict()
        for k, v in json_resp.items():
            dict_resp[int(k)] = IAM.Request.from_json(v)
        return dict_resp

    def get_requests_for_input_lists(self, input_list_id: int) -> List[IAM.Request]:
        """
        Returns all requests connected to a specific input list

        :param input_list_id: The input list id we want to get the connected Requests for.
        :return List: List of Request objects
        """
        json_resp = self.client.get("v1/inputs/requests", params={
            "inputListId": input_list_id
        })
        return [IAM.Request.from_json(js) for js in json_resp]
