import json
from typing import Optional, List

import requests
from annotell.auth.authsession import DEFAULT_HOST as DEFAULT_AUTH_HOST, AuthSession

from . import __version__

DEFAULT_HOST = "https://api.annotell.com"


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
    def __init__(self, *,
                 auth=None,
                 host=DEFAULT_HOST,
                 auth_host=DEFAULT_AUTH_HOST):
        """
        :param auth: Annotell authentication credentials,
        see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: Annotell api host
        :param auth_host: authentication server host
        """
        self.host = host
        self.metadata_url = "%s/v1/search/metadata/query" % self.host

        self.oauth_session = AuthSession(auth=auth, host=auth_host)

    @property
    def session(self):
        return self.oauth_session.session

    def stream_metadata(self,
                        query_filter: str,
                        limit: Optional[int] = 10,
                        includes: Optional[List[str]] = None,
                        excludes: Optional[List[str]] = None):
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
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": "annotell-ams/query:%s" % __version__
        }

        params = {"stream": "true"}

        resp = self.session.post(
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
