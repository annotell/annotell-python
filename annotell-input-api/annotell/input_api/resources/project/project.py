from typing import List

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


class ProjectResource(InputAPIResource):
    """
    Project related information
    """

    def get_projects(self) -> List[IAM.Project]:
        """
        Returns all projects connected to the users organization.

        :return List: List containing all projects connected to the user
        """
        json_resp = self.client.get("v1/projects")
        return [IAM.Project.from_json(js) for js in json_resp]

    def get_project_batches(self, project: str) -> List[IAM.Project]:
        """
        Returns all `batches` for the `project`.

        :return List: List containing all batches
        """
        json_resp = self.client.get(f"v1/projects/{project}/batches")
        return [IAM.InputBatch.from_json(js) for js in json_resp]

    def publish_batch(self, project: str, batch: str) -> IAM.InputBatch:
        """
        Publish input batch, marking the input batch ready for annotation.
        After publishing, no more inputs can be added to the input batch

        :return InputBatch: Updated input batch
        """
        json_resp = self.client.post(f"v1/projects/{project}/batches/{batch}/publish")
        return IAM.InputBatch.from_json(json_resp)
