import os
import torch
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Hardware Device Detection
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
HALF_PRECISION = bool(torch.cuda.is_available())

# Video and Performance Settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 360
TARGET_DISPLAY_FPS = 25
TARGET_INFERENCE_FPS = 10  # Configurable: 5, 8, 10, 12 FPS
YOLO_INFERENCE_SIZE = 320  # 320 for fast CPU inference, 640 for GPU
YOLO_MODEL_NAME = "yolov8n.pt"
YOLO_CONF = 0.25

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory Paths
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
VIDEOS_DIR = BASE_DIR / "car_accidents"
EVIDENCE_DIR = BASE_DIR / "evidence"
RAG_CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
CHROMA_DIR = RAG_CHROMA_DIR
MLRUNS_DIR = BASE_DIR / "mlruns"
MLFLOW_EXPERIMENT_NAME = "RoadGuardian_Severity_Scoring"
CAMERAS_CONFIG_PATH = BASE_DIR / "config" / "cameras.json"

for d in [DATA_DIR, MODELS_DIR, VIDEOS_DIR, EVIDENCE_DIR, RAG_CHROMA_DIR, MLRUNS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
