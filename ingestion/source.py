import cv2
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Tuple, Optional
import numpy as np

class VideoSourceType(str, Enum):
    LOCAL_VIDEO = "LOCAL_VIDEO"
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"
    URL = "URL"

class VideoSource:
    """
    Unified Video Source Interface.
    Supports LOCAL_VIDEO, WEBCAM, RTSP, and HTTP/video URLs.
    Handles continuous frame streaming, frame resizing, configurable FPS, and timestamp preservation.
    """

    def __init__(
        self,
        camera_id: str,
        source_type: VideoSourceType = VideoSourceType.LOCAL_VIDEO,
        source_path: str = "",
        target_fps: int = 10,
        frame_width: int = 640,
        frame_height: int = 360,
        loop: bool = True
    ):
        self.camera_id = camera_id
        self.source_type = source_type
        self.source_path = source_path
        self.target_fps = target_fps
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.loop = loop

        self.cap: Optional[cv2.VideoCapture] = None
        self.native_fps: float = 30.0
        self.frame_count: int = 0
        self.start_wall_time: datetime = datetime.now()
        self.is_open: bool = False

    def open(self) -> bool:
        if self.source_type == VideoSourceType.WEBCAM:
            cam_idx = int(self.source_path) if self.source_path.isdigit() else 0
            self.cap = cv2.VideoCapture(cam_idx)
        else:
            self.cap = cv2.VideoCapture(self.source_path)

        if not self.cap or not self.cap.isOpened():
            print(f"[VideoSource] Error: Failed to open {self.source_type} stream from: {self.source_path}")
            self.is_open = False
            return False

        self.native_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.is_open = True
        self.start_wall_time = datetime.now()
        self.frame_count = 0
        return True

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray], str, int]:
        if not self.is_open or self.cap is None:
            if not self.open():
                return False, None, "", self.frame_count

        ret, frame = self.cap.read()
        if not ret:
            if self.loop and self.source_type == VideoSourceType.LOCAL_VIDEO:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            if not ret:
                return False, None, "", self.frame_count

        self.frame_count += 1
        ts_offset_sec = self.frame_count / self.native_fps
        current_time = self.start_wall_time + timedelta(seconds=ts_offset_sec)
        iso_timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%S")

        if self.frame_width and self.frame_height:
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))

        return True, frame, iso_timestamp, self.frame_count

    def stream_frames(
        self, max_frames: Optional[int] = None
    ) -> Generator[Tuple[int, str, np.ndarray], None, None]:
        if not self.open():
            return

        frame_interval = max(1, int(self.native_fps / self.target_fps))
        raw_count = 0
        yielded = 0

        while True:
            ret, frame, iso_ts, f_idx = self.read_frame()
            if not ret or frame is None:
                break

            if raw_count % frame_interval == 0:
                yielded += 1
                yield (yielded, iso_ts, frame)
                if max_frames and yielded >= max_frames:
                    break

            raw_count += 1

        self.close()

    def close(self):
        if self.cap:
            self.cap.release()
        self.is_open = False
