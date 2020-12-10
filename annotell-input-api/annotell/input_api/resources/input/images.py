import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4 as uuid

from annotell.input_api import model as IAM
from annotell.input_api.resources.abstract import CreateableInputAPIResource

log = logging.getLogger(__name__)


class ImageResource(CreateableInputAPIResource):
    def create(self, folder: Path,
               images_files: IAM.ImagesFiles,
               metadata: IAM.SceneMetaData = IAM.SceneMetaData(external_id=str(uuid())),
               project: Optional[str] = None,
               batch: Optional[str] = None,
               input_list_id: Optional[int] = None,
               dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Verifies the images and metadata given and then uploads images to Google Cloud Storage and
        creates an input job.
        :param folder: Absolute path to directory containing all images.
        :param images_files: List containing all images for the input.
        :param metadata: class containing metadata necessary for creating input from images.
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param input_list_id: input list to add input to (alternative to project-batch)
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns InputJobCreatedMessage: Class containing id of the created input job, or None if dryrun.
        """

        for image in images_files.images:
            image.set_images_dimensions(folder)

        filenames = [image.filename for image in images_files.images]
        upload_url_resp = self.get_upload_urls(IAM.FilesToUpload(filenames))

        internal_id = upload_url_resp.internal_id
        self._create_images_input_job(images_files=images_files,
                                      metadata=metadata,
                                      internal_id=internal_id,
                                      project=project,
                                      batch=batch,
                                      input_list_id=input_list_id,
                                      dryrun=True)

        files_in_response = upload_url_resp.files_to_url.keys()
        assert set(filenames) == set(files_in_response)

        if not dryrun:
            self.file_resource_client.upload_files(folder=folder, url_map=upload_url_resp.files_to_url)
            input_job_created_message = self._create_images_input_job(images_files=images_files,
                                                                      metadata=metadata,
                                                                      internal_id=internal_id,
                                                                      project=project,
                                                                      batch=batch,
                                                                      input_list_id=input_list_id
                                                                      )
            log.info(f"Creating input for images with internal_id={input_job_created_message.internal_id}")
            return input_job_created_message

    def _create_images_input_job(self, images_files: IAM.ImagesFiles,
                                 metadata: IAM.SceneMetaData,
                                 internal_id: str,
                                 project: Optional[str],
                                 batch: Optional[str],
                                 input_list_id: Optional[int],
                                 dryrun: bool = False) -> Optional[IAM.CreateInputJobResponse]:
        """
        Creates an input job for an image input

        :param images_files: Contains all images, with their dimensions
        :param metadata: Contains necessary metadata in order to create and validate inputs
        :param input_list_id: input list id which the new input will be added to
        :param internal_id: When created, the input will use this internal id.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :returns CreateInputJobResponse: Class containing id of the created input job, or None if dryrun
        """

        create_input_job_json = dict(files=images_files.to_dict(),
                                     metadata=metadata.to_dict(),
                                     internalId=internal_id)

        return self.post_input_request('images', create_input_job_json, project=project, batch=batch,
                                       input_list_id=input_list_id, dryrun=dryrun)
