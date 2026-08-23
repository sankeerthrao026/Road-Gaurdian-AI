import os
import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import VIDEOS_DIR, CAMERAS_CONFIG_PATH
from ingestion.source import VideoSource, VideoSourceType
from ingestion.video_manager import VideoManager
from vision.tracker import VideoTracker
from vision.annotator import VideoAnnotator
from vision.fire_smoke import FireSmokeDetector
from incidents.state_machine import IncidentEntity, IncidentStateStatus
from incidents.manager import IncidentManager
from severity.dataset import calculate_rule_score, score_to_label, generate_synthetic_dataset
from severity.scorer import score_incident, get_model_comparison_metrics
from severity.train_mlflow import train_and_evaluate_models
from agents.graph import process_incident_through_agents
from agents.state import global_incident_store
from rag.store import global_rag_store

class TestRoadGuardianRealVideoSystem(unittest.TestCase):

    def test_01_real_video_files_and_sources(self):
        VideoManager.ensure_video_directory()
        vid_path = VideoManager.get_video_path("CAM-01", "car_accidents/collision_01.mp4")
        self.assertTrue(os.path.exists(vid_path), f"Video file missing: {vid_path}")

        source = VideoSource("CAM-01", VideoSourceType.LOCAL_VIDEO, vid_path, target_fps=10)
        opened = source.open()
        self.assertTrue(opened, "Failed to open real video source with OpenCV")
        ret, frame, ts, idx = source.read_frame()
        self.assertTrue(ret, "Failed to read real video frame")
        self.assertIsNotNone(frame, "Read frame was None")
        self.assertEqual(len(frame.shape), 3, "Frame must be 3-channel BGR")
        source.close()

    def test_02_yolo_and_bytetrack_tracking(self):
        tracker = VideoTracker()
        vid_path = VideoManager.get_video_path("CAM-01", "car_accidents/collision_01.mp4")
        source = VideoSource("CAM-01", VideoSourceType.LOCAL_VIDEO, vid_path, target_fps=10)
        source.open()

        all_detections = []
        for _ in range(5):
            ret, frame, ts, idx = source.read_frame()
            if ret and frame is not None:
                dets = tracker.track(frame, camera_id="CAM-01")
                all_detections.append(dets)
        source.close()

        self.assertGreater(len(all_detections), 0, "No frames processed by tracker")

    def test_03_frame_annotation(self):
        vid_path = VideoManager.get_video_path("CAM-01", "car_accidents/collision_01.mp4")
        source = VideoSource("CAM-01", VideoSourceType.LOCAL_VIDEO, vid_path)
        source.open()
        ret, frame, ts, _ = source.read_frame()
        source.close()

        mock_dets = [{"id": 1, "class": "car", "bbox": [50, 50, 150, 120], "conf": 0.90, "velocity": 5.2}]
        annotated = VideoAnnotator.annotate_frame(
            frame, "CAM-01", ts, mock_dets, road_name="NH-44 Corridor"
        )
        self.assertEqual(annotated.shape, frame.shape)

    def test_04_incident_state_machine_and_debouncing(self):
        manager = IncidentManager()
        loc = {"name": "I-405 Northbound", "lat": 47.6101, "lon": -122.2015}
        mock_dets = [
            {"id": 1, "class": "car", "center": (100, 100), "bbox": [80, 80, 120, 120], "velocity": 0.0},
            {"id": 2, "class": "car", "center": (110, 105), "bbox": [90, 85, 130, 125], "velocity": 0.0}
        ]
        fire_res = {"fire_detected": False, "smoke_detected": False, "bboxes": []}

        status1, inc1 = manager.process_frame_detections("CAM-01", loc, "2026-08-22T10:00:00", mock_dets, fire_res)
        self.assertIsNotNone(inc1)

        status2, inc2 = manager.process_frame_detections("CAM-01", loc, "2026-08-22T10:00:01", mock_dets, fire_res)
        self.assertEqual(inc1.incident_id, inc2.incident_id, "Debouncing failed: spawned duplicate incident IDs")

    def test_05_severity_ml_and_langgraph_pipeline(self):
        sample_raw = {
            "incident_id": "TEST_REAL_001",
            "type": "collision",
            "camera_id": "CAM-01",
            "location": {"name": "I-405 Bellevue", "lat": 47.6101, "lon": -122.2015},
            "timestamp": "2026-08-22T14:32:10",
            "features": {
                "vehicle_count": 3,
                "person_on_road": True,
                "fire_smoke": False,
                "rollover": False,
                "traffic_impact": "high"
            }
        }
        res = process_incident_through_agents(sample_raw)
        self.assertIn("severity_score", res)
        self.assertIn("severity_label", res)
        self.assertIn("shap_values", res)
        self.assertIn("report_text", res)
        self.assertIn("priority_rank", res)

if __name__ == "__main__":
    unittest.main()
