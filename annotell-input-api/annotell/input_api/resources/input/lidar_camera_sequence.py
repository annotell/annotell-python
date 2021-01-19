import logging
from typing import Optional

from annotell.input_api import model as IAM
from annotell.input_api.util import get_resource_id, get_image_dimensions
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class LidarAndImageSequenceResource(CreateableInputAPIResource):

    path = 'lidars-and-cameras-sequence'

    @staticmethod
    def _set_sensor_settings(lidars_and_cameras_sequence: IAM.LidarsAndCamerasSequence):
        def _create_camera_settings(width_height_dict: dict):
            return IAM.CameraSettings(width_height_dict['width'], width_height_dict['height'])

        def _create_sensor_settings():
            first_frame = lidars_and_cameras_sequence.frames[0]
            return {
                image_frame.sensor_name: _create_camera_settings(get_image_dimensions(image_frame.filename)) for image_frame in first_frame.image_frames
            }
            
        if lidars_and_cameras_sequence.sensor_specification is None:
            lidars_and_cameras_sequence.sensor_specification = IAM.SensorSpecification(sensor_settings=_create_sensor_settings())
        elif lidars_and_cameras_sequence.sensor_specification.sensor_settings is None:
            lidars_and_cameras_sequence.sensor_specification.sensor_settings = _create_sensor_settings()

    def create(self,
               lidars_and_cameras_sequence: IAM.LidarsAndCamerasSequence,
               project: Optional[str] = None,
               batch: Optional[str] = None,
               input_list_id: Optional[int] = None,
               dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Upload files and create an input of type ``lidars_and_cameras_sequence``.

        :param lidars_and_cameras_sequence: class containing 2D and 3D resources that constitute the input
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns CreateInputJobResponse: Class containing id of the created input job, or None if dryrun.

        The files are uploaded to annotell GCS and an input_job is submitted to the inputEngine.
        In order to increase annotation tool performance the supplied pointcloud-file is converted
        into potree after upload (server side). Supported fileformats for pointcloud files are
        currently .csv & .pcd (more information about formatting can be found in the readme.md).
        The job is successful once it converts the pointcloud file into potree, at which time an
        input of type 'lidars_and_cameras_sequence' is created for the designated `project` `batch` or `input_list_id`.
        If the input_job fails (cannot perform conversion) the input is not added. To see if
        conversion was successful please see the method `get_input_jobs_status`.
        """

        self._set_sensor_settings(lidars_and_cameras_sequence)

        # We need to set job-id from the response
        payload = lidars_and_cameras_sequence.to_dict()

        response = self.post_input_request(self.path, payload,
                                project=project,
                                batch=batch,
                                input_list_id=input_list_id,
                                dryrun=dryrun)

        if dryrun:
            return

        log.info(f"Created inputs for files with job_id={response.internal_id}")
        return response
