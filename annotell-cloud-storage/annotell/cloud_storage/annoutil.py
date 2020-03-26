from input_api_client import InputApiClient
from typing import Optional, List
from tabulate import tabulate

import click


c = InputApiClient(
    host="http://annotell.org:8010",
    api_token="DEF",
    auth_host="http://annotell.org:8001"
)


def get_table(sequence, headers):
    body = []
    for p in sequence:
        body.append([vars(p)[h] for h in headers])

    tab = tabulate(
        body,
        headers=headers,
        tablefmt='orgtbl',
    )
    return tab


@click.group()
def cli():
    """A CLI wrapper for Annotell utilities"""


@click.command()
def projects():
    list_of_projects = c.list_projects()
    headers = ["id", "created", "title", "description", "deadline", "status"]
    tab = get_table(list_of_projects, headers)
    print()
    print(tab)


cli.add_command(projects)


@click.argument('project_id', nargs=1, required=True)
@click.command()
def inputlists(project_id: int):
    list_of_input_lists = c.list_input_lists(project_id)
    headers = ["id", "project_id", "name", "created"]
    tab = get_table(list_of_input_lists, headers)
    print()
    print(tab)


cli.add_command(inputlists)


@click.option('--id', help='id for a specific calibration')
@click.option('--external_id', help='external_id for a specific calibration')
@click.command()
def calibrationdata(id: Optional[int], external_id: Optional[str]):
    list_of_calibrations = c.get_calibration_data(id, external_id)

    print()
    if id:
        headers = ["id", "external_id", "created"]
        tab = get_table(list_of_calibrations, headers)
        print(tab)
        print()
        [print(calib.calibration) for calib in list_of_calibrations]
    elif external_id:
        headers = ["id", "external_id", "created"]
        tab = get_table(list_of_calibrations, headers)
        print(tab)
    else:
        headers = ["id", "external_id", "created"]
        tab = get_table(list_of_calibrations, headers)
        print(tab)


cli.add_command(calibrationdata)


@click.argument('request_ids', nargs=-1, default=None)
@click.argument('input_list_id', nargs=-1, default=None)
@click.command()
def requests(request_ids: List[int], input_list_id: int):
    pass


def inputlists(internal_ids: List[str]):
    pass

def inputstatus(internal_ids: List[str]):
    pass

def download(internal_ids: List[str], request_id: Optional[int]):
    pass




if __name__ == '__main__':
    cli(prog_name="annoutil")
