import requests
from annotell.auth.authsession import AuthSession, DEFAULT_HOST as DEFAULT_AUTH_HOST

DEFAULT_HOST = "https://export.annotell.com"

class ExportApiClient:
    """Export Annotell data."""

    def __init__(self, *,
                 auth: None,
                 host: str = DEFAULT_HOST,
                 auth_host: str = DEFAULT_AUTH_HOST):
        """
        :param auth: auth credentials, see https://github.com/annotell/annotell-python/tree/master/annotell-auth
        :param host: override for input api host
        :param auth_host: override for authentication host
        """

        self.host = host
        self.oauth_session = AuthSession(host=auth_host, auth=auth)
        self.headers = {
            "Accept-Encoding": "gzip",
            "Accept": "application/json"
        }

    @property
    def session(self) -> requests.Session:
        return self.oauth_session.session

    @staticmethod
    def _raise_on_error(resp: requests.Response) -> requests.Response:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise
        return resp

    def post_annotation_feedback(self,
                                 customer_callback_id: str,
                                 feedback: dict):
        """
        :param customer_callback_id: customer callback id
        :feedback
        {
            “inputInternalId”: <uuid>,
            “requestId”: <int>,
            “annotationId”: <int>,
            “passed”: <bool>,
            “itemErrors”: <optional list of error maps>,
            "generalErrors": <optional list of error maps>
        }
        error:
        {
            “message”: <string>
            “objectId”: <optional string>
            “checkId”: <optional string>
        }
        objectId does not apply for generalErrors

        :return:
        """
        url = f"{self.host}/v1/feedback/annotations/{customer_callback_id}"
        resp = self.session.post(url, json=feedback, headers=self.headers)
        return self._raise_on_error(resp)

