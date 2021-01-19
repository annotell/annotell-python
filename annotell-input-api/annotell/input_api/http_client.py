"""Client for communicating with the Annotell platform."""
import logging

import requests
from annotell.auth.authsession import FaultTolerantAuthRequestSession
from annotell.input_api.util import filter_none

from annotell.input_api import __version__

log = logging.getLogger(__name__)

ENVELOPED_JSON_TAG = "data"


class HttpClient:
    """Http Client dealing with auth and communication with API."""

    def __init__(self,
                 auth,
                 host: str,
                 auth_host: str,
                 client_organization_id: int = None):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api url
        :param auth_host: override for authentication url
        :param client_organization_id: Overrides your users organization id. Only works with an Annotell user.
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """

        self.host = host
        self._auth_req_session = FaultTolerantAuthRequestSession(host=auth_host, auth=auth)
        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
            "User-Agent": "annotell-input-api/%s" % __version__
        }
        self.dryrun_header = {"X-Dryrun": ""}

        if client_organization_id is not None:
            self.headers["X-Organization-Id"] = str(client_organization_id)
            log.warn(f"WARNING: You will now act as if you are part of organization: {client_organization_id}. "
                     f"This will not work unless you are an Annotell user.")

    @property
    def session(self):
        return self._auth_req_session

    @staticmethod
    def _raise_on_error(resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as exception:
            if exception.response is not None and exception.response.status_code == 400:
                try:
                    message = exception.response.json()["message"]
                except ValueError:
                    message = exception.response.text
                raise RuntimeError(message) from exception

            raise exception from None
        return resp

    @staticmethod
    def _unwrap_enveloped_json(js: dict) -> dict:
        if isinstance(js, list):
            return js
        elif js is not None and js.get(ENVELOPED_JSON_TAG) is not None:
            return js[ENVELOPED_JSON_TAG]
        return js

    def get(self, endpoint, **kwargs) -> dict:
        r"""Sends a GET request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """

        kwargs.setdefault("headers", self.headers)
        resp = self.session.get(f"{self.host}/{endpoint}", **kwargs)
        return self._unwrap_enveloped_json(self._raise_on_error(resp).json())

    def post(self, endpoint, data=None, json=None, dryrun=False, discard_response=False, **kwargs) -> dict:
        r"""Sends a POST request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """

        if dryrun:
            headers = {**self.headers, **self.dryrun_header}
        else:
            headers = {**self.headers}
        kwargs.setdefault("headers", headers)

        resp = self.session.post(f"{self.host}/{endpoint}", data, filter_none(json), **kwargs)
        if discard_response:
            return
        else:
            return self._unwrap_enveloped_json(self._raise_on_error(resp).json())

    def put(self, endpoint, data, **kwargs) -> dict:
        r"""Sends a PUT request. Returns :class:`dict` object.

        :param endpoint: endpoint to be appended to `client.host`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: dict
        """
        kwargs.setdefault("headers", self.headers)
        resp = self.session.put(f"{self.host}/{endpoint}", filter_none(data), **kwargs)
        return self._unwrap_enveloped_json(self._raise_on_error(resp).json())
