from typing import List

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import InputAPIResource


class ProjectResource(InputAPIResource):
    """
    Project related information
    """

    def get_requests_for_project_id(self, project_id: int) -> List[IAM.Request]:
        """
        Returns all Requests connected to a project id

        :param project_id: A project id
        :return List: List containing Request objects
        """
        json_resp = self.client.get("v1/inputs/requests", params={
            "projectId": project_id
        })

        return [IAM.Request.from_json(js) for js in json_resp]

    def list_projects(self) -> List[IAM.Project]:
        """
        Returns all projects connected to the users organization.

        :return List: List containing all projects connected to the user
        """
        json_resp = self.client.get("v1/inputs/project")
        return [IAM.Project.from_json(js) for js in json_resp]

    def list_project_batches(self, project: str) -> List[IAM.Project]:
        """
        Returns all `batches` for the `project`.

        :return List: List containing all batches
        """
        json_resp = self.client.get(f"v1/inputs/project/{project}/batch")
        return [IAM.InputBatch.from_json(js) for js in json_resp]

    def list_input_lists(self, project_id: int) -> List[IAM.InputList]:
        """
        Returns a list of all input lists connected to the specified project.

        :param project_id: The id of the project
        :return List: List with the input lists connected to the project id
        """
        json_resp = self.client.get(f"v1/inputs/input-lists?projectId={project_id}")
        return [IAM.InputList.from_json(js) for js in json_resp]

    def publish_batch(self, project: str, batch: str) -> IAM.InputBatch:
        """
        Publish input batch, marking the input batch ready for annotation.
        After publishing, no more inputs can be added to the input batch

        :return InputBatch: Updated input batch
        """
        json_resp = self.client.post(f"v1/inputs/project/{project}/batch/{batch}/publish")
        return IAM.InputBatch.from_json(json_resp)
