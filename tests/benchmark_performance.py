import os
import sys
import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import cv2
import torch
from config.settings import CAMERAS_CONFIG_PATH
from vision.camera_worker import CameraWorker
from ingestion.video_manager import VideoManager

def benchmark_video_processing():
    print("=" * 70)
    print("ROADGUARDIAN PERFORMANCE BENCHMARK")
    print(f"PyTorch CUDA Available: {torch.cuda.is_available()}")
    print("=" * 70)

    video_path = VideoManager.get_video_path("CAM-01", "car_accidents/car_rollover 2.mp4")
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 180)
    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    video_duration = total_frames / max(1.0, native_fps)
    cap.release()

    print(f"Video File: {Path(video_path).name}")
    print(f"Total Frames: {total_frames}")
    print(f"Native FPS: {native_fps:.1f}")
    print(f"Video Duration: {video_duration:.2f}s")
    print("-" * 70)

    worker = CameraWorker(
        camera_id="CAM-01",
        camera_name="Highway 101 Rollover",
        video_path=video_path,
        gps_info={"name": "Highway 101", "lat": 47.61, "lon": -122.20},
        road_name="Highway 101 Corridor"
    )

    t0 = time.time()
    worker.start()

    while worker.processing_state != "COMPLETE":
        time.sleep(0.05)

    total_time = time.time() - t0
    _, meta = worker.get_frame_and_meta()
    worker.stop()

    speedup = video_duration / max(0.001, total_time)

    print("\nBENCHMARK RESULTS:")
    print(f"Total Processing Time:     {total_time:.2f}s")
    print(f"Video Real Duration:       {video_duration:.2f}s")
    print(f"Speedup vs Real-Time:      {speedup:.2f}x")
    print(f"Frames Inferred:           {meta.get('frames_processed', 0)}")
    print(f"Frames Skipped (Interpol): {meta.get('frames_skipped', 0)}")
    print(f"Display FPS:               {meta.get('display_fps', 0)}")
    print(f"AI Inference FPS:          {meta.get('ai_fps', 0)}")
    print(f"Final Incident Detected:   {worker.final_result.get('type') if worker.final_result else 'None'}")
    print(f"Final Severity:            {worker.final_result.get('severity_score') if worker.final_result else 'None'}/100")
    print("=" * 70)

if __name__ == "__main__":
    benchmark_video_processing()
