from annotell.input_api.input_api_client import InputApiClient
from annotell.input_api import input_api_model as IAM
from pathlib import Path

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

client.upload_and_create_images_input_job(folder=folder,
                                          images_files=images_files,
                                          project=project,
                                          dryrun=True) # Dry run will not generate inputs
