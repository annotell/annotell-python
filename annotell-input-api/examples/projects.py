from annotell.input_api import model as IAM
from annotell.input_api.input_api_client import InputApiClient

print("Listing projects...")


# Instantiating Input API Client
client = InputApiClient()

projects = client.project.get_projects()

for project in projects:
    print(f"Project: {project.external_id}")
    batches = client.project.get_project_batches(project.external_id)

    print(", ".join([batch.external_id for batch in batches]))