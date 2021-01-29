from typing import Optional
from dataclasses import dataclass
from annotell.input_api.util import filter_none
from pathlib import Path

camera_sensor_default = "CAM"


@dataclass
class VideoFrame:
    video_timestamp: int
    filename: str
    resource_id: Optional[str] = None
    sensor_name: str = camera_sensor_default

    def to_dict(self) -> dict:
        return filter_none({
            "videoTimestamp": self.video_timestamp,
            "sensorName": self.sensor_name,
            "resourceId": self.resource_id or str(Path(self.filename).expanduser())
        })
