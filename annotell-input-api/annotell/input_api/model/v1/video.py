from dataclasses import dataclass

camera_source_default = "CAM"


@dataclass
class VideoFrame:
    video_timestamp: int
    filename: str
    resource_id: str
    sensor_name: str = camera_source_default

    def to_dict(self) -> dict:
        return dict(videoTimestamp=self.video_timestamp,
                    sensorName=self.sensor_name)
