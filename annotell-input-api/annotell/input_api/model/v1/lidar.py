from typing import Optional
from dataclasses import dataclass
from annotell.input_api.util import filter_none


lidar_source_default = "lidar"


@dataclass
class LidarFrame:
    filename: str
    resource_id: Optional[str] = None
    sensor_name: str = lidar_source_default

    def to_dict(self) -> dict:
        return filter_none({
            "filename": self.filename,
            "resourceId": self.resource_id,
            "sensorName": self.sensor_name
        })
