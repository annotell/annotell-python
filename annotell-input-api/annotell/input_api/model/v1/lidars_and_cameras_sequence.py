from dataclasses import dataclass
from typing import List, Optional, Union

from annotell.input_api.model.v1.frame import Frame, ImageFrame, PointCloudFrame, VideoFrame
from annotell.input_api.model.v1.sensor_specification import SensorSpecification


@dataclass
class LidarsAndCamerasSequence:
    external_id: str
    frames: List[Frame]
    calibration_id: int
    sensor_specification: Optional[SensorSpecification] = None

    def to_dict(self) -> dict:
        return dict(frames=[frame.to_dict() for frame in self.frames],
                    sensorSpecification=self.sensor_specification.to_dict(),
                    externalId=self.external_id,
                    calibrationId=self.calibration_id)

    def get_local_resources(self) -> List[Union[PointCloudFrame, VideoFrame, ImageFrame]]:
        resources = []
        for frame in self.frames:
            for resource in (frame.point_cloud_frames + frame.image_frames + frame.video_frames):
                if resource.resource_id is None:
                    resources.append(resource)

        return resources
