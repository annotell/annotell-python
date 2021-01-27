"""Utility functions for Input API """

import mimetypes
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from PIL import Image as PILImage
from typing import List, Dict

import dateutil.parser
from urllib3.util import Url, parse_url

GCS_SCHEME = "gs"


def ts_to_dt(date_string: str) -> datetime:
    """
    Parse string datetime into datetime
    """
    return dateutil.parser.parse(date_string)


def filter_none(js: dict) -> dict:
    if isinstance(js, Mapping):
        return {k: filter_none(v) for k, v in js.items() if v is not None}
    else:
        return js


def get_content_type(filename: str) -> str:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
    if filename.split(".")[-1] == "csv":
        content_type = "text/csv"
    else:
        content_type = mimetypes.guess_type(filename)[0]
        content_type = content_type if content_type is not None else 'application/octet-stream'

    return content_type


def get_resource_id(signed_url: str) -> str:
    url = parse_url(signed_url)
    resource_id = Url(scheme=GCS_SCHEME, path=url.path)
    return str(resource_id).replace("///", "//")


def get_image_dimensions(image_path: str) -> dict:
    fi = Path(image_path).expanduser()
    with PILImage.open(fi) as im:
        width, height = im.size
        return {"width": width, "height": height}

def get_view_links(internal_ids: List[str]) -> Dict[str, str]:
        """
        For each given internal id returns an URL where the input can be viewed in the web app.

        :param internal_ids: List with internal ids
        :return Dict: Dictionary mapping each internal id with an URL to view the input.
        """
        view_dict = dict()
        for internal_id in internal_ids:
            view_dict[internal_id] = f"https://app.annotell.com/input-view/{internal_id}"

        return view_dict
