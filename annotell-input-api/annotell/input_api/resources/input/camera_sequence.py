import logging
from typing import Optional

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import CreateableInputAPIResource

class CameraSequenceResource(CreateableInputAPIResource):
    def create(self,
               cameras_sequence: IAM.CamerasSequence,
               project: Optional[str] = None,
               batch: Optional[str] = None,
               input_list_id: Optional[int] = None,
               dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Upload files and create an input of type ``cameras_sequence``.

        :param cameras_sequence: class containing 2D that constitute the input
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns CreateInputJobResponse: Class containing id of the created input job, or None if dryrun.

        The files are uploaded to annotell GCS and an input_job is submitted to the inputEngine.
        If the input_job fails (cannot perform conversion) the input is not added. To see if
        conversion was successful please see the method `get_input_jobs_status`.
        """
        self._create(cameras_sequence,
                     project=project,
                     batch=batch,
                     input_list_id=input_list_id,
                     dryrun=dryrun)
