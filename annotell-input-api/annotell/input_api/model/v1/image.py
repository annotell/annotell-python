from typing import Optional, List
from annotell.input_api.model.abstract.abstract_models import RequestCall
from pathlib import Path
from PIL import Image as PILImage


class Image(RequestCall):
    def __init__(self, filename: str,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
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

    def set_images_dimensions(self, folder: Path) -> None:
        if self.width is None or self.height is None:
            fi = folder.joinpath(self.filename).expanduser()
            with PILImage.open(fi) as im:
                width, height = im.size
                self.height = height
                self.width = width

class ImagesFiles(RequestCall):
    def __init__(self, images: List[Image]):
        self.images = images

    def to_dict(self) -> dict:
        return dict(images=[image.to_dict() for image in self.images])