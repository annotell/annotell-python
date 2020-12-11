from typing import List, Optional
from dataclasses import dataclass, field
from annotell.input_api.model.v1.image import ImageFrame
from annotell.input_api.model.v1.video import VideoFrame
from annotell.input_api.model.v1.lidar import LidarFrame


@dataclass
class Frame:
    frame_id: str
    relative_timestamp: int
    lidar_frames: List[LidarFrame] = field(default_factory=list)
    image_frames: List[ImageFrame] = field(default_factory=list)
    video_frames: List[VideoFrame] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(frameId=self.frame_id,
                    relativeTimestamp=self.relative_timestamp,
                    lidarFrames=[frame.to_dict() for frame in self.lidar_frames] if self.lidar_frames is not None else None,
                    imageFrames=[frame.to_dict() for frame in self.image_frames] if self.image_frames is not None else None,
                    videoFrames=[frame.to_dict() for frame in self.video_frames] if self.video_frames is not None else None)
