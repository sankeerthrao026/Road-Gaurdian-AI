import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

class VideoAnnotator:
    """
    Renders professional roadside intelligent CCTV computer vision overlays directly onto real video frames.
    Features:
      - Smooth anti-aliased bounding boxes with high-contrast corner bracket accents
      - Polished vehicle classification badges (e.g. CAR #1  0.92)
      - Fading centroid motion trajectory trails
      - Roadside CCTV camera telemetry HUD
    """

    CLASS_COLORS = {
        "car": (255, 165, 0),        # Vibrant Orange / Cyan BGR
        "truck": (0, 215, 255),      # Gold
        "bus": (255, 105, 180),      # Magenta
        "motorcycle": (0, 255, 255), # Yellow
        "person": (255, 50, 150),    # Violet
        "vehicle": (255, 165, 0),
        "fire": (0, 69, 255)         # Red-Orange
    }

    SEVERITY_COLORS = {
        "LOW": (0, 200, 0),
        "MEDIUM": (0, 215, 255),
        "HIGH": (0, 140, 255),
        "CRITICAL": (0, 0, 255)
    }

    @classmethod
    def annotate_frame(
        cls,
        frame: np.ndarray,
        camera_id: str,
        timestamp: str,
        detections: List[Dict[str, Any]],
        processing_state: str = "ANALYZING",
        frame_idx: int = 1,
        total_frames: int = 300,
        fire_bboxes: Optional[List[Dict[str, Any]]] = None,
        final_result: Optional[Dict[str, Any]] = None,
        road_name: str = "Highway Corridor",
        draw_trajectories: bool = True
    ) -> np.ndarray:
        if frame is None:
            return np.zeros((360, 640, 3), dtype=np.uint8)

        annotated = frame.copy()
        h, w, _ = annotated.shape

        # 1. Draw Object Trajectory Trails & Smooth Bounding Boxes
        for det in detections:
            cls_name = det.get("class", "car").lower()
            track_id = det.get("id", 1)
            conf = float(det.get("conf", 0.85))
            bbox = det.get("bbox", [0, 0, 10, 10])
            x1, y1, x2, y2 = [int(v) for v in bbox]
            vel = float(det.get("velocity", 0.0))
            traj = det.get("trajectory", [])

            # Clamp coordinates to frame boundaries
            x1 = max(0, min(w - 2, x1))
            y1 = max(0, min(h - 2, y1))
            x2 = max(x1 + 2, min(w - 1, x2))
            y2 = max(y1 + 2, min(h - 1, y2))

            color = cls.CLASS_COLORS.get(cls_name, (255, 165, 0))

            # A. Draw Smooth Trajectory Motion Trail (Fading dots and polyline)
            if draw_trajectories and traj and len(traj) >= 2:
                pts = [pt for pt in traj if 0 <= pt[0] < w and 0 <= pt[1] < h]
                if len(pts) >= 2:
                    np_pts = np.array(pts, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated, [np_pts], isClosed=False, color=(0, 230, 255), thickness=2, lineType=cv2.LINE_AA)

                    # Draw fading circular trail points
                    num_pts = len(pts)
                    for i, pt in enumerate(pts[-8:]):
                        radius = max(2, int(3 * ((i + 1) / 8.0)))
                        cv2.circle(annotated, (int(pt[0]), int(pt[1])), radius, (255, 255, 255), -1, lineType=cv2.LINE_AA)

            # B. Draw Sleek Bounding Box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2, lineType=cv2.LINE_AA)

            # C. High-Tech Corner Bracket Accents
            corner_w = max(8, int((x2 - x1) * 0.18))
            corner_h = max(8, int((y2 - y1) * 0.18))
            accent_color = (255, 255, 255)

            # Top-Left
            cv2.line(annotated, (x1, y1), (x1 + corner_w, y1), accent_color, 3, cv2.LINE_AA)
            cv2.line(annotated, (x1, y1), (x1, y1 + corner_h), accent_color, 3, cv2.LINE_AA)
            # Top-Right
            cv2.line(annotated, (x2, y1), (x2 - corner_w, y1), accent_color, 3, cv2.LINE_AA)
            cv2.line(annotated, (x2, y1), (x2, y1 + corner_h), accent_color, 3, cv2.LINE_AA)
            # Bottom-Left
            cv2.line(annotated, (x1, y2), (x1 + corner_w, y2), accent_color, 3, cv2.LINE_AA)
            cv2.line(annotated, (x1, y2), (x1, y2 - corner_h), accent_color, 3, cv2.LINE_AA)
            # Bottom-Right
            cv2.line(annotated, (x2, y2), (x2 - corner_w, y2), accent_color, 3, cv2.LINE_AA)
            cv2.line(annotated, (x2, y2), (x2, y2 - corner_h), accent_color, 3, cv2.LINE_AA)

            # D. Label Badge (Pill with Dark Backdrop)
            label_text = f"{cls_name.upper()} #{track_id}  {conf:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.44
            thickness = 1
            (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)

            badge_y1 = max(0, y1 - th - 8)
            badge_y2 = y1
            badge_x1 = x1
            badge_x2 = x1 + tw + 12

            # Background pill
            cv2.rectangle(annotated, (badge_x1, badge_y1), (badge_x2, badge_y2), (15, 23, 42), -1)
            cv2.rectangle(annotated, (badge_x1, badge_y1), (badge_x2, badge_y2), color, 1, cv2.LINE_AA)
            cv2.putText(annotated, label_text, (badge_x1 + 6, badge_y2 - 5),
                        font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # 2. Draw Fire / Smoke Bounding Boxes
        if fire_bboxes:
            for fb in fire_bboxes:
                fx1, fy1, fx2, fy2 = fb.get("bbox", [0, 0, 10, 10])
                cv2.rectangle(annotated, (fx1, fy1), (fx2, fy2), (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(annotated, "🔥 FIRE/SMOKE DETECTED", (fx1, fy1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 255), 2, cv2.LINE_AA)

        # 3. Top CCTV Telemetry HUD Bar
        cv2.rectangle(annotated, (0, 0), (w, 30), (15, 23, 42), -1)
        status_dot_color = (0, 220, 0) if processing_state == "COMPLETE" else (0, 215, 255)
        cv2.circle(annotated, (14, 15), 5, status_dot_color, -1, lineType=cv2.LINE_AA)
        cam_tag = f"ROADGUARDIAN CCTV [{camera_id}] — {road_name} | {timestamp}"
        cv2.putText(annotated, cam_tag, (26, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1, cv2.LINE_AA)

        # 4. Bottom Status Banner
        pct = int(min(100, (frame_idx / max(1, total_frames)) * 100))
        if processing_state == "COMPLETE" and final_result:
            inc_type = str(final_result.get("type", "INCIDENT")).upper()
            sev_label = str(final_result.get("severity_label", "HIGH")).upper()
            sev_score = int(final_result.get("severity_score", 85))
            banner_color = cls.SEVERITY_COLORS.get(sev_label, (0, 0, 255))

            cv2.rectangle(annotated, (0, h - 32), (w, h), (15, 23, 42), -1)
            cv2.rectangle(annotated, (0, h - 32), (w, h), banner_color, 2, cv2.LINE_AA)
            alert_str = f"🔴 FINAL ANALYSIS COMPLETE | {inc_type} CONFIRMED | SEVERITY: {sev_label} ({sev_score}/100)"
            cv2.putText(annotated, alert_str, (14, h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, banner_color, 2, cv2.LINE_AA)
        else:
            cv2.rectangle(annotated, (0, h - 28), (w, h), (15, 23, 42), -1)
            status_text = f"🟡 ANALYZING VIDEO... | FRAME {frame_idx}/{total_frames} ({pct}%) | YOLOv8 + ByteTrack ACTIVE"
            cv2.putText(annotated, status_text, (14, h - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 215, 255), 1, cv2.LINE_AA)

        return annotated
