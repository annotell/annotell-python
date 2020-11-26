from typing import List

import annotell.input_api.input_api_model as IAM
import annotell.input_api.model.calibration as Calibration
from annotell.input_api.input_api_client import InputApiClient


def create_calibration_spec(external_id, lidar_sources: List[str], camera_sources: List[str]):

    # Create lidar calibration
    def unity_lidar_calibration():
        lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
        lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        return Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                    rotation_quaternion=lidar_rotation)
    # Create a camera calibration

    def unity_camera_calibration():
        camera_camera_type = Calibration.CameraType.PINHOLE
        camera_position = Calibration.Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
        camera_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
        camera_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
        camera_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
        camera_properties = Calibration.CameraProperty(camera_type=camera_camera_type)
        return Calibration.CameraCalibrationExplicit(position=camera_position,
                                                     rotation_quaternion=camera_rotation,
                                                     camera_matrix=camera_camera_matrix,
                                                     distortion_coefficients=camera_distortion_coefficients,
                                                     camera_properties=camera_properties,
                                                     image_height=920,
                                                     image_width=1244)

    # Create calibration for the scene
    calibration_dict = {**{lidar_source: unity_lidar_calibration() for lidar_source in lidar_sources},
                        **{camera_source: unity_camera_calibration() for camera_source in camera_sources}
                        }
    calibration = IAM.Calibration(calibration_dict=calibration_dict)
    calibration_external_id = external_id
    calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                           calibration=calibration)

    return calibration_spec


if __name__ == "__main__":
    print("Creating Calibration...")

    client = InputApiClient()

    calibration = create_calibration_spec("2020-06-16", ["lidar"], ["RFC01"])

    # Create the calibration using the inputApi client
    created_calibration = client.create_calibration_data(calibration_spec=calibration)
