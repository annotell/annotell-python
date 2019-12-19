"""
Storage API client
"""

import requests

from apiclients.AnnotellLogger import AnnotellLogger
from apiclients.BaseApi import BaseApi

logger = AnnotellLogger.get_logger(__name__)


class StorageApi(BaseApi):
    """ Annotell API client """

    def __init__(self, token, session=requests.session(), base_url="http://annotell.org:8004/v1/"):
        logger.debug("starting " + str(__name__))
        super().__init__(session, token, base_url)

    def download_image(self, filename, target_filename):
        """ Create a new project. """
        return self._api_get_file("image?fileName=" + str(filename), target_filename)

    def download_rasterization(self, judgement_id, target_filename):
        """ Create a new project. """
        return self._api_get_file("bitmap?judgementId=" + str(judgement_id), target_filename)

    def create_rasterization(self, judgement_id):
        """ Create a new project. """
        data = {
            "judgementId": int(judgement_id),
        }
        return self._api_post("bitmap/rasterize", data)
