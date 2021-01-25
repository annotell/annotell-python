from annotell.input_api import model as IAM
from annotell.input_api.input_api_client import InputApiClient

print("Listing inputs...")


# Project - Available via `client.list_projects()`
project = "b8f2c092-fc84-4407-b20e-4df9712cc736"

# Instantiating Input API Client
client = InputApiClient()

inputs = client.input.get_inputs(project)