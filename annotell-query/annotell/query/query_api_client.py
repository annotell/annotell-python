from typing import Optional, List, Mapping, Union

import requests
from annotell.auth.authsession import DEFAULT_HOST as DEFAULT_AUTH_HOST, AuthSession

from . import __version__
from .query_model import QueryResponse, StreamingQueryResponse, QueryException

DEFAULT_HOST = "https://query.annotell.com"

# placeholder, get the default limit from the server
DEFAULT_LIMIT = -1
MAX_LIMIT = 10000

FIELDS_TYPE = Union[List[str], str, None]
AGGREGATES_TYPE = Optional[Mapping[str, dict]]

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
            "User-Agent": "annotell-query/%s" % __version__
        }

    @property
    def session(self):
        return self.oauth_session.session

    def _create_request_body(self, *,
                             query_filter: Optional[str] = None,
                             limit: Optional[int] = DEFAULT_LIMIT,
                             includes: FIELDS_TYPE = None,
                             excludes: FIELDS_TYPE = None,
                             aggregates: AGGREGATES_TYPE = None):
        if excludes is None:
            excludes = []
        if includes is None:
            includes = []

        qf = "" if query_filter is None else query_filter

        body = {
            "queryFilter": qf,
            "fields": {
                "includes": includes,
                "excludes": excludes
            }
        }
        if limit is not None and limit != DEFAULT_LIMIT:
            body['limit'] = limit

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
        except requests.exceptions.ChunkedEncodingError as e:
            raise QueryException("Got unexpected content in the streaming response from the the server") from e

    def _query(self, url: str, stream: bool = False, **kwargs):

        aggs = kwargs.get("aggregates")
        if aggs and stream:
            raise ValueError("Cannot use aggregates in streaming mode")

        limit = kwargs.get("limit")
        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError("Limit must be int")

            if not stream and limit > MAX_LIMIT:
                raise ValueError(f"Use stream to get more than {MAX_LIMIT} items")

        body = self._create_request_body(**kwargs)

        params = {"stream": "true"} if stream else None

        resp = self.session.post(
            url=url,
            json=body,
            headers=self.headers,
            params=params,
            stream=stream
        )
        r = self._return_request_resp(resp)
        return StreamingQueryResponse(r) if stream else QueryResponse(r)

    def query_metadata(self,
                       query_filter: Optional[str] = None,
                       limit: Optional[int] = DEFAULT_LIMIT,
                       includes: FIELDS_TYPE = None,
                       excludes: FIELDS_TYPE = None,
                       aggregates: AGGREGATES_TYPE = None,
                       stream: bool = False):
        """
        Returns a QueryResponse or StreamingQueryResponse with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :param stream, use stream if you want to get more than 10000 items
        :return:
        """
        return self._query(self.metadata_url, stream,
                           query_filter=query_filter,
                           limit=limit,
                           includes=includes,
                           excludes=excludes,
                           aggregates=aggregates)

    def query_kpi_data_entries(self,
                               query_filter: Optional[str] = None,
                               limit: Optional[int] = DEFAULT_LIMIT,
                               includes: FIELDS_TYPE = None,
                               excludes: FIELDS_TYPE = None,
                               aggregates: AGGREGATES_TYPE = None,
                               stream: bool = False):
        """
        Returns a QueryResponse or StreamingQueryResponse with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :param aggregates: dict
        :param stream, use stream if you want to get more than 10000 items
        :return:
        """
        return self._query(self.kpi_query_url,
                           query_filter=query_filter,
                           limit=limit,
                           includes=includes,
                           excludes=excludes,
                           aggregates=aggregates,
                           stream=stream)

    def query_judgements(self,
                         query_filter: Optional[str] = None,
                         limit: Optional[int] = DEFAULT_LIMIT,
                         includes: FIELDS_TYPE = None,
                         excludes: FIELDS_TYPE = None,
                         aggregates: AGGREGATES_TYPE = None,
                         stream: bool = False):
        """
        Returns a QueryResponse or StreamingQueryResponse with result items
        :param query_filter:
        :param limit: set to None for no limit
        :param excludes: list
        :param includes: list
        :param aggregates: dict
        :param stream, use stream if you want to get more than 10000 items
        :return:
        """
        return self._query(self.judgements_query_url,
                           query_filter=query_filter,
                           limit=limit,
                           includes=includes,
                           excludes=excludes,
                           aggregates=aggregates,
                           stream=stream)
