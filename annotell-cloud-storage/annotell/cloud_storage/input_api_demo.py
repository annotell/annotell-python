import os
import json
from pathlib import Path
import yaml

from input_api_client import InputApiClient


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
                "camera_type": "pinhole"
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
    c = InputApiClient(
        api_token=api_token
    )

    folder = Path("/Users/markocotra/input_api_demo")
    image = "india_1260002498938491_1575967280926345_FC.jpg"
    pointcloud = "india_1260002498938491.csv"

    files = dict(
        images=[image],
        pointclouds=[pointcloud]  # currently only supports 1 lidar file
    )

    """
    calibration_file = "sensor_setup_191210_191215.yaml"
    path_to_calibration_yaml_file = os.path.join(folder, calibration_file)
    calibration = convert_calibration(path_to_calibration_yaml_file)
    """

    input_list_id = 256

    scene_metadata = {
        "externalId": f"{pointcloud.split('.')[0]}",
        "sourceSpecification": {
            "imagesToSource": {
                image: "FC"
            },
            "sourceToPrettyName": {
                "FC": "Front Camera"
            },
            "sourceOrder": ["FC"]
        },
        "calibrationId": 31827623
    }

    """
    "calibrationSpec": {
        "externalId": f"{calibration_file.split('.')[0]}",
        "calibration": calibration
    }
    """
    print()
    print("create_inputs_point_cloud_with_images")
    resp = c.create_inputs_point_cloud_with_images(folder, files, input_list_id, scene_metadata)
    print(resp)
