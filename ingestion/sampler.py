import cv2
from datetime import datetime, timedelta
from typing import Generator, Tuple, Optional
import numpy as np

class VideoSampler:
    """Samples frames from video files or streams at configurable FPS with exact timestamps."""

    def __init__(self, target_fps: int = 10, max_frames: Optional[int] = 300):
        self.target_fps = target_fps
        self.max_frames = max_frames

    def sample_frames(
        self, video_path: str, start_time: Optional[datetime] = None
    ) -> Generator[Tuple[int, float, str, np.ndarray], None, None]:
        if start_time is None:
            start_time = datetime.now()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[VideoSampler] Warning: Could not open video {video_path}")
            return

        native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(native_fps / self.target_fps))

        frame_count = 0
        yielded_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                ts_sec = frame_count / native_fps
                current_ts = start_time + timedelta(seconds=ts_sec)
                iso_ts = current_ts.strftime("%Y-%m-%dT%H:%M:%S")

                yield (yielded_count, ts_sec, iso_ts, frame)
                yielded_count += 1

                if self.max_frames and yielded_count >= self.max_frames:
                    break

            frame_count += 1

        cap.release()
