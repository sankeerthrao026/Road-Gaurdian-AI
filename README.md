# 🛡️ RoadGuardian AI — Intelligent Single-Camera Roadside CCTV Monitor
> **Real Roadside CCTV Monitor** | **Theme**: Single-Camera Real Video Streaming + Movement Vector Tracking + 2-Stage Incident Confirmation (Suspected -> Confirmed) + Explainable ML Severity (SHAP) + LangGraph Agentic Intelligence

---

## 🌟 Key Architecture & Features

1. **Single-Camera Intelligent Roadside Monitor ([`dashboard/app.py`](file:///d:/dev_classroom/RoadGuardian/dashboard/app.py))**:
   - Single large prominent CCTV video stream replacing the 3-camera grid.
   - Camera Selector: `[ CAM-01: I-405 Northbound ▼ ]`, `CAM-02: I-35W`, `CAM-03: 170 Freeway`.
   - Seamless stream switching: selecting a camera automatically activates its real video stream while pausing background feeds.
2. **Vehicle Movement & Trajectory Tracking ([`vision/tracker.py`](file:///d:/dev_classroom/RoadGuardian/vision/tracker.py))**:
   - YOLOv8 + ByteTrack persistent tracking (`CAR #17`, `TRUCK #5`, `PERSON #7`).
   - Calculates movement direction, velocity vectors, and renders live trailing trajectory paths behind vehicles.
3. **Two-Stage Mishap Detection While It Happens ([`incidents/manager.py`](file:///d:/dev_classroom/RoadGuardian/incidents/manager.py))**:
   - **Stage 1: `⚠️ INCIDENT SUSPECTED`**: Gathers temporal evidence upon trajectory convergence, abrupt velocity drop, flame contours, or stationary travel-lane blockage.
   - **Stage 2: `🔴 INCIDENT CONFIRMED`**: Confirms incident and activates ML severity scoring and the LangGraph Agent pipeline.
   - Supports **`collision`**, **`fire`**, and **`breakdown`** incident types, plus visual **`rollover`** and pedestrian risk.
4. **Agentic AI & ML Severity (Activated ONLY on Confirmed Incidents)**:
   - ML Severity Scorer (`RandomForest`/`XGBoost`) + SHAP feature attribution bar chart.
   - LangGraph Agent Workflow: Generates simulated authority & hospital dispatches (`[SIMULATED NOTIFICATION SENT]`), objective GenAI reports, and queries ChromaDB RAG.
5. **Real CCTV Footage & Evidence**:
   - Uses real recorded highway footage from `car_accidents/` with rolling frame evidence buffer.

---

## 🚀 How to Run

```powershell
cd d:\dev_classroom\RoadGuardian
.venv\Scripts\python.exe start_all.py
```
Open **`http://localhost:8501`** in your browser.
# Road_gaurdian_ai
