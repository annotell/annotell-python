import annotell.input_api.input_api_model as IAM
import annotell.input_api.model.calibration as Calibration
import annotell.input_api.input_api_client as IAC

from .calibration import create_calibration_spec

from pathlib import Path

print("Creating Point Cloud Input...")

client = IAC.InputApiClient()
# Create representation of images and point clouds + source specification images
image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is

# Create calibration
calibration_spec = create_calibration_spec("Collection 2020-06-16", ["lidar"], ["RFC01"])
created_calibration = client.create_calibration_data(calibration_spec)

# Create metadata
scene_external_id = "Scene X collection 2020-06-16"
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       calibration_id=created_calibration.id)

# Project - Available via `client.list_projects()`
project = "<project-identifier>"

# Add input                                       
client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project=project)