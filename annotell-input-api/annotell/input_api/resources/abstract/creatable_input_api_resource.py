from typing import Optional

import logging

from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.model import (CameraSettings, CreateInputJobResponse, FilesToUpload,
                                      UploadUrlsResponse, SceneInput, SensorSpecification)
from annotell.input_api.util import get_resource_id, get_image_dimensions

log = logging.getLogger("annotell.input_api")

class CreateableInputAPIResource(FileResourceClient):

    def __init__(self, client: HttpClient, file_resource_client: FileResourceClient):
        super().__init__()
        self.client = client
        self.file_resource_client = file_resource_client

    @staticmethod
    def _set_resource_id(scene_input: SceneInput,
                         upload_urls_response: UploadUrlsResponse):

        resources = scene_input.get_local_resources()
        for resource in resources:
            if resource.resource_id is None:
                resource.resource_id = get_resource_id(upload_urls_response.files_to_url[resource.filename])

    @staticmethod
    def _set_sensor_settings(scene_input: SceneInput):
        def _create_camera_settings(width_height_dict: dict):
            return CameraSettings(width_height_dict['width'], width_height_dict['height'])

        def _create_sensor_settings():
            first_frame = scene_input.frames[0]
            return {
                image_frame.sensor_name: _create_camera_settings(get_image_dimensions(image_frame.filename)) for image_frame in first_frame.image_frames
            }
            
        if scene_input.sensor_specification is None:
            scene_input.sensor_specification = SensorSpecification(sensor_settings=_create_sensor_settings())
        elif scene_input.sensor_specification.sensor_settings is None:
            scene_input.sensor_specification.sensor_settings = _create_sensor_settings()

    def _get_files_to_upload(self, scene_input: SceneInput) -> UploadUrlsResponse:
        resources = scene_input.get_local_resources()
        files_to_upload = list(map(lambda res: res.filename, resources))
        upload_urls_response = self.get_upload_urls(FilesToUpload(files_to_upload))

        files_in_response = list(upload_urls_response.files_to_url.keys())
        assert set(files_to_upload) == set(files_in_response)

        return upload_urls_response

    def _create(self,
               scene_input: SceneInput,
               project: Optional[str] = None,
               batch: Optional[str] = None,
               input_list_id: Optional[int] = None,
               dryrun: bool = False):
        upload_urls_response = self._get_files_to_upload(scene_input)
        self._set_resource_id(scene_input, upload_urls_response)
        self._set_sensor_settings(scene_input)

        # We need to set job-id from the response
        payload = scene_input.to_dict()
        payload['internalId'] = upload_urls_response.internal_id

        self.post_input_request(scene_input.path(), payload,
                                project=project,
                                batch=batch,
                                input_list_id=input_list_id,
                                dryrun=True)

        if dryrun:
            return

        self.file_resource_client.upload_files(upload_urls_response.files_to_url)

        create_input_response = self.post_input_request(
            scene_input.path(),
            payload,
            project=project,
            batch=batch,
            input_list_id=input_list_id,
            dryrun=False
        )

        log.info(f"Created inputs for files with job_id={create_input_response.internal_id}")
        return create_input_response

    def post_input_request(self, resource_path: str,
                           input_request: dict,
                           project: Optional[str],
                           batch: Optional[str],
                           input_list_id: Optional[int],
                           dryrun: bool = False) -> Optional[CreateInputJobResponse]:
        """
        Send input to Input API. if not dryrun is true, only validation is performed
        Otherwise, returns `CreateInputJobResponse`
        """
        if input_list_id is not None:
            input_request['inputListId'] = input_list_id
        
        log.debug("POST:ing to %s input %s", resource_path, input_request)

        request_url = self._resolve_request_url(resource_path, project, batch)
        json_resp = self.client.post(request_url, json=input_request, dryrun=dryrun)
        if not dryrun:
            return CreateInputJobResponse.from_json(json_resp)

    @staticmethod
    def _resolve_request_url(resource_path: str,
                             project: Optional[str] = None,
                             batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = f"v1/inputs/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path

        return url

    def get_upload_urls(self, files_to_upload: FilesToUpload) -> UploadUrlsResponse:
        """Get upload urls to cloud storage"""
        json_resp = self.client.get("v1/inputs/upload-urls", json=files_to_upload.to_dict())
        return UploadUrlsResponse.from_json(json_resp)
