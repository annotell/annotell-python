from annotell.input_api.input_api_client import InputApiClient
from annotell.input_api import model as IAM
from pathlib import Path

print("Creating Point Cloud Input...")


# Creating Point Cloud Object
# Support for .csv, .pcd or .las
pointcloud_file = "filename1.csv"
pointclouds = IAM.PointCloudFiles([IAM.PointCloud(filename=pointcloud_file)])
folder = Path("/home/user_name/example_path")

# Project - Available via `client.list_projects()`
project = "0edb8f59-a8ea-4c9b-aebb-a3caaa6f2ba3"

# Instantiating Input API Client
client = InputApiClient()

client.point_cloud.create(folder=folder,
                          point_clouds=pointclouds,
                          project=project,
                          )  # Dry run will not generate inputs
