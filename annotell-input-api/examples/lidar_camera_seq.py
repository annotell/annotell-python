from __future__ import absolute_import

import annotell.input_api.input_api_client as IAC
import annotell.input_api.model as IAM
from annotell.input_api.logger import setup_logging

from calibration import create_calibration_spec

print("Creating Lidar and Camera Sequence Input...")

setup_logging(level="INFO")

client = IAC.InputApiClient()

# Create calibration
calibration_spec = create_calibration_spec("Collection 2020-06-16", ["lidar"], ["RFC01"])
created_calibration = client.calibration.create_calibration_data(calibration_spec)

lidar_and_camera_seq = IAM.LidarsAndCamerasSequence(
    external_id="input1",
    frames=[
        IAM.Frame("1", 0, lidar_frames=[
            IAM.LidarFrame("lidar_RFL01.pcd", sensor_name="RFL01"),
            IAM.LidarFrame("lidar_RFL02.pcd", sensor_name="RFL02"),
            IAM.LidarFrame("lidar_RFL03.pcd", sensor_name="RFL03")
        ],
            image_frames=[
            IAM.ImageFrame("lidar_RFC01.png", sensor_name="RFC01"),
            IAM.ImageFrame("lidar_RFC02.png", sensor_name="RFC02"),
            IAM.ImageFrame("lidar_RFC03.png", sensor_name="RFC03")
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
