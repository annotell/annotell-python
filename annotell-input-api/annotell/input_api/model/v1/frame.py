from typing import List, Optional
from dataclasses import dataclass
from annotell.input_api.model.v1.image import ImageFrame
from annotell.input_api.model.v1.video import VideoFrame
from annotell.input_api.model.v1.lidar import LidarFrame


@dataclass
class Frame:
    frame_id: str
    relative_timestamp: int
    lidar_frames: Optional[List[LidarFrame]] = None
    image_frames: Optional[List[ImageFrame]] = None
    video_frames: Optional[List[VideoFrame]] = None

    def to_dict(self) -> dict:
        return dict(frameId=self.frame_id,
                    relativeTimestamp=self.relative_timestamp,
                    lidarFrames=[frame.to_dict() for frame in self.lidar_frames] if self.lidar_frames is not None else None,
                    imageFrames=[frame.to_dict() for frame in self.image_frames] if self.image_frames is not None else None,
                    videoFrames=[frame.to_dict() for frame in self.video_frames] if self.video_frames is not None else None)
