from typing import List, Optional, Union, Dict

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


class AnnotationResource(InputAPIResource):
    def get_annotations(self, internal_ids: List[str]
                             ) -> Dict[str, List[IAM.ExportAnnotation]]:
        """
        Returns the export ready annotations, either
        * All annotations connected to a specific request, if a request id is given
        * All annotations connected to the organization of the user, if no request id is given

        :param internal_ids: List with internal ids
        :param request_id: An id of a request
        :return Dict: A dictionary containing the ready annotations
        """
        js = internal_ids
        json_resp = self.client.get("v1/annotations", json=js)

        annotations = dict()
        for k, v in json_resp.items():
            annotations[k] = [IAM.ExportAnnotation.from_json(annotation) for annotation in v]
        return json_resp
