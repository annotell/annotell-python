import logging
from typing import Optional

from annotell.input_api import model as IAM
from annotell.input_api.util import get_resource_id, get_image_dimensions
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class LidarAndImageSequenceResource(CreateableInputAPIResource):

    path = 'lidars-and-cameras-sequence'

    @staticmethod
    def _set_resource_id(lidars_and_cameras_sequence: IAM.LidarsAndCamerasSequence,
                         upload_urls_response: IAM.UploadUrlsResponse):

        resources = lidars_and_cameras_sequence.get_local_resources()
        for resource in resources:
            if resource.resource_id is None:
                resource.resource_id = get_resource_id(upload_urls_response.files_to_url[resource.filename])

    @staticmethod
    def _set_sensor_settings(lidars_and_cameras_sequence: IAM.LidarsAndCamerasSequence):

        first_frame = lidars_and_cameras_sequence.frames[0]
        sensor_settings = {
            image_frame.sensor_name: get_image_dimensions(image_frame.filename) for image_frame in first_frame.image_frames
        }
        if lidars_and_cameras_sequence.sensor_specification is None:
            lidars_and_cameras_sequence.sensor_specification = IAM.SensorSpecification(sensor_settings=sensor_settings)
        elif lidars_and_cameras_sequence.sensor_specification.sensor_settings is None:
            lidars_and_cameras_sequence.sensor_specification.sensor_settings = sensor_settings

    def _get_files_to_upload(self, lidars_and_cameras_sequence: IAM.LidarsAndCamerasSequence) -> IAM.UploadUrlsResponse:
        resources = lidars_and_cameras_sequence.get_local_resources()
        files_to_upload = list(map(lambda res: res.filename, resources))
        upload_urls_response = self.get_upload_urls(IAM.FilesToUpload(files_to_upload))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_to_upload) == set(files_in_response)

        return upload_urls_response

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

        upload_urls_response = self._get_files_to_upload(lidars_and_cameras_sequence)
        self._set_resource_id(lidars_and_cameras_sequence, upload_urls_response)
        self._set_sensor_settings(lidars_and_cameras_sequence)

        # We need to set job-id from the response
        payload = lidars_and_cameras_sequence.to_dict()
        payload['internalId'] = upload_urls_response.internal_id

        self.post_input_request(self.path, payload,
                                project=project,
                                batch=batch,
                                input_list_id=input_list_id,
                                dryrun=True)

        if dryrun:
            return

        self.file_resource_client.upload_files(upload_urls_response.files_to_url)

        create_input_response = self.post_input_request(
            self.path,
            payload,
            project=project,
            batch=batch,
            input_list_id=input_list_id,
            dryrun=False
        )

        log.info(f"Created inputs for files with job_id={create_input_response.internal_id}")
        return create_input_response
