import logging
from typing import List, Optional

from .abstract_models import SensorCalibration
from .calibration import CameraProperty
from .enums import CameraType

log = logging.getLogger(__name__)


class CameraCalibration(SensorCalibration):
    def __init__(self, position: List[float], rotation_quaternion: List[float],
                 camera_matrix: List[float], camera_properties: CameraProperty,
                 distortion_coefficients: List[float], image_height: int, image_width: int,
                 undistortion_coefficients: Optional[List[float]]):

        self.position = position
        self.rotation_quaternion = rotation_quaternion

        self.camera_matrix = camera_matrix
        self.camera_properties = camera_properties
        self.distortion_coefficients = distortion_coefficients
        self.image_height = image_height
        self.image_width = image_width
        self.undistortion_coefficients = undistortion_coefficients

        assert(len(position) == 3)
        assert(len(rotation_quaternion) == 4)
        assert(len(camera_matrix) == 9)

        if camera_properties.camera_type == CameraType.KANNALA:
            assert(undistortion_coefficients is not None)
            assert(len(distortion_coefficients) == 4 and len(undistortion_coefficients) == 4)
        else:
            assert(len(distortion_coefficients) == 5)

        log.warning(f"DEPRECATED: Use the new, explicit camera calibration model CameraCalibrationExplicit.")  # noqa:E501

    def to_dict(self):
        base = {
            "position": self.position,
            "rotation_quaternion": self.rotation_quaternion,
            "camera_matrix": self.camera_matrix,
            "camera_properties": self.camera_properties.to_dict(),
            "distortion_coefficients": self.distortion_coefficients,
            "image_height": self.image_height,
            "image_width": self.image_width
        }

        if self.undistortion_coefficients is not None:
            base["undistortion_coefficients"] = self.undistortion_coefficients

        return base


class LidarCalibration(SensorCalibration):
    def __init__(self, position: List[float], rotation_quaternion: List[float]):
        self.position = position
        self.rotation_quaternion = rotation_quaternion

        assert(len(position) == 3)
        assert(len(rotation_quaternion) == 4)
        log.warning(f"DEPRECATED: Use the new, explicit lidar calibration model LidarCalibrationExplicit.")  # noqa:E501

    def to_dict(self):
        return {
            "position": self.position,
            "rotation_quaternion": self.rotation_quaternion
        }
