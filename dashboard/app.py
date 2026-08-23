import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import plotly.graph_objects as go
import numpy as np

from config.settings import CAMERAS_CONFIG_PATH, BASE_DIR, DEVICE
from vision.camera_worker import global_camera_manager
from agents.state import global_incident_store
from agents.graph import process_incident_through_agents
from rag.store import global_rag_store
from severity.scorer import get_model_comparison_metrics
from dashboard.styles import DARK_THEME_CSS

# 1. Page Configuration
st.set_page_config(
    page_title="RoadGuardian AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# 2. Camera Configurations
@st.cache_data
def load_cameras():
    with open(CAMERAS_CONFIG_PATH, "r") as f:
        return json.load(f)

cameras = load_cameras()
cam_dict = {cam["id"]: cam for cam in cameras}
camera_options = [f"{cam['id']}: {cam['name']}" for cam in cameras]

# 3. Initialize Camera Background Workers & Session State
if "active_camera_id" not in st.session_state:
    st.session_state["active_camera_id"] = cameras[0]["id"]
if "is_streaming" not in st.session_state:
    st.session_state["is_streaming"] = True
if "video_complete" not in st.session_state:
    st.session_state.video_complete = False
if "finalization_started" not in st.session_state:
    st.session_state.finalization_started = False
if "finalization_complete" not in st.session_state:
    st.session_state.finalization_complete = False
if "final_result" not in st.session_state:
    st.session_state.final_result = None

if "initialized" not in st.session_state:
    global_camera_manager.initialize_cameras(cameras)
    global_camera_manager.set_active_camera(st.session_state["active_camera_id"])
    st.session_state["initialized"] = True

# 4. Chart Builders
def build_gauge_fig(score: int, label: str):
    colors = {"Low": "#55C98A", "Medium": "#C98255", "High": "#C98255", "Critical": "#D9534F"}
    bar_color = colors.get(label, "#C98255")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"SEVERITY: <b>{label.upper()}</b>", 'font': {'size': 11.5, 'color': '#999EA5', 'family': 'IBM Plex Sans'}},
        number={'font': {'size': 24, 'color': '#D4D9DF', 'family': 'IBM Plex Mono'}, 'suffix': "/100"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#394047", 'tickfont': {'color': '#798690', 'family': 'IBM Plex Mono'}},
            'bar': {'color': bar_color, 'thickness': 0.25},
            'bgcolor': "#141517",
            'borderwidth': 1,
            'bordercolor': "#394047",
            'steps': [
                {'range': [0, 29], 'color': 'rgba(85, 201, 138, 0.08)'},
                {'range': [29, 54], 'color': 'rgba(201, 130, 85, 0.08)'},
                {'range': [54, 79], 'color': 'rgba(201, 130, 85, 0.12)'},
                {'range': [79, 100], 'color': 'rgba(217, 83, 79, 0.14)'}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=25, b=5),
        height=135
    )
    return fig

def build_shap_fig(shap_values: dict):
    features = list(shap_values.keys())
    values = [shap_values[f] for f in features]
    colors = ['#C98255' if v > 0 else '#55C98A' for v in values]
    friendly_names = {
        "vehicle_count": "Vehicle Count",
        "person_on_road": "Person on Road",
        "fire_smoke": "Fire / Smoke",
        "rollover": "Vehicle Rollover",
        "traffic_impact": "Traffic Impact"
    }
    display_names = [friendly_names.get(f, f) for f in features]

    fig = go.Figure(go.Bar(
        x=values,
        y=display_names,
        orientation='h',
        marker=dict(color=colors, line=dict(color='#394047', width=1)),
        text=[f"{v:+.1f}" for v in values],
        textposition='outside',
        textfont=dict(color='#D4D9DF', size=10.5, family='IBM Plex Mono')
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="<b>SHAP Feature Attribution</b>", font=dict(size=11.5, color='#999EA5', family='IBM Plex Sans')),
        xaxis=dict(gridcolor='#1D222A', zerolinecolor='#394047', tickfont=dict(color='#798690', family='IBM Plex Mono')),
        yaxis=dict(gridcolor='#1D222A', tickfont=dict(color='#999EA5', size=11, family='IBM Plex Sans')),
        margin=dict(l=10, r=30, t=25, b=5),
        height=170
    )
    return fig

