from annotell.apiclients.input_api_client import create_input_api_client
from typing import Optional, List
from tabulate import tabulate
from .input_api_client import InputApiClient
from pprint import pprint

import click
import os

env = os.getenv("ANNOTELL_CLIENT_ORGANIZATION_ID", None)
if env:
    org_id = int(env)
    print("<" * 25,  f" Acting on behalf of organization {org_id}", 25 * ">")
else:
    org_id = None

client = InputApiClient(auth=None, client_organization_id=org_id)


def _tabulate(body, headers, title=None):
    tab = tabulate(
        body,
        headers=headers,
        tablefmt='fancy_grid',
    )
    if title:
        title_len = len(title)
        spacing = len(tab.split('\n')[0])

        roof = "=" * spacing
        floor = "=" * spacing

        left_multi = spacing // 2 - title_len // 2 - 1

        title_text_left = " " * left_multi + title
        title_text = title_text_left

        title_house = roof + '\n' + title_text + '\n' + floor
        tab = title_house + '\n' + tab
    return tab


def _get_table(sequence, headers, title=None):
    body = []
    for p in sequence:
        body.append([vars(p)[h] for h in headers])
    return _tabulate(body, headers, title)


@click.group()
def cli():
    """A CLI wrapper for Annotell utilities"""


@click.command()
@click.argument('project', nargs=1, default=None, required=False, type=str)
@click.option('--get-batches', is_flag=True)
def projects(project, get_batches):
    print()
    if project and get_batches:
        list_of_input_batches = client.get_project_batches(project)
        headers = ["external_id", "title", "status", "created", "updated"]
        tab = _get_table(list_of_input_batches, headers, "BATCHES")
        print(tab)
    elif project:
        list_of_projects = client.get_projects()
        target_project = [p for p in list_of_projects if p.external_id == project]
        headers = ["created", "title", "description", "status", "external_id"]
        tab = _get_table(target_project, headers, "PROJECTS")
        print(tab)
    else:
        list_of_projects = client.get_projects()
        headers = ["created", "title", "description", "status", "external_id"]
        tab = _get_table(list_of_projects, headers, "PROJECTS")
        print(tab)


@click.command()
@click.argument('project', nargs=1, default=None, required=True, type=str)
@click.option('--batch', nargs=1, default=None, required=False, type=str)
@click.option('--external-ids', required=False, multiple=True)
@click.option('--include-invalidated', required=False, is_flag=True)
@click.option("--view", is_flag=True)
def inputs(project, batch, external_ids, include_invalidated, view):
    print()
    if view:
        inputs = client.get_inputs(project, batch, external_ids=external_ids, include_invalidated=include_invalidated)
        view_dict = client.get_view_links([input.internal_id for input in inputs])
        body = []
        headers = ["internal_id", "view_link"]
        for internal_id, link in view_dict.items():
            body.append([
                internal_id, link
            ])
        tab = _tabulate(body, headers, title="VIEW LINKS FOR INPUTS")
        print(tab)
    else:
        inputs = client.get_inputs(project, batch, include_invalidated=include_invalidated)
        headers = ["internal_id",
                   "external_id",
                   "batch",
                   "input_type",
                   "status",
                   "error_message"]
        tab = _get_table(inputs, headers, "INPUTS")
        print(tab)


@click.command()
@click.argument('input_internal_id', nargs=1, required=True, type=str)
def view(input_internal_id):
    print()
    view_dict = client.get_view_links([input_internal_id])
    body = [[input_internal_id, view_dict[input_internal_id]]]
    headers = ["internal_id", "view_link"]
    tab = _tabulate(body, headers, title="VIEW LINK")
    print(tab)

@click.command()
@click.option('--id', nargs=1, default=None, required=False, type=int)
@click.option("--external-id", nargs=1, required=False, type=str)
@click.option('--raw', is_flag=True)
def calibration(id, external_id, raw):
    print()
    if id is not None:
        list_of_calibrations = client.get_calibration_data(id=id)
        headers = ["id", "external_id", "created"]
        tab = _get_table(list_of_calibrations, headers, "CALIBRATION")
        print(tab)
        if raw:
            print()
            [pprint(calib.calibration) for calib in list_of_calibrations]
    elif external_id is not None:
        list_of_calibrations = client.get_calibration_data(external_id=external_id)
        headers = ["id", "external_id", "created"]
        tab = _get_table(list_of_calibrations, headers, "CALIBRATION")
        print(tab)
    else:
        list_of_calibrations = client.get_calibration_data()
        headers = ["id", "external_id", "created"]
        tab = _get_table(list_of_calibrations, headers, "CALIBRATION")
        print(tab)


cli.add_command(projects)
cli.add_command(inputs)
cli.add_command(calibration)
cli.add_command(view)


def main():
    cli(prog_name="annoutil")
