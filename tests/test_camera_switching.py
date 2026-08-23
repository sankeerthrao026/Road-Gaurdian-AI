import os
import sys
import json
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from vision.camera_worker import global_camera_manager
from config.settings import CAMERAS_CONFIG_PATH

class TestCameraManagerSwitching(unittest.TestCase):

    def test_single_active_camera_and_switching(self):
        with open(CAMERAS_CONFIG_PATH, "r") as f:
            cameras = json.load(f)

        global_camera_manager.initialize_cameras(cameras, target_fps=25)

        # 1. Activate CAM-01
        res1 = global_camera_manager.set_active_camera("CAM-01")
        self.assertTrue(res1)
        self.assertEqual(global_camera_manager.get_active_camera_id(), "CAM-01")
        w1 = global_camera_manager.get_active_worker()
        self.assertIsNotNone(w1)
        self.assertEqual(w1.camera_id, "CAM-01")
        self.assertEqual(w1.status, "PLAYING")

        # Let CAM-01 stream frames
        time.sleep(1.5)
        f1, meta1 = w1.get_frame_and_meta()
        self.assertIsNotNone(f1)
        self.assertGreater(meta1["frame_idx"], 1)

        # 2. Switch to CAM-02 -> CAM-01 paused, CAM-02 playing
        res2 = global_camera_manager.set_active_camera("CAM-02")
        self.assertTrue(res2)
        self.assertEqual(global_camera_manager.get_active_camera_id(), "CAM-02")
        w2 = global_camera_manager.get_active_worker()
        self.assertEqual(w2.camera_id, "CAM-02")
        self.assertEqual(w2.status, "PLAYING")
        self.assertEqual(w1.status, "PAUSED")

        # Let CAM-02 stream frames
        time.sleep(1.5)
        f2, meta2 = w2.get_frame_and_meta()
        self.assertIsNotNone(f2)
        self.assertGreater(meta2["frame_idx"], 1)

        # 3. Switch to CAM-03 -> CAM-02 paused, CAM-03 playing
        res3 = global_camera_manager.set_active_camera("CAM-03")
        self.assertTrue(res3)
        self.assertEqual(global_camera_manager.get_active_camera_id(), "CAM-03")
        w3 = global_camera_manager.get_active_worker()
        self.assertEqual(w3.camera_id, "CAM-03")
        self.assertEqual(w3.status, "PLAYING")
        self.assertEqual(w2.status, "PAUSED")

        # 4. Invalid Camera ID fallback
        res_invalid = global_camera_manager.set_active_camera("NON_EXISTENT_CAM")
        self.assertTrue(res_invalid, "Invalid camera ID should gracefully fall back")
        active_w = global_camera_manager.get_active_worker()
        self.assertIsNotNone(active_w)

        global_camera_manager.stop_all()
        print("CameraManager set_active_camera verified successfully with zero errors!")

if __name__ == "__main__":
    unittest.main()
