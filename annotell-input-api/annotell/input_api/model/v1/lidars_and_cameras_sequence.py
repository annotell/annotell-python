from dataclasses import dataclass
from typing import List, Optional, Set

from annotell.input_api.model.v1.frame import Frame
from annotell.input_api.model.v1.sensor_specification import SensorSpecification


@dataclass
class LidarsAndCamerasSequence:
    external_id: str
    frames: List[Frame]
    calibration_id: int
    internal_id: str
    start_ts: Optional[int] = None
    sensor_specification: Optional[SensorSpecification] = None
    """
    Unix timestamp for start of sequence
    """

    # pre_annotation: Optional[DataId]

    def to_dict(self) -> dict:
        return dict(frames=self.frames,
                    sensorSpecification=self.sensor_specification,
                    externalId=self.external_id,
                    internalId=self.internal_id,
                    startTs=self.start_ts,
                    # preAnnotation = self.preAnnotation,
                    calibrationId=self.calibration_id)

    def resources(self) -> Set[str]:
        resources = []
        for frame in self.frames:
            for resource in (frame.lidar_frames + frame.image_frames + frame.video_frames):
                resources.append(resource.filename)

        return set(resources)
