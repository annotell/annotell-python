from typing import Optional, List, Mapping

import requests
from annotell.auth.authsession import DEFAULT_HOST as DEFAULT_AUTH_HOST, AuthSession

from . import __version__
from .query_model import QueryResponse, StreamingQueryResponse, QueryException

DEFAULT_HOST = "https://query.annotell.com"
DEFAULT_LIMIT = 10


class QueryApiClient:
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
        self.judgements_query_url = "%s/v1/search/judgements/query" % self.host
        self.kpi_query_url = "%s/v1/search/kpi/query" % self.host

        self.oauth_session = AuthSession(auth=auth, host=auth_host)

        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": "annotell-ams/query:%s" % __version__
        }

    @property
    def session(self):
        return self.oauth_session.session

    def _create_request_body(self, *,
                             query_filter: Optional[str] = None,
                             limit: Optional[int] = DEFAULT_LIMIT,
                             includes: Optional[List[str]] = None,
                             excludes: Optional[List[str]] = None,
                             aggregates: Mapping[str, dict] = dict()):
        if excludes is None:
            excludes = []
        if includes is None:
            includes = []

        qf = "" if query_filter is None else query_filter

        body = {
            "queryFilter": qf,
            "limit": limit,
            "fields": {
                "includes": includes,
                "excludes": excludes
            }
        }

        if aggregates:
            body['aggregates'] = aggregates

        return body

    def _return_request_resp(self, resp):
        try:
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            msg = resp.content.decode()
            raise QueryException("Got %s error %s" % (resp.status_code, msg)) from e

    def _stream_query(self, url: str, **kwargs):
        body = self._create_request_body(**kwargs)

        params = {"stream": "true"}

        resp = self.session.post(
            url=url,
            params=params,
            json=body,
            headers=self.headers,
            stream=True)
        return StreamingQueryResponse(self._return_request_resp(resp))

    def _query(self, url: str, **kwargs):
        body = self._create_request_body(**kwargs)
        resp = self.session.post(url=url, json=body, headers=self.headers)
        return QueryResponse(self._return_request_resp(resp))

    def stream_metadata(self,
                        query_filter: Optional[str] = None,
                        limit: Optional[int] = 10,
                        includes: Optional[List[str]] = None,
                        excludes: Optional[List[str]] = None):
        """
        Returns a StreamingQueryResponse with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :return:
        """

        return self._stream_query(self.metadata_url,
                                  query_filter=query_filter,
                                  limit=limit,
                                  includes=includes,
                                  excludes=excludes)

    def query_kpi_data_entries(self,
                               query_filter: Optional[str] = None,
                               limit: Optional[int] = DEFAULT_LIMIT,
                               includes: Optional[List[str]] = None,
                               excludes: Optional[List[str]] = None,
                               aggregates: Mapping[str, dict] = dict()):
        """
        Returns a QueryResponse with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :param aggregates: dict
        :return:
        """
        return self._query(self.kpi_query_url,
                           query_filter=query_filter,
                           limit=limit,
                           includes=includes,
                           excludes=excludes,
                           aggregates=aggregates)
