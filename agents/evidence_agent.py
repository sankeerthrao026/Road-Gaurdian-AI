import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import EVIDENCE_DIR

class EvidenceAgent:
    """Saves keyframe images and clip evidence in the agreed contract structure."""

    def __init__(self, base_evidence_dir: Optional[Path] = None):
        self.evidence_dir = Path(base_evidence_dir) if base_evidence_dir else EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def capture_evidence(
        self,
        incident_id: str,
        frame_image: Optional[np.ndarray] = None,
        clip_source_path: Optional[str] = None
    ) -> Dict[str, Any]:
        incident_folder = self.evidence_dir / incident_id
        incident_folder.mkdir(parents=True, exist_ok=True)

        keyframe_path = incident_folder / "frame_1.jpg"
        relative_frame_path = f"evidence/{incident_id}/frame_1.jpg"
        relative_clip_path = f"evidence/{incident_id}/clip.mp4"

        if frame_image is not None:
            try:
                cv2.imwrite(str(keyframe_path), frame_image)
            except Exception as e:
                print(f"[EvidenceAgent] Error writing keyframe: {e}")
        elif not keyframe_path.exists():
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            placeholder[80:280, 80:560] = [40, 40, 40]
            cv2.putText(placeholder, f"INCIDENT: {incident_id}", (140, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imwrite(str(keyframe_path), placeholder)

        evidence_payload = {
            "clip_path": relative_clip_path,
            "key_frames": [relative_frame_path]
        }

        return evidence_payload
