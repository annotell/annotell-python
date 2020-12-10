from dataclasses import dataclass

camera_source_default = "CAM"


@dataclass
class ImageFrame:
    filename: str
    resource_id: str
    sensor_name: str = camera_source_default

    def to_dict(self) -> dict:
        return dict(filename=self.filename,
                    resourceId=self.resource_id,
                    sensorName=self.sensor_name)
