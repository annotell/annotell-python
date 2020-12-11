from typing import Optional, List, Dict, Mapping
from dataclasses import dataclass

from annotell.input_api.util import filter_none


@dataclass
class CameraSettings:
    width: int
    height: int


@dataclass
class SensorSpecification:
    sensor_to_pretty_name: Optional[Dict[str, str]] = None
    sensor_order: Optional[List[str]] = None
    sensor_settings: Optional[Mapping[str, CameraSettings]] = None

    def to_dict(self):
        return filter_none({
            "sensorToPrettyName": self.sensor_to_pretty_name,
            "sensorOrder": self.sensor_order,
            "sensorSettings": self.sensor_settings
        })
