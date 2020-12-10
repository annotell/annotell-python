from typing import Optional, List
from annotell.input_api.model.abstract.abstract_models import RequestCall


class PointCloud(RequestCall):
    def __init__(self, filename: str, source: Optional[str] = "lidar"):
        self.filename = filename
        self.source = source

    def to_dict(self) -> dict:
        return dict(filename=self.filename,
                    source=self.source)

class PointCloudFiles(RequestCall):
    def __init__(self, point_clouds: List[PointCloud]):
        self.point_clouds = point_clouds

    def to_dict(self) -> dict:
        return dict(pointClouds=[point_cloud.to_dict() for point_cloud in self.point_clouds])