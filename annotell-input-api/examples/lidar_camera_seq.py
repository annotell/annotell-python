import annotell.input_api.model as IAM
import annotell.input_api.model.calibration as Calibration
import annotell.input_api.input_api_client as IAC

from .calibration import create_calibration_spec

from pathlib import Path

print("Creating Lidar and Camera Sequence Input...")

client = IAC.InputApiClient()

# Create calibration
calibration_spec = create_calibration_spec("Collection 2020-06-16", ["lidar"], ["RFC01"])
created_calibration = client.calibration.create_calibration_data(calibration_spec)

lidar_and_camera_seq = IAM.LidarsAndCamerasSequence(
    external_id="input1",
    frames=[
        IAM.Frame("1", 0, lidar_frames=[
            IAM.LidarFrame("lidar_RFL01.pcd", "lidar.pcd", "RFL01"),
            IAM.LidarFrame("lidar_RFL02.pcd", "lidar.pcd", "RFL02"),
            IAM.LidarFrame("lidar_RFL03.pcd", "lidar.pcd", "RFL03")
        ],
            image_frames=[
            IAM.ImageFrame("lidar_RFC01.png", "lidar.png", "RFC01"),
            IAM.ImageFrame("lidar_RFC02.png", "lidar.png", "RFC02"),
            IAM.ImageFrame("lidar_RFC03.png", "lidar.png", "RFC03")
        ]),
    ],
    calibration_id=created_calibration.id,
    internal_id="123"
)


# Project - Available via `client.list_projects()`
project = "<project-identifier>"


# Add input
client.LidarAndImageSequence.create(lidar_and_camera_seq,
                                    project=project,
                                    dryrun=True)
