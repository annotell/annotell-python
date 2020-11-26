from dataclasses import dataclass
from typing import List, Dict, Optional
from .abstract_models import RequestCall, SensorCalibration
from .enums import CameraType


@dataclass
class RotationQuaternion(RequestCall):
    w: float
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict:
        return self.__dict__


@dataclass
class Position(RequestCall):
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict:
        return self.__dict__


@dataclass
class CameraMatrix(RequestCall):
    fx: float
    fy: float
    cx: float
    cy: float

    def to_dict(self) -> Dict:
        return self.__dict__


@dataclass
class DistortionCoefficients(RequestCall):
    k1: float
    k2: float
    p1: float
    p2: float
    k3: Optional[float] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def validate(self, camera_type: CameraType):
        if camera_type == CameraType.KANNALA:
            assert(self.k3 is None)
        else:
            assert(self.k3 is not None)


@dataclass
class UndistortionCoefficients(RequestCall):
    l1: float
    l2: float
    l3: float
    l4: float

    def to_dict(self) -> Dict:
        return self.__dict__


@dataclass
class CameraProperty(RequestCall):
    camera_type: CameraType

    def to_dict(self):
        return {
            "camera_type": self.camera_type
        }

    def get_camera_type(self) -> CameraType:
        return self.camera_type


@dataclass
class LidarCalibrationExplicit(SensorCalibration):
    position: Position
    rotation_quaternion: RotationQuaternion

    def to_dict(self) -> Dict:
        return {
            "position": self.position.to_dict(),
            "rotation_quaternion": self.rotation_quaternion.to_dict()
        }


@dataclass
class CameraCalibrationExplicit(SensorCalibration):
    position: Position
    rotation_quaternion: RotationQuaternion
    camera_matrix: CameraMatrix
    distortion_coefficients: DistortionCoefficients
    camera_properties: CameraProperty
    image_height: int
    image_width: int
    undistortion_coefficients: Optional[UndistortionCoefficients] = None

    def __post_init__(self):
        camera_type = self.camera_properties.get_camera_type()
        self.distortion_coefficients.validate(camera_type=camera_type)
        if camera_type == CameraType.KANNALA:
            assert (self.undistortion_coefficients is not None)

    def to_dict(self) -> Dict:
        base = {
            "position": self.position.to_dict(),
            "rotation_quaternion": self.rotation_quaternion.to_dict(),
            "camera_matrix": self.camera_matrix.to_dict(),
            "camera_properties": self.camera_properties.to_dict(),
            "distortion_coefficients": self.distortion_coefficients.to_dict(),
            "image_height": self.image_height,
            "image_width": self.image_width
        }
        if self.undistortion_coefficients is not None:
            base["undistortion_coefficients"] = self.undistortion_coefficients.to_dict()

        return base
