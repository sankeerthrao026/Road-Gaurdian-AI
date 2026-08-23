import os
from pathlib import Path
from config.settings import VIDEOS_DIR, BASE_DIR

class VideoManager:
    """
    Manages real road/highway CCTV video files.
    Resolves local video files from car_accidents/ or configured paths.
    Fails loudly with FileNotFoundError if real video file is missing.
    """

    @staticmethod
    def ensure_video_directory():
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_video_path(cls, camera_id: str, configured_path: str) -> str:
        cls.ensure_video_directory()
        candidate = Path(configured_path)
        if candidate.exists() and candidate.is_file():
            return str(candidate.resolve())

        # Only check configured_path relative to BASE_DIR (e.g. car_accidents/...) - never demo_clips
        fallback = BASE_DIR / configured_path
        if fallback.exists() and fallback.is_file():
            return str(fallback.resolve())

        # Check in car_accidents folder directly
        filename = Path(configured_path).name
        car_acc_candidate = BASE_DIR / "car_accidents" / filename
        if car_acc_candidate.exists() and car_acc_candidate.is_file():
            return str(car_acc_candidate.resolve())

        raise FileNotFoundError(
            f"Real video not found for {camera_id} at '{configured_path}'. "
            f"Check that the file exists in car_accidents/ and cameras.json points to it correctly."
        )
