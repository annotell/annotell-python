import logging
from pathlib import Path
from typing import Optional

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class PointCloudWithImagesResource(CreateableInputAPIResource):
    def _create_inputs_point_cloud_with_images(self, point_clouds_with_images: IAM.PointCloudsWithImages,
                                               internal_id: str,
                                               metadata: IAM.CalibratedSceneMetaData,
                                               project: Optional[str],
                                               batch: Optional[str],
                                               input_list_id: Optional[int],
                                               dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """Create point cloud with images"""

        js = dict(
            files=point_clouds_with_images.to_dict(),
            internalId=internal_id,
            metadata=metadata.to_dict())

        return self.post_input_request('pointclouds-with-images', js, project=project, batch=batch,
                                       input_list_id=input_list_id, dryrun=dryrun)

    def create(self, folder: Path,
               point_clouds_with_images: IAM.PointCloudsWithImages,
               metadata: IAM.CalibratedSceneMetaData,
               project: Optional[str] = None,
               batch: Optional[str] = None,
               input_list_id: Optional[int] = None,
               dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Upload files and create an input of type 'point_cloud_with_image'.

        :param folder: path to folder containing files
        :param point_clouds_with_images: class containing images and pointclouds that constitute the input
        :param metadata: Class containing metadata necessary for point cloud with images
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
        input of type 'point_cloud_with_image' is created for the designated `project` `batch` or `input_list_id`.
        If the input_job fails (cannot perform conversion) the input is not added. To see if
        conversion was successful please see the method `get_input_jobs_status`.
        """

        files_on_disk = [image.filename for image in point_clouds_with_images.images] + \
                        [pc.filename for pc in point_clouds_with_images.point_clouds]

        upload_urls_response = self.get_upload_urls(IAM.FilesToUpload(files_on_disk))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_on_disk) == set(files_in_response)

        for image in point_clouds_with_images.images:
            image.set_images_dimensions(folder)

        self._create_inputs_point_cloud_with_images(point_clouds_with_images,
                                                    upload_urls_response.internal_id,
                                                    metadata,
                                                    project=project,
                                                    batch=batch,
                                                    input_list_id=input_list_id,
                                                    dryrun=True)
        if not dryrun:
            self.file_resource_client.upload_files(folder=folder, url_map=upload_urls_response.files_to_url)

            create_input_response = self._create_inputs_point_cloud_with_images(point_clouds_with_images,
                                                                                upload_urls_response.internal_id,
                                                                                metadata,
                                                                                project=project,
                                                                                batch=batch,
                                                                                input_list_id=input_list_id,
                                                                                )

            log.info(f"Creating inputs for files with job_id={create_input_response.internal_id}")
            return create_input_response