from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from annotell.input_api.util import filter_none

camera_sensor_default = "CAM"


@dataclass
class ImageFrame:
    filename: str
    resource_id: Optional[str] = None
    sensor_name: str = camera_sensor_default

    def to_dict(self) -> dict:
        return filter_none({
            "filename": self.filename,
            "resourceId": self.resource_id or str(Path(self.filename).expanduser()),
            "sensorName": self.sensor_name
        })
