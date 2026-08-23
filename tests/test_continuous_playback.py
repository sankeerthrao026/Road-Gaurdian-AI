import os
import sys
import time
import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from vision.camera_worker import global_camera_manager
from config.settings import CAMERAS_CONFIG_PATH

class TestContinuousVideoPlayback(unittest.TestCase):

    def test_single_active_camera_continuous_playback(self):
        with open(CAMERAS_CONFIG_PATH, "r") as f:
            cameras = json.load(f)

        global_camera_manager.initialize_cameras(cameras, target_fps=25)

        # 1. Test CAM-01 continuous playback
        global_camera_manager.set_active_camera("CAM-01")
        time.sleep(2.0)
        w1 = global_camera_manager.get_active_worker()
        self.assertIsNotNone(w1)
        frame, meta = w1.get_frame_and_meta()
        self.assertIsNotNone(frame)
        self.assertGreater(meta["frame_idx"], 5, f"CAM-01 did not advance frames (frame_idx={meta['frame_idx']})")
        self.assertEqual(meta["status"], "PLAYING")
        print(f"[CAM-01] Stream advancing -> Frame: {meta['frame_idx']}/{meta['total_frames']}, FPS: {meta['fps']}, Time: {meta['time_str']}")

        # 2. Test Pause & Play
        global_camera_manager.pause_active()
        time.sleep(0.3)
        _, meta_paused = w1.get_frame_and_meta()
        self.assertEqual(meta_paused["status"], "PAUSED")

        global_camera_manager.play_active()
        time.sleep(0.3)
        _, meta_play = w1.get_frame_and_meta()
        self.assertEqual(meta_play["status"], "PLAYING")

        # 3. Test Switching to CAM-02
        global_camera_manager.set_active_camera("CAM-02")
        time.sleep(2.0)
        w2 = global_camera_manager.get_active_worker()
        self.assertEqual(w2.camera_id, "CAM-02")
        frame2, meta2 = w2.get_frame_and_meta()
        self.assertIsNotNone(frame2)
        self.assertGreater(meta2["frame_idx"], 5, f"CAM-02 did not advance frames (frame_idx={meta2['frame_idx']})")
        print(f"[CAM-02] Stream advancing -> Frame: {meta2['frame_idx']}/{meta2['total_frames']}, FPS: {meta2['fps']}, Time: {meta2['time_str']}")

        global_camera_manager.stop_all()
        print("Single-camera continuous playback & switching verified successfully!")

if __name__ == "__main__":
    unittest.main()
