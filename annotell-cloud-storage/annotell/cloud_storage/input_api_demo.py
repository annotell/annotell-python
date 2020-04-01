import os
import json
from pathlib import Path
import yaml

from input_api_client import InputApiClient
import input_api_model as IAM


def convert_calibration(path_to_target_yaml_file: str) -> dict:
    with open(path_to_target_yaml_file) as fd:
        original_calib = yaml.load(fd)

    sensors = original_calib["sensors"]
    new_calib = {}

    for cam in sensors["cameras"]:
        direction = cam["name"]
        new_calib[direction] = {
            "position": cam["position"],
            # cv2.Rodrigues(np.array(camera_rot))[0].tolist()
            "rotation_quaternion": cam["rotation_quaternion"],
            "camera_matrix": cam["camera_matrix"],  # Column order, [x1, y1, z1, x2, y2, ...]
            "distortion_coefficients": cam["distortion_coefficients"],
            "image_width":  cam["resolution"][0],
            "image_height": cam["resolution"][1],
            "camera_properties": {
                "camera_type": "pinhole"  # could also be "fisheye"
            },

        }

    # We only support a single LIDAR at the moment.
    lidar = sensors["lidars"][0]
    new_calib["lidar"] = {
        "position": lidar["position"],
        "rotation_quaternion": lidar["rotation_quaternion"]
    }

    keymap = {
        "FL1": "LF",
        "FL2": "LC",
        "FL3": "LB",
        "FR1": "RF",
        "FR2": "RC",
        "FR3": "RB",
        "F": "FC",
        "R": "BC"
    }

    new_sensor_calib_with_proper_keys = {}

    for (key, val) in new_calib.items():
        if key in keymap.keys():
            new_key = keymap[key]
        else:
            new_key = key
        new_sensor_calib_with_proper_keys[new_key] = new_calib[key]

    return new_sensor_calib_with_proper_keys


if __name__ == "__main__":
    api_token = "abfd14d7483fa72e81a9dbb1"
    client = InputApiClient(
        api_token=api_token
    )

    folder = Path("/Users/markocotra/input_api_demo")

    image = "india_1260003370120391_1575968152103699_FC.jpg"
    pointcloud = "india_1260003370120391.csv"

    files = IAM.FilesPointCloudWithImages(
        images=[image],
        pointclouds=[pointcloud]  # Only support 1 pointcloud
    )

    input_list_id = 256
    metadata = IAM.Metadata(
        external_id=f"{pointcloud.split('.')[0]}",
        source_specification=IAM.SourceSpecification(
            images_to_source={
                image: "FC"
            },
            source_to_pretty_name={
                "FC": "Front Camera"
            },
            source_order=["FC"]
        ),
        calibration_id=31827623
    )

    response = client.create_inputs_point_cloud_with_images(
        folder,
        files,
        input_list_id,
        metadata
    )
    print(response)
