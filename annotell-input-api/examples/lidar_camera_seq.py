from __future__ import absolute_import

import annotell.input_api.input_api_client as IAC
import annotell.input_api.model as IAM
from annotell.input_api.logger import setup_logging

from calibration import create_calibration_spec

print("Creating Lidar and Camera Sequence Input...")

setup_logging(level="INFO")

client = IAC.InputApiClient()


# Create calibration
calibration_spec = create_calibration_spec("Collection 2020-06-16", ["RFL01"], ["RFC01", "RFC02", "RFC03"])
created_calibration = client.calibration.create_calibration_data(calibration_spec)

lidar_and_camera_seq = IAM.LidarsAndCamerasSequence(
    external_id="input1",
    frames=[
        IAM.Frame(
            frame_id="1",
            relative_timestamp=0,
            lidar_frames=[
                IAM.LidarFrame("~/Downloads/lidar_RFL01.pcd", sensor_name="RFL01"),
            ],
            image_frames=[
                IAM.ImageFrame("~/Downloads/img_RFC01.jpg", sensor_name="RFC01"),
                IAM.ImageFrame("~/Downloads/img_RFC01.jpg", sensor_name="RFC02"),
                IAM.ImageFrame("~/Downloads/img_RFC01.jpg", sensor_name="RFC03")
            ]),
    ],
    calibration_id=created_calibration.id,
)


# Project - Available via `client.list_projects()`
project = "<project-identifier>"


# Add input
client.LidarAndImageSequence.create(lidar_and_camera_seq,
                                    project=project,
                                    dryrun=True)
