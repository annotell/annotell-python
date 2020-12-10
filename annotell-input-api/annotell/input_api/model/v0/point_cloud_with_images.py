from typing import List
from annotell.input_api.model.abstract.abstract_models import RequestCall
from annotell.input_api.model.v0.image import Image
from annotell.input_api.model.v0.point_cloud import PointCloud


class PointCloudsWithImages(RequestCall):
    def __init__(self, images: List[Image], point_clouds: List[PointCloud]):
        self.images = images
        self.point_clouds = point_clouds

    def to_dict(self):
        return dict(images=[image.to_dict() for image in self.images],
                    pointClouds=[pc.to_dict() for pc in self.point_clouds])