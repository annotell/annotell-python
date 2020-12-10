from dataclasses import dataclass

lidar_source_default = "lidar"


@dataclass
class LidarFrame:
    filename: str
    resource_id: str
    sensor_name: str = lidar_source_default

    def to_dict(self) -> dict:
        return dict(filename=self.filename,
                    resourceId=self.resource_id,
                    sensorName=self.sensor_name)
