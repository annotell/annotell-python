"""Client for communicating with the Annotell platform."""
import logging

from annotell.auth.authsession import DEFAULT_HOST as DEFAULT_AUTH_HOST

from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.resources.annotation.annotation import AnnotationResource
from annotell.input_api.resources.calibration.calibration import CalibrationResource
from annotell.input_api.resources.input.images import ImageResource
from annotell.input_api.resources.input.input import InputResource
from annotell.input_api.resources.input.lidar_camera_sequence import LidarAndImageSequenceResource
from annotell.input_api.resources.input.point_cloud import PointCloudResource
from annotell.input_api.resources.input.point_cloud_images import PointCloudWithImagesResource
from annotell.input_api.resources.project.project import ProjectResource

DEFAULT_HOST = "https://input.annotell.com"

log = logging.getLogger(__name__)


class InputApiClient:
    """Creates Annotell inputs from local files."""

    def __init__(self, *,
                 auth=None,
                 host: str = DEFAULT_HOST,
                 auth_host: str = DEFAULT_AUTH_HOST,
                 client_organization_id: int = None,
                 max_upload_retry_attempts: int = 23,
                 max_upload_retry_wait_time: int = 60):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id. Only works with an Annotell user.
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """

        client = HttpClient(auth=auth,
                            host=host,
                            auth_host=auth_host,
                            client_organization_id=client_organization_id)
        file_client = FileResourceClient(max_upload_retry_attempts=max_upload_retry_attempts,
                                         max_upload_retry_wait_time=max_upload_retry_wait_time)

        self.calibration = CalibrationResource(client)
        self.project = ProjectResource(client)
        self.annotation = AnnotationResource(client)
        self.input = InputResource(client)

        # Only expose v1 inputs
        # self.point_cloud = PointCloudResource(client, file_client)
        # self.point_cloud_with_images = PointCloudWithImagesResource(client, file_client)
        # self.images = ImageResource(client, file_client)

        self.lidar_and_image_sequence = LidarAndImageSequenceResource(client, file_client)
