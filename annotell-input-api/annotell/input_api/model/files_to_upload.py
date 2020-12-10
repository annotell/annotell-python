from typing import List
from annotell.input_api.model.abstract.abstract_models import RequestCall


class FilesToUpload(RequestCall):
    """
    Used when retrieving upload urls from input api
    """

    def __init__(self, files: List[str]):
        self.files = files

    def to_dict(self):
        return dict(filesToUpload=self.files)
