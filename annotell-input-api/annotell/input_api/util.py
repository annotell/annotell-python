"""Utility functions for Input API """

from datetime import datetime
import mimetypes
import dateutil.parser


def ts_to_dt(date_string: str) -> datetime:
    """
    Parse string datetime into datetime
    """
    return dateutil.parser.parse(date_string)


def get_content_type(filename: str) -> str:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
    if filename.split(".")[-1] == "csv":
        content_type = "text/csv"
    else:
        content_type = mimetypes.guess_type(filename)[0]
        content_type = content_type if content_type is not None else 'application/octet-stream'

    return content_type
