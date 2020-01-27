import requests
import os
import json
from typing import Union
from . import __version__

default_host = "https://api.annotell.com"


def _iter_items(resp):
    # parse each line as a json document
    for item in resp.iter_lines():
        if item.startswith(b"{"):
            item = item if not item.endswith(b",") else item[:-1]
            yield json.loads(item)


class QueryResponse:
    def __init__(self, response):
        self.raw_response = response
        self.status_code = response.status_code

    def items(self):
        return _iter_items(self.raw_response)


class QueryException(RuntimeError):
    pass


class QueryClient:
    def __init__(self, host=default_host, token=None):
        self.host = host
        self.metadata_url = "%s/v1/search/metadata/query" % self.host
        self.token = token or os.getenv("ANNOTELL_API_TOKEN")

    def stream_metadata(self, query_filter: str, limit: Union[int, None]=10, includes=None, excludes=None):
        """
        Returns an iterator with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :return:
        """
        if excludes is None:
            excludes = []
        if includes is None:
            includes = []

        body = {
            "queryFilter": query_filter,
            "limit": limit,
            "fields": {
                "includes": includes,
                "excludes": excludes
            }
        }

        headers = {
            "Authorization": "Bearer %s" % self.token,
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": "annotell-ams/query:%s" % __version__
        }

        params = {"stream": "true"}

        resp = requests.post(
            url=self.metadata_url,
            params=params,
            json=body,
            headers=headers,
            stream=True)

        try:
            resp.raise_for_status()
            return QueryResponse(resp)
        except requests.exceptions.HTTPError as e:
            msg = resp.content.decode()
            raise QueryException("Got %s error %s" % (resp.status_code, msg)) from e
