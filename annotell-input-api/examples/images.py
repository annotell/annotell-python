from pathlib import Path

from annotell.input_api import model as IAM
from annotell.input_api.input_api_client import InputApiClient

print("Creating Images Input...")


# Creating Image Object
image1 = "filename1.jpg"
image1_source = "CAM1"
image2 = "filename1.jpg"
image2_source = "CAM2"
images = [
    IAM.Image(filename=image1, source=image1_source),
    IAM.Image(filename=image2, source=image2_source)
]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")

# Optional metadata

source_specification = IAM.SourceSpecification(
    # Name to be displayed within app
    source_to_pretty_name=dict(
        image1_source="Left Camera",
        image2_source="Right Camera"
    ),
    # Order to display sources during annotation
    source_order=[image1_source, image2_source]
)
metadata = IAM.SceneMetaData(external_id="2020-06-16",
                             source_specification=source_specification)

# Project - Available via `client.list_projects()`
project = "<project-identifier>"

# Instantiating Input API Client
client = InputApiClient()

client.Images.create(folder=folder,
                     images_files=images_files,
                     metadata=metadata,
                     project=project,
                     dryrun=True)  # Dryrun will not generate inputs
