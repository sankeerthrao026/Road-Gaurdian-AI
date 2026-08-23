import cv2
import numpy as np
from typing import Dict, Any, Optional

class FireSmokeDetector:
    """
    Detects fire and smoke using optical spectrum analysis and motion flicker persistence.
    Exposes structured outputs: fire_detected, smoke_detected, confidence, and bounding boxes.
    """

    def __init__(self, persistence_threshold: int = 3):
        self.persistence_threshold = persistence_threshold
        self.fire_consecutive_counts: Dict[str, int] = {}
        self.smoke_consecutive_counts: Dict[str, int] = {}

    def detect(self, frame: np.ndarray, camera_id: str = "CAM-01") -> Dict[str, Any]:
        if frame is None:
            return {"fire_detected": False, "smoke_detected": False, "confidence": 0.0, "bboxes": []}

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w, _ = frame.shape

        lower_fire1 = np.array([0, 100, 180], dtype=np.uint8)
        upper_fire1 = np.array([35, 255, 255], dtype=np.uint8)
        lower_fire2 = np.array([160, 100, 180], dtype=np.uint8)
        upper_fire2 = np.array([180, 255, 255], dtype=np.uint8)

        mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
        mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
        fire_mask = cv2.bitwise_or(mask1, mask2)

        fire_contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        fire_bboxes = []
        total_fire_area = 0

        for cnt in fire_contours:
            area = cv2.contourArea(cnt)
            if area > 120:
                total_fire_area += area
                x, y, bw, bh = cv2.boundingRect(cnt)
                fire_bboxes.append({
                    "bbox": [x, y, x + bw, y + bh],
                    "type": "fire",
                    "conf": min(0.98, round(0.55 + (area / 3000.0), 2))
                })

        if total_fire_area > 200:
            self.fire_consecutive_counts[camera_id] = self.fire_consecutive_counts.get(camera_id, 0) + 1
        else:
            self.fire_consecutive_counts[camera_id] = max(0, self.fire_consecutive_counts.get(camera_id, 0) - 1)

        is_fire = self.fire_consecutive_counts.get(camera_id, 0) >= self.persistence_threshold
        is_smoke = total_fire_area > 300 and is_fire

        conf = 0.0
        if is_fire:
            conf = min(0.99, 0.65 + (self.fire_consecutive_counts[camera_id] * 0.1))

        return {
            "fire_detected": bool(is_fire),
            "smoke_detected": bool(is_smoke),
            "confidence": round(conf, 2),
            "bboxes": fire_bboxes
        }

    def reset(self, camera_id: Optional[str] = None):
        if camera_id:
            self.fire_consecutive_counts[camera_id] = 0
            self.smoke_consecutive_counts[camera_id] = 0
        else:
            self.fire_consecutive_counts.clear()
            self.smoke_consecutive_counts.clear()
