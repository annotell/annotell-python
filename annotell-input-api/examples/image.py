from pathlib import Path

from annotell.input_api import model as IAM
from annotell.input_api.input_api_client import InputApiClient

print("Creating Image Input...")


# Creating Image Object
image1 = "filename1.jpg"
image = IAM.Image(filename=image1)
images_files = IAM.ImagesFiles([image])
folder = Path("/home/user_name/example_path")

# Project - Available via `client.list_projects()`
project = "<project-identifier>"

# Instantiating Input API Client
client = InputApiClient()

client.Images.create(folder=folder,
                     images_files=images_files,
                     project=project,
                     dryrun=True)  # Dry run will not generate inputs
