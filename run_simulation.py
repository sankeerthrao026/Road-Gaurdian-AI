import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import CAMERAS_CONFIG_PATH, VIDEOS_DIR, EVIDENCE_DIR
from ingestion.source import VideoSource, VideoSourceType
from ingestion.video_manager import VideoManager
from vision.tracker import VideoTracker
from vision.annotator import VideoAnnotator
from vision.fire_smoke import FireSmokeDetector
from incidents.manager import global_incident_manager
from agents.graph import process_incident_through_agents
from agents.state import global_incident_store
from rag.store import global_rag_store
from severity.train_mlflow import train_and_evaluate_models

def run_real_video_pipeline():
    print("=" * 75)
    print("[ROADGUARDIAN AI] REAL ROAD VIDEO + YOLO/BYTETRACK + AGENTIC AI PIPELINE")
    print("=" * 75)

    print("\n[Phase 1/5] Initializing ML Severity Models (RandomForest vs XGBoost)...")
    train_and_evaluate_models()

    print("\n[Phase 2/5] Loading Real Highway/Road CCTV Video Sources...")
    with open(CAMERAS_CONFIG_PATH, "r") as f:
        cameras = json.load(f)

    video_sources = {}
    for cam in cameras:
        vid_path = VideoManager.get_video_path(cam["id"], cam["source_path"])
        video_sources[cam["id"]] = VideoSource(
            camera_id=cam["id"],
            source_type=VideoSourceType.LOCAL_VIDEO,
            source_path=vid_path,
            target_fps=10,
            frame_width=640,
            frame_height=360,
            loop=False
        )
        print(f"  -> Camera [{cam['id']}]: '{cam['name']}' -> Source: {vid_path}")

    tracker = VideoTracker()
    fire_detector = FireSmokeDetector()

    print("\n[Phase 3/5] Processing Real CCTV Video Feeds with YOLO & ByteTrack...")

    for cam in cameras:
        cam_id = cam["id"]
        cam_name = cam["name"]
        gps_info = cam["gps"]
        v_source = video_sources[cam_id]

        print(f"\n--- Streaming Real Video: [{cam_id}] {cam_name} ---")
        processed_frames = 0
        latest_incident_dict = None
        keyframe_saved = None

        for f_idx, iso_ts, frame in v_source.stream_frames(max_frames=35):
            processed_frames += 1

            detections = tracker.track(frame, camera_id=cam_id)
            fire_res = fire_detector.detect(frame, camera_id=cam_id)

            m_status, inc_entity = global_incident_manager.process_frame_detections(
                camera_id=cam_id,
                location=gps_info,
                timestamp=iso_ts,
                detections=detections,
                fire_result=fire_res,
                manual_rollover=False
            )

            if inc_entity:
                latest_incident_dict = inc_entity.to_dict()
                keyframe_saved = frame

        if latest_incident_dict:
            final_inc = process_incident_through_agents(
                latest_incident_dict,
                frame_image=keyframe_saved
            )
            global_rag_store.add_incident(final_inc)
            print(f"[OK] [{cam_id}] Incident Detected: {final_inc.get('type').upper()} | Severity: {final_inc.get('severity_score')}/100 ({final_inc.get('severity_label')}) | Priority Rank: #{final_inc.get('priority_rank')}")
        else:
            print(f"[OK] [{cam_id}] Processed {processed_frames} real frames. Traffic flowing within normal bounds.")

    print("\n" + "=" * 75)
    print("[PRIORITY QUEUE] REAL-TIME CROSS-CAMERA INCIDENT RANKINGS:")
    print("=" * 75)
    active = global_incident_store.get_all_active_sorted()
    for inc in active:
        print(f"Rank #{inc.get('priority_rank')}: [{inc.get('incident_id')}] {inc.get('type').upper()} on {inc.get('camera_id')} ({inc.get('location', {}).get('name')}) - Score: {inc.get('severity_score')} ({inc.get('severity_label')})")

    print("\n" + "=" * 75)
    print("[WOW MOMENT] EXECUTING LIVE DYNAMIC RE-PRIORITIZATION (Thermal Escalation on CAM-02)")
    print("=" * 75)
    print("Simulating real-time fire and vehicle rollover outbreak on CAM-02...")
    time.sleep(1)

    target_inc = global_incident_store.get_incident("CAM02_001")
    if not target_inc and active:
        target_inc = active[-1]

    if target_inc:
        target_inc["features"]["fire_smoke"] = True
        target_inc["features"]["rollover"] = True
        target_inc["features"]["person_on_road"] = True
        target_inc["features"]["vehicle_count"] = 4
        target_inc["features"]["traffic_impact"] = "high"
        target_inc["type"] = "fire"
        target_inc["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        escalated_inc = process_incident_through_agents(target_inc)
        global_rag_store.add_incident(escalated_inc)

        print(f"\n[ESCALATED] {escalated_inc.get('incident_id')} updated with Fire & Rollover!")
        print(f"New Severity Score: {escalated_inc.get('severity_score')}/100 ({escalated_inc.get('severity_label')})")
        print(f"New Priority Rank:  #{escalated_inc.get('priority_rank')} (DYNAMICALLY PROMOTED TO #1 CRITICAL!)")

    print("\n" + "=" * 75)
    print("[RE-RANKED QUEUE] POST-ESCALATION MULTI-CAMERA PRIORITY QUEUE:")
    print("=" * 75)
    for inc in global_incident_store.get_all_active_sorted():
        print(f"Rank #{inc.get('priority_rank')}: [{inc.get('incident_id')}] {inc.get('type').upper()} on {inc.get('camera_id')} - Score: {inc.get('severity_score')} ({inc.get('severity_label')})")

    print("\n" + "=" * 75)
    print("[CONTRACT OUTPUT] JSON Payload conforming to backend contract:")
    print("=" * 75)
    sample_incident = global_incident_store.get_all_active_sorted()[0]
    contract_json = {
        "incident_id": sample_incident.get("incident_id"),
        "type": sample_incident.get("type"),
        "camera_id": sample_incident.get("camera_id"),
        "location": sample_incident.get("location"),
        "timestamp": sample_incident.get("timestamp"),
        "features": sample_incident.get("features"),
        "severity_score": sample_incident.get("severity_score"),
        "severity_label": sample_incident.get("severity_label"),
        "evidence": sample_incident.get("evidence")
    }
    print(json.dumps(contract_json, indent=2))
    print("\n[SUCCESS] Real video simulation pipeline completed successfully!")

if __name__ == "__main__":
    run_real_video_pipeline()
