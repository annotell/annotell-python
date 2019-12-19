"""
Base API
"""
import json
import requests
import time
import traceback

from utilities.AnnotellLogger import AnnotellLogger

logger = AnnotellLogger.get_logger(__name__)


class BaseApi(object):
    """ Base API class """

    def __init__(self, session, token, base_url):
        self.session = session
        self.base_url = base_url
        self.token = token

    @staticmethod
    def _to_data(content, external_id=None, content_type="application/json"):
        inp = {
            "contentType": content_type,
            "content": json.dumps(content)
        }
        if external_id:
            inp["externalId"] = external_id
        return inp

    @staticmethod
    def _set_data_ref(data, external_id, input_id):
        if not (external_id or input_id):
            raise KeyError("external_id or input_id is required.")
        if external_id:
            data["externalId"] = external_id
        else:
            data["inputId"] = input_id

    def _login(self, email, password, userapi_url):

        data = {
            "email": email,
            "password": password
        }
        logger.debug("logging in with " + str(data))
        resp = self.session.post(userapi_url + "users/login", json=data)
        resp.raise_for_status()

    def _api_post(self, path, data, with_token=False):
        logger.debug("posting to " + path)
        if with_token: data['token'] = self.token
        try:
            resp = self.session.post(self.base_url + path, json=data, headers={'Connection': 'close'})
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            logger.warn("time out posting to url=" + str(path) + "\nRetrying in 5s...")
            time.sleep(5)
            self._api_post(path, data, with_token)
        except Exception as exc:
            print(traceback.format_exc())
            logger.error(exc)
            raise exc
            # return None

    def _api_get_file(self, path, target_filename):
        logger.debug("getting file " + path)
        url_path = self.base_url + path
        try:
            resp = self.session.get(url_path)
            resp.raise_for_status()
            target_filename = open(target_filename, 'wb')
            target_filename.write(resp.content)
            target_filename.close()
            return target_filename
        except requests.Timeout:
            logger.warn("time out posting to url=" + str(path) + "\nRetrying in 5s...")
            time.sleep(5)
            self._api_get_file(path, target_filename)
        except Exception as exc:
            logger.error(exc)
            return None

    def _api_get(self, path):
        logger.debug("getting " + path)
        url_path = self.base_url + path
        try:
            resp = self.session.get(url_path)
            response = {"status": resp.status_code, "content": resp.content}
            resp.raise_for_status()
            logger.debug("response=" + str(response))
            return resp.json()
        except requests.Timeout:
            logger.warn("time out posting to url=" + str(path) + "\nRetrying in 5s...")
            time.sleep(5)
            self._api_get(path)
        except Exception as exc:
            logger.error(exc)
            return None