# 5. Sidebar Navigation & Global Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=44)
    st.title("ROADGUARDIAN")
    st.caption("AI Incident Intelligence")
    st.markdown("<div style='border-bottom: 1px solid #394047; margin: 12px 0;'></div>", unsafe_allow_html=True)

    st.subheader("CAMERA")
    active_idx = 0
    for idx, opt in enumerate(camera_options):
        if opt.startswith(st.session_state["active_camera_id"]):
            active_idx = idx
            break

    selected_option = st.selectbox(
        "Active Camera",
        options=camera_options,
        index=active_idx,
        key="camera_selector_dropdown"
    )
    selected_cam_id = selected_option.split(":")[0].strip()

    if selected_cam_id != st.session_state["active_camera_id"]:
        st.session_state["active_camera_id"] = selected_cam_id
        global_camera_manager.set_active_camera(selected_cam_id)
        st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #394047; margin: 14px 0;'></div>", unsafe_allow_html=True)
    st.subheader("PLAYBACK")
    c_p1, c_p2, c_p3 = st.columns(3)
    active_worker = global_camera_manager.get_active_worker()

    with c_p1:
        if st.button("▶ Play", key="btn_play_active", use_container_width=True, type="primary"):
            st.session_state["is_streaming"] = True
            if active_worker:
                active_worker.play()
    with c_p2:
        if st.button("⏸ Pause", key="btn_pause_active", use_container_width=True):
            st.session_state["is_streaming"] = False
            if active_worker:
                active_worker.pause()
    with c_p3:
        if st.button("↻ Restart", key="btn_restart_active", use_container_width=True):
            st.session_state["is_streaming"] = True
            if active_worker:
                active_worker.restart()
            st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #394047; margin: 14px 0;'></div>", unsafe_allow_html=True)
    st.markdown("<span class='badge-simulated'>SIMULATED DISPATCH</span>", unsafe_allow_html=True)
    st.caption(f"YOLOv8 + ByteTrack ({DEVICE.upper()}) with single EOF Agentic AI pipeline.")

