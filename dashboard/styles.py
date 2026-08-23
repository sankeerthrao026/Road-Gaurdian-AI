DARK_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    /* 1. Global Root Container & Technical Grid Background */
    html, body, .stApp, [data-testid="stAppViewContainer"], .stMain, [data-testid="stHeader"] {
        background-color: #0D0E10 !important;
        background-image: 
            linear-gradient(rgba(57, 64, 71, 0.12) 1px, transparent 1px),
            linear-gradient(90deg, rgba(57, 64, 71, 0.12) 1px, transparent 1px) !important;
        background-size: 32px 32px !important;
        color: #D4D9DF !important;
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Hide default Streamlit header bar */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 95% !important;
    }

    /* Minimal Technical Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: #0D0E10;
    }
    ::-webkit-scrollbar-thumb {
        background: #394047;
        border-radius: 2px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #C98255;
    }

    /* 2. Editorial Header Container */
    .dribbble-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0 16px 0;
        border-bottom: 1px solid #394047;
        margin-bottom: 20px;
    }

    .brand-title {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #D4D9DF;
        text-transform: uppercase;
    }

    .brand-subtitle {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #798690;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    .system-status-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        color: #999EA5;
        background: #141517;
        border: 1px solid #394047;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot-warm {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #C98255;
        display: inline-block;
    }

    /* 3. Section Divider Headers */
    .dribbble-section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #C98255;
        margin-top: 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 1px solid #394047;
        padding-bottom: 6px;
    }

    /* 4. Cards & Surface Containers */
    .dribbble-card {
        background-color: #141517;
        border: 1px solid #394047;
        border-radius: 6px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }

    .incident-card {
        background-color: #141517;
        border: 1px solid #394047;
        border-left: 3px solid #C98255;
        border-radius: 6px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }

    .incident-card-critical {
        border-left-color: #D9534F !important;
        background-color: #1A1516;
        border-color: rgba(217, 83, 79, 0.4);
    }

    .incident-card-high {
        border-left-color: #C98255 !important;
        background-color: #1B1714;
        border-color: rgba(201, 130, 85, 0.4);
    }

    .incident-card-medium {
        border-left-color: #C98255 !important;
        border-color: rgba(201, 130, 85, 0.3);
    }

    .incident-card-low {
        border-left-color: #55C98A !important;
        border-color: rgba(85, 201, 138, 0.3);
    }

    /* 5. Badge Styling */
    .badge-simulated {
        background-color: #1B1D20;
        color: #999EA5;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border: 1px solid #394047;
    }

    /* 6. Report Box - Technical Analysis Document Style */
    .report-box {
        background-color: #141517;
        border: 1px solid #394047;
        border-top: 2px solid #C98255;
        border-radius: 6px;
        padding: 16px 18px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        line-height: 1.7;
        color: #D4D9DF;
        white-space: pre-wrap;
    }

    /* 7. Telemetry HUD Bar - Technical Readout Row */
    .hud-bar {
        background-color: #141517;
        border: 1px solid #394047;
        border-radius: 4px;
        padding: 8px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #999EA5;
        margin-bottom: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
    }

    .hud-bar code {
        color: #D4D9DF !important;
        background: transparent !important;
        padding: 0 !important;
        font-weight: 600;
    }

    /* 8. Streamlit Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0D0E10 !important;
        border-right: 1px solid #394047 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #D4D9DF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
    }

    /* 9. Streamlit Buttons Styling */
    [data-testid="stButton"] button {
        background-color: #1B1D20 !important;
        color: #D4D9DF !important;
        border: 1px solid #394047 !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }

    [data-testid="stButton"] button:hover {
        background-color: #242930 !important;
        border-color: #C98255 !important;
        color: #C98255 !important;
    }

    [data-testid="stButton"] button[kind="primary"] {
        background-color: #1F1B18 !important;
        border-color: #C98255 !important;
        color: #C98255 !important;
    }

    /* 10. Streamlit Selectboxes */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #141517 !important;
        border: 1px solid #394047 !important;
        border-radius: 4px !important;
        color: #D4D9DF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11.5px !important;
    }

    /* 11. Streamlit Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 4px !important;
        background-color: transparent !important;
        padding: 0 !important;
        border-bottom: 1px solid #394047 !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        height: 36px !important;
        background-color: transparent !important;
        border: none !important;
        color: #798690 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 0 14px !important;
        text-transform: uppercase !important;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        background-color: transparent !important;
        color: #C98255 !important;
        border-bottom: 2px solid #C98255 !important;
    }

    /* 12. Streamlit Alerts */
    [data-testid="stAlert"] {
        background-color: #141517 !important;
        border: 1px solid #394047 !important;
        border-radius: 4px !important;
        color: #999EA5 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11.5px !important;
    }

    /* 13. Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #C98255 !important;
        border-radius: 2px !important;
    }

    .perf-box {
        background-color: #141517;
        border: 1px solid #394047;
        border-radius: 6px;
        padding: 16px;
        font-family: 'IBM Plex Mono', monospace;
    }
</style>
"""
