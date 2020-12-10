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
                    lidarFrames=self.lidar_frames,
                    imageFrames=self.image_frames,
                    videoFrames=self.video_frames)
