from typing import List
from annotell.input_api.model.abstract.abstract_models import RequestCall


class Video(RequestCall):
    def __init__(self, filename: str,
                 width: int,
                 height: int,
                 source: str = "CAM"):

        self.filename = filename
        self.width = width
        self.height = height
        self.source = source

    def to_dict(self) -> dict:
        return dict(filename=self.filename,
                    width=self.width,
                    height=self.height,
                    source=self.source)