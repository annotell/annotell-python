from typing import List, Optional
from dataclasses import dataclass, field
from annotell.input_api.model.v1.image import ImageFrame
from annotell.input_api.model.v1.video import VideoFrame
from annotell.input_api.model.v1.point_cloud import PointCloudFrame


@dataclass
class Frame:
    frame_id: str
    relative_timestamp: int
    point_cloud_frames: List[PointCloudFrame] = field(default_factory=list)
    image_frames: List[ImageFrame] = field(default_factory=list)
    video_frames: List[VideoFrame] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(frameId=self.frame_id,
                    relativeTimestamp=self.relative_timestamp,
                    pointCloudFrames=[frame.to_dict() for frame in self.point_cloud_frames] if self.point_cloud_frames is not None else None,
                    imageFrames=[frame.to_dict() for frame in self.image_frames] if self.image_frames is not None else None,
                    videoFrames=[frame.to_dict() for frame in self.video_frames] if self.video_frames is not None else None)
