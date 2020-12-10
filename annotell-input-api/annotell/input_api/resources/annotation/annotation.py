from typing import List, Optional, Union, Dict

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


class AnnotationResource(InputAPIResource):
    def download_annotations(self, internal_ids: List[str], request_id: Optional[int] = None
                             ) -> Dict[str, Union[Dict[int, IAM.ExportAnnotation], IAM.ExportAnnotation]]:
        """
        Returns the export ready annotations, either
        * All annotations connected to a specific request, if a request id is given
        * All annotations connected to the organization of the user, if no request id is given

        :param internal_ids: List with internal ids
        :param request_id: An id of a request
        :return Dict: A dictionary containing the ready annotations
        """
        js = internal_ids
        json_resp = self.client.get("v1/inputs/export", json=js, params={
            "requestId": request_id,
        })

        if request_id is None:
            for k, v in json_resp.items():
                inner_dict_resp = dict()
                for kk, vv in v.items():
                    inner_dict_resp[int(kk)] = IAM.ExportAnnotation.from_json(vv)
                json_resp[k] = inner_dict_resp
            return json_resp

        else:
            for k, v in json_resp.items():
                json_resp[k] = IAM.ExportAnnotation.from_json(v)
            return json_resp

    def get_input_status(self, internal_ids: List[str]) -> Dict[str, Dict[int, bool]]:
        """
        Returns a nested dictionary, the outmost key is the internal_id, which points to a
        dictionary whose keys are the request_ids for the requests where the input is included
        (via the inputList). The key is a boolean denoting if the input is ready for export (true)
        or not (false).

        :param internal_ids: List of internal ids
        :return Dict: Nested dictionary that for each input and request specify it is ready
        for export or not.
        """
        js = internal_ids
        json_resp = self.client.get("v1/inputs/export-status", json=js)
        for k, v in json_resp.items():
            inner_dict_resp = dict()
            for kk, vv in v.items():
                inner_dict_resp[int(kk)] = vv
            json_resp[k] = inner_dict_resp

        return json_resp