# 6. Main Dashboard Header
st.markdown("""
<div class="dribbble-header">
    <div>
        <div class="brand-title">ROADGUARDIAN</div>
        <div class="brand-subtitle">AI ROAD INCIDENT INTELLIGENCE</div>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <span class="system-status-tag"><span class="status-dot-warm"></span> SYSTEM ONLINE</span>
        <span class="system-status-tag">CAM-01 / HIGHWAY MONITORING</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. Single CCTV Video Stream Layout (Prominent Top Center)
st.markdown('<div class="dribbble-section-title">VIDEO AREA</div>', unsafe_allow_html=True)

cam_progress_placeholder = st.empty()
cam_meta_placeholder = st.empty()
cam_video_placeholder = st.empty()

st.markdown("<div style='border-bottom: 1px solid #394047; margin: 16px 0;'></div>", unsafe_allow_html=True)

# 8. Intelligence Dossier (Below Video)
st.markdown('<div class="dribbble-section-title">INCIDENT ANALYSIS</div>', unsafe_allow_html=True)

col_inc_left, col_inc_right = st.columns([5, 7])

with col_inc_left:
    st.markdown("<div style='font-family: \"IBM Plex Mono\", monospace; font-size: 11px; font-weight: 700; color: #999EA5; text-transform: uppercase; margin-bottom: 8px;'>Incident Status</div>", unsafe_allow_html=True)
    incident_card_placeholder = st.empty()

    st.markdown("<div style='font-family: \"IBM Plex Mono\", monospace; font-size: 11px; font-weight: 700; color: #999EA5; text-transform: uppercase; margin-top: 14px; margin-bottom: 8px;'>Severity & Attribution</div>", unsafe_allow_html=True)
    g_col, s_col = st.columns([1, 1])
    with g_col:
        gauge_placeholder = st.empty()
    with s_col:
        shap_placeholder = st.empty()

with col_inc_right:
    st.markdown("<div style='font-family: \"IBM Plex Mono\", monospace; font-size: 11px; font-weight: 700; color: #999EA5; text-transform: uppercase; margin-bottom: 8px;'>Agentic Intelligence & Response</div>", unsafe_allow_html=True)
    tab_dispatch, tab_report, tab_rag, tab_perf, tab_mlflow = st.tabs([
        "Dispatches",
        "Final Report",
        "RAG Context",
        "Performance",
        "ML Models"
    ])

    with tab_dispatch:
        dispatch_placeholder = st.empty()

    with tab_report:
        report_placeholder = st.empty()

    with tab_rag:
        rag_placeholder = st.empty()

    with tab_perf:
        perf_placeholder = st.empty()

    with tab_mlflow:
        mlflow_winner_placeholder = st.empty()
        mlflow_table_placeholder = st.empty()

# 9. Render Intelligence Dossier ONCE per Streamlit Cycle
def render_incident_dossier(meta: Dict[str, Any]):
    p_state = meta.get("processing_state", "ANALYZING")
    final_res = meta.get("final_result") or st.session_state.get("final_result")

    if p_state == "COMPLETE" and final_res:
        st.session_state.final_result = final_res
        st.session_state.finalization_complete = True

        inc_type = str(final_res.get("type", "COLLISION")).upper()
        sev_label = str(final_res.get("severity_label", "High"))
        sev_score = int(final_res.get("severity_score", 85))
        inc_id = final_res.get("incident_id", "INC_001")
        card_class = f"incident-card incident-card-{sev_label.lower()}"
        icon = "💥" if inc_type == "COLLISION" else ("🔥" if inc_type == "FIRE" else ("🔄" if inc_type == "ROLLOVER" else "🛑"))

        incident_card_placeholder.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <span style="font-size: 15px; font-weight: 700; color: #D4D9DF;">Incident Confirmed — {icon} {inc_type}</span>
                    <span style="color: #999EA5; font-size: 11px; margin-left: 8px; font-family: 'IBM Plex Mono', monospace;">[{inc_id}]</span>
                </div>
                <div style="font-size: 13px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; color: {'#D9534F' if sev_label in ['Critical','High'] else '#C98255'};">
                    {sev_label.upper()} ({sev_score}/100)
                </div>
            </div>
            <div style="color: #999EA5; font-size: 12.5px; margin-bottom: 8px;">
                📍 <b>{meta['road_name']}</b> ({meta['camera_id']})
            </div>
            <div style="display: flex; gap: 14px; font-size: 11px; color: #798690; font-family: 'IBM Plex Mono', monospace;">
                <span>Vehicles: <b style="color: #D4D9DF;">{final_res.get('features', {}).get('vehicle_count', 1)}</b></span>
                <span>Pedestrian: <b style="color: #D4D9DF;">{'YES' if final_res.get('features', {}).get('person_on_road') else 'NO'}</b></span>
                <span>Fire: <b style="color: #D4D9DF;">{'YES' if final_res.get('features', {}).get('fire_smoke') else 'NO'}</b></span>
                <span>Rollover: <b style="color: #D4D9DF;">{'YES' if final_res.get('features', {}).get('rollover') else 'NO'}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plotly Gauge
        g_fig = build_gauge_fig(sev_score, sev_label)
        gauge_placeholder.plotly_chart(g_fig, use_container_width=True)

        # SHAP
        shap_vals = final_res.get("shap_values", {})
        if shap_vals:
            s_fig = build_shap_fig(shap_vals)
            shap_placeholder.plotly_chart(s_fig, use_container_width=True)

        # Dispatches
        dispatches = global_incident_store.get_dispatches()
        matched_d = [d for d in dispatches if d.get("target_incident") == inc_id]
        if matched_d:
            d_html = ""
            for d in matched_d:
                d_html += f"""
                <div style="background-color: #141517; border: 1px solid #394047; border-left: 3px solid #C98255; padding: 12px 14px; border-radius: 4px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: #D4D9DF; font-size: 13px;">{d.get('service')}</span>
                        <span class="badge-simulated">{d.get('badge', 'SIMULATED DISPATCH')}</span>
                    </div>
                    <div style="color: #999EA5; font-size: 11.5px; margin-top: 5px; font-family: 'IBM Plex Mono', monospace;">{d.get('message')}</div>
                </div>
                """
            dispatch_placeholder.markdown(d_html, unsafe_allow_html=True)

        # Report
        report_text = final_res.get("report_text", "Generating structured observation report...")
        report_placeholder.markdown(f"<div class='report-box'>{report_text}</div>", unsafe_allow_html=True)

        # RAG Context
        similar_list = global_rag_store.find_similar_incidents(final_res, top_k=2)
        if similar_list:
            rag_html = ""
            for sim in similar_list:
                rag_html += f"""
                <div style="background-color: #141517; border: 1px solid #394047; border-radius: 4px; padding: 12px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; font-weight: 600; color: #C98255; font-size: 12.5px;">
                        <span>#{sim.get('incident_id')} — {str(sim.get('type')).upper()}</span>
                        <span style="color: #999EA5;">Severity: {sim.get('severity')} ({sim.get('severity_score')}/100)</span>
                    </div>
                    <div style="color: #798690; font-size: 11px; margin-top: 2px; font-family: 'IBM Plex Mono', monospace;">📍 {sim.get('location')} | {sim.get('timestamp')}</div>
                    <div style="color: #999EA5; font-size: 12px; margin-top: 5px;">{sim.get('summary')}</div>
                </div>
                """
            rag_placeholder.markdown(rag_html, unsafe_allow_html=True)

    elif p_state == "FINAL_ANALYSIS":
        incident_card_placeholder.markdown("""
        <div style="background-color: #141517; border: 1px solid #394047; border-left: 3px solid #C98255; border-radius: 4px; padding: 16px 18px;">
            <div style="font-weight: 600; color: #C98255; font-size: 13.5px;">● ANALYZING</div>
            <div style="color: #999EA5; font-size: 12px; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">
                Video frames complete. Executing ML severity scoring, SHAP attribution, RAG context recall, and emergency dispatch decision.
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauge_placeholder.info("Severity scoring in progress...")
        shap_placeholder.info("Generating SHAP attribution...")
        dispatch_placeholder.info("Generating emergency dispatch decisions...")
        report_placeholder.info("Generating final GenAI report...")
        rag_placeholder.info("Querying ChromaDB RAG context...")

    else:
        # PROCESSING / ANALYZING STATE
        incident_card_placeholder.markdown("""
        <div style="background-color: #141517; border: 1px solid #394047; border-left: 3px solid #C98255; border-radius: 4px; padding: 16px 18px;">
            <div style="font-weight: 600; color: #C98255; font-size: 13.5px;">● MONITORING</div>
            <div style="color: #999EA5; font-size: 12px; margin-top: 4px; font-family: 'IBM Plex Mono', monospace;">
                YOLOv8 + ByteTrack observation active. Final classification, ML severity scoring, and emergency dispatch trigger upon video completion.
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauge_placeholder.info("Severity gauge will render upon video completion.")
        shap_placeholder.info("SHAP attribution will render upon video completion.")
        dispatch_placeholder.info("Simulated emergency dispatches will activate after final decision.")
        report_placeholder.info("GenAI Structured Incident Report will generate after video finishes.")
        rag_placeholder.info("ChromaDB historical incident recall will display with final decision.")

    # Performance Metrics Tab
    import psutil
    mem = psutil.virtual_memory()
    ram_used_gb = round(mem.used / (1024**3), 1)
    ram_total_gb = round(mem.total / (1024**3), 1)
    ram_pct = mem.percent
    cpu_pct = psutil.cpu_percent(interval=None)

    ram_color = "#D9534F" if ram_pct > 85 else "#55C98A"

    perf_html = f"""
    <div class="perf-box">
        <div style="color: #C98255; margin-bottom: 10px; font-weight: 600; font-family: 'IBM Plex Sans', sans-serif;">System Benchmarks</div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 12px; color: #999EA5;">
            <div>📹 <b>Video Duration</b>: <span style="color: #D4D9DF;">{meta.get('video_duration_s', 0)}s</span></div>
            <div>⏱️ <b>Processing Time</b>: <span style="color: #D4D9DF;">{meta.get('processing_duration_s', 0)}s</span></div>
            <div>⚡ <b>Inference FPS</b>: <span style="color: #C98255; font-weight: 600;">{meta.get('ai_fps', 0)} FPS</span></div>
            <div>🖥️ <b>Display FPS</b>: <span style="color: #C98255; font-weight: 600;">{meta.get('display_fps', 0)} FPS</span></div>
            <div>🔍 <b>Frames Inferred</b>: <span style="color: #D4D9DF;">{meta.get('frames_processed', 0)}</span></div>
            <div>⏭️ <b>Frames Skipped</b>: <span style="color: #D4D9DF;">{meta.get('frames_skipped', 0)}</span></div>
            <div>⚙️ <b>Engine</b>: <span style="color: #D4D9DF;">{DEVICE.upper()} (YOLOv8n + ByteTrack)</span></div>
            <div>🧠 <b>RAM Usage</b>: <span style="color: {ram_color}; font-weight: 600;">{ram_used_gb} GB / {ram_total_gb} GB ({ram_pct}%)</span></div>
            <div>💻 <b>CPU Usage</b>: <span style="color: #D4D9DF;">{cpu_pct}%</span></div>
            <div>📊 <b>Total Frames</b>: <span style="color: #D4D9DF;">{meta.get('total_frames', 0)}</span></div>
        </div>
    </div>
    """
    perf_placeholder.markdown(perf_html, unsafe_allow_html=True)

    # MLflow Model Comparison
    model_comp = get_model_comparison_metrics()
    mlflow_winner_placeholder.success(f"Winning Model: **{model_comp.get('winner')}**")
    models_data = model_comp.get("models", {})
    comp_rows = []
    for m_name, m_info in models_data.items():
        comp_rows.append({
            "Model": m_name,
            "R² Score": m_info.get("r2_score"),
            "RMSE": m_info.get("rmse"),
            "Accuracy": f"{m_info.get('accuracy', 0)*100:.1f}%",
            "F1": m_info.get("f1_weighted")
        })
    mlflow_table_placeholder.dataframe(comp_rows, use_container_width=True)

# 10. Frame-by-Frame Video Playback Loop
def run_video_stream():
    active_cid = st.session_state.get("active_camera_id", "CAM-01")
    worker = global_camera_manager.get_worker(active_cid)

    if not worker:
        return

    # Render Intelligence Dossier ONCE before entering video loop
    _, initial_meta = worker.get_frame_and_meta()
    render_incident_dossier(initial_meta)
    initial_p_state = initial_meta.get("processing_state")

    # High-FPS Frame Streaming Loop
    if st.session_state.get("is_streaming", True):
        for _ in range(30):
            rgb_frame, meta = worker.get_frame_and_meta()
            status_icon = "🟢 PLAYING" if meta["status"] == "PLAYING" else ("🟡 PAUSED" if meta["status"] == "PAUSED" else ("⚪ ENDED" if meta["status"] == "ENDED" else "🔴 ERROR"))
            p_state = meta.get("processing_state", "ANALYZING")

            if p_state == "ANALYZING":
                p_badge = "● MONITORING"
            elif p_state == "FINAL_ANALYSIS":
                p_badge = "● ANALYZING"
            else:
                p_badge = "● COMPLETE"

            pct = meta.get("progress_pct", 0)

            # Update Progress Bar
            cam_progress_placeholder.progress(pct / 100.0, text=f"Analysis Progress: {pct}% ({meta['frame_idx']}/{meta['total_frames']})")

            # Update Telemetry HUD Bar
            cam_meta_placeholder.markdown(
                f"<div class='hud-bar'>"
                f"<span>CAMERA: <code>{meta['camera_id']}</code></span> • "
                f"<span>ROAD: <code>{meta['road_name']}</code></span> • "
                f"<span>STATUS: <b>{p_badge}</b></span> • "
                f"<span>VIDEO FPS: <code>{meta['video_fps']}</code></span> • "
                f"<span>AI FPS: <code>{meta['ai_fps']}</code></span> • "
                f"<span>DISPLAY FPS: <code>{meta['display_fps']}</code></span> • "
                f"<span>PROCESSED: <code>{meta['frames_processed']}</code></span> • "
                f"<span>SKIPPED: <code>{meta['frames_skipped']}</code></span>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Update Video Frame
            if rgb_frame is not None:
                cam_video_placeholder.image(
                    rgb_frame,
                    caption=f"CCTV [{meta['camera_id']}] — {meta['road_name']} (Tracking: {meta['num_vehicles']} Vehicles, {meta['num_persons']} Pedestrians)",
                    use_container_width=True
                )

            # If video processing state transitioned, break loop to rerun and render dossier
            if p_state != initial_p_state:
                break

            time.sleep(0.04)

        # Rerun condition: keep loop going if playing, or if processing state changed, or if video ended but finalization is still running
        if meta["status"] == "PLAYING" or p_state != initial_p_state or (meta["status"] == "ENDED" and p_state != "COMPLETE"):
            st.rerun()
    else:
        rgb_frame, meta = worker.get_frame_and_meta()
        pct = meta.get("progress_pct", 0)
        cam_progress_placeholder.progress(pct / 100.0, text=f"Video Paused: {pct}%")
        cam_meta_placeholder.markdown(
            f"<div class='hud-bar'>"
            f"<span>CAMERA: <code>{meta['camera_id']}</code></span> • <span>ROAD: <code>{meta['road_name']}</code></span> • <span>STATUS: 🟡 PAUSED</span> • <span>VIDEO FPS: <code>{meta['video_fps']}</code></span> • <span>AI FPS: <code>{meta['ai_fps']}</code></span>"
            f"</div>",
            unsafe_allow_html=True
        )
        if rgb_frame is not None:
            cam_video_placeholder.image(
                rgb_frame,
                caption=f"CCTV [{meta['camera_id']}] — {meta['road_name']}",
                use_container_width=True
            )

run_video_stream()

st.markdown("<div style='border-bottom: 1px solid #394047; margin: 20px 0;'></div>", unsafe_allow_html=True)
st.caption("🛡️ RoadGuardian AI — Open Source Road Incident Intelligence")
