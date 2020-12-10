from typing import List, Mapping

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


class DataResource(InputAPIResource):
    """
    Class exposing Annotel Data:s
    Will be removed during v1. release...
    """

    def get_datas_for_inputs_by_internal_ids(self, internal_ids: List[str]) -> Mapping[IAM.Input, List[IAM.Data]]:
        """
        For every internal id given, returns that input together with all the data connected to that input

        :param internal_ids: List of internal ids
        :return Mapping: Maps a Input with all the data conntected to it
        """
        js = internal_ids
        # TODO: change this, sending JSON in GET is not cool
        json_resp = self.client.get("v1/inputs/datas-internal-id", json=js)

        new_dict = {}
        for (k, v) in json_resp:
            new_key = IAM.Input.from_json(k)
            new_values = [IAM.Data.from_json(vv) for vv in v]
            new_dict[new_key] = new_values

        return new_dict

    def get_datas_for_inputs_by_external_ids(self, external_ids: List[str]) -> Mapping[IAM.Input, List[IAM.Data]]:
        """
        For every external id given, returns that input together with all the data connected to that input

        :param external_ids: List of external ids
        :return Mapping: Maps a Input with all the data connected to it
        """
        js = external_ids
        json_resp = self.client.get("v1/inputs/datas-external-id", json=js)

        new_dict = {}
        for (k, v) in json_resp:
            new_key = IAM.Input.from_json(k)
            new_values = [IAM.Data.from_json(vv) for vv in v]
            new_dict[new_key] = new_values

        return new_dict
