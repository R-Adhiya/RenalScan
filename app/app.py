import sys
import io
import time
import base64
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.pipeline.pipeline import RenalScanPipeline
from src.measurement.measure import ASSUMED_MM_PER_PIXEL, NON_CLINICAL_DISCLAIMER

# Page Configuration - Light Pastel Blue Workstation Theme Default
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Analysis Workstation",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS — Clinical Workstation Design System (Inter Font, Pastel Blue Palette, Aligned Grid)
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Pastel Blue Gradient Background */
    .stApp {
        background: linear-gradient(180deg, #EEF6FF 0%, #F5F9FF 50%, #EDF7FA 100%);
        color: #18253D;
    }
    
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1560px;
    }

    /* Workstation Top Navigation Bar */
    .rs-ws-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-radius: 18px;
        padding: 12px 28px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(60, 110, 170, 0.05);
    }
    .rs-logo-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .rs-logo-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #3B82F6 0%, #19B8B5 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.2rem;
    }
    .rs-logo-title-navy {
        font-size: 1.45rem;
        font-weight: 800;
        color: #18253D;
        letter-spacing: -0.02em;
    }
    .rs-logo-title-blue {
        color: #3B82F6;
        font-weight: 800;
    }
    .rs-logo-sub {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
    }
    .rs-btn-upload-nav {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 9px 22px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .rs-btn-upload-nav:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
    }

    /* Disclaimer Banner (Pastel Amber Notice Style) */
    .rs-notice-banner {
        background-color: #FFF8E8;
        border: 1px solid #F2D39A;
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.88rem;
        color: #785412;
    }
    .rs-notice-tag {
        font-weight: 800;
        color: #92400E;
    }
    .rs-notice-link {
        font-weight: 700;
        color: #3B82F6;
        cursor: pointer;
    }

    /* AI Pipeline 5-Step Workflow Bar */
    .rs-pipeline-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(60, 110, 170, 0.04);
    }
    .rs-step-item {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rs-step-badge {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.82rem;
        font-weight: 800;
    }
    .rs-sb-1 { background-color: #DDEEFF; color: #3B82F6; }
    .rs-sb-2 { background-color: #D5F5F4; color: #19B8B5; }
    .rs-sb-3 { background-color: #EAE4FF; color: #8B5CF6; }
    .rs-sb-4 { background-color: #FFD9C7; color: #F97316; }
    .rs-sb-5 { background-color: #CDEDDD; color: #10B981; }

    .rs-step-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #18253D;
    }
    .rs-step-status {
        font-size: 0.75rem;
        color: #10B981;
        font-weight: 600;
    }
    .rs-step-line {
        flex-grow: 1;
        height: 2px;
        background-color: #E2E8F0;
        margin: 0 16px;
    }

    /* Clinical Workstation Cards */
    .rs-ws-card {
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(60, 110, 170, 0.05);
        margin-bottom: 18px;
    }
    .rs-ws-card-title {
        font-size: 1.02rem;
        font-weight: 800;
        color: #18253D;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }

    /* Metadata Table Grid */
    .rs-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 16px;
    }
    .rs-meta-label {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 600;
    }
    .rs-meta-val {
        font-size: 0.88rem;
        color: #18253D;
        font-weight: 700;
    }

    /* CT Scan Viewer Canvas Container (Dark Navy Imaging Canvas #101827) */
    .rs-ct-canvas {
        background-color: #101827;
        border-radius: 20px;
        border: 1px solid #1F2937;
        padding: 20px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    }
    .rs-ct-canvas-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 1px solid #1F2937;
        margin-bottom: 14px;
    }
    .rs-ct-slice-txt {
        color: #9CA3AF;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .rs-ct-ready-txt {
        color: #19B8B5;
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Plain-English Summary Focal Card */
    .rs-summary-banner {
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-left: 5px solid #3B82F6;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 18px;
        font-size: 1.02rem;
        font-weight: 600;
        color: #18253D;
        line-height: 1.5;
        box-shadow: 0 4px 14px rgba(60, 110, 170, 0.05);
    }
    .rs-blue-bold {
        color: #3B82F6;
        font-weight: 800;
    }

    /* 3 Pastel Top Metric Cards */
    .rs-metrics-trio {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 18px;
    }
    .rs-metric-box {
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }
    .rs-mb-blue { background-color: #DDEEFF; border: 1px solid #B8D9FF; }
    .rs-mb-lavender { background-color: #C5B7F7; border: 1px solid #B4A2F5; color: #FFFFFF; }
    .rs-mb-teal { background-color: #19B8B5; border: 1px solid #14A09D; color: #FFFFFF; }

    .rs-metric-lbl {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 2px;
        opacity: 0.9;
    }
    .rs-metric-num {
        font-size: 1.55rem;
        font-weight: 800;
    }

    /* Compact Stone Finding Cards */
    .rs-finding-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.2s;
    }
    .rs-finding-card:hover {
        border-color: #3B82F6;
        background-color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
    }
    .rs-finding-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .rs-finding-id {
        font-weight: 800;
        font-size: 0.92rem;
        color: #18253D;
    }
    .rs-finding-conf {
        background-color: #D5F5F4;
        color: #0D9488;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 10px;
    }

    /* Anatomical Kidney Map Box */
    .rs-kidney-box {
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(60, 110, 170, 0.05);
    }
    .rs-kidney-flex {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 12px;
    }
    .rs-kidney-organ {
        width: 90px;
        height: 115px;
        background-color: #FFD6E0;
        border: 2px solid #F472B6;
        border-radius: 45% 55% 50% 50% / 60% 40% 60% 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        font-weight: 800;
        color: #9D174D;
        font-size: 0.85rem;
    }
    .rs-stone-pulse-dot {
        width: 14px;
        height: 14px;
        background-color: #3B82F6;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 8px #3B82F6;
        animation: pulseDot 1.5s infinite;
    }
    @keyframes pulseDot {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }

    /* Physical Measurement Value Table */
    .rs-meas-box {
        background-color: #FFFFFF;
        border: 1px solid #D7E6F5;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(60, 110, 170, 0.05);
    }
    .rs-meas-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }
    .rs-meas-table th {
        font-size: 0.78rem;
        color: #64748B;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 2px solid #E2E8F0;
    }
    .rs-meas-table td {
        font-size: 0.88rem;
        padding: 12px 14px;
        border-bottom: 1px solid #E2E8F0;
        color: #18253D;
        font-weight: 600;
    }
    .rs-meas-val-cell {
        background-color: #F0F7FF;
        color: #3B82F6 !important;
        font-weight: 800 !important;
        border-radius: 6px;
    }

    /* Footer */
    .rs-ws-footer {
        margin-top: 40px;
        padding: 24px;
        border-top: 1px solid #D7E6F5;
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Pipeline Loader
@st.cache_resource
def get_pipeline():
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=ASSUMED_MM_PER_PIXEL)

pipeline = get_pipeline()

# Session State Initializations
if 'active_image' not in st.session_state:
    st.session_state['active_image'] = None
if 'active_sample_name' not in st.session_state:
    st.session_state['active_sample_name'] = None

sample_dir = PROJECT_ROOT / "data" / "test" / "images"
sample_files = sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []

# Default to first sample if active_image is None
if st.session_state['active_image'] is None and len(sample_files) > 0:
    bgr = cv2.imread(str(sample_files[0]))
    st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    st.session_state['active_sample_name'] = sample_files[0].name

# Encode sample CT image to base64 for HTML animation
sample_b64 = ""
if len(sample_files) > 0:
    with open(sample_files[0], "rb") as img_f:
        sample_b64 = base64.b64encode(img_f.read()).decode()

# -----------------------------------------------------------------------------
# 1. WORKSTATION TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
nav_col1, nav_col2, nav_col3 = st.columns([2, 3.2, 1])
with nav_col1:
    st.markdown("""
    <div class="rs-logo-group">
        <div class="rs-logo-icon">🩺</div>
        <div>
            <div><span class="rs-logo-title-navy">Renal</span><span class="rs-logo-title-blue">Scan</span></div>
            <div class="rs-logo-sub">AI Kidney Stone Analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    tab1, tab2 = st.tabs(["📊 Workstation Dashboard", "🔬 How RenalScan Works (Interactive AI Pipeline)"])

with nav_col3:
    st.markdown('<button class="rs-btn-upload-nav">📤 Upload New CT Scan</button>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: INTERACTIVE ANIMATED "HOW RENALSCAN WORKS" PIPELINE SECTION
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #D7E6F5; border-radius: 18px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(60, 110, 170, 0.04);">
        <h2 style="color: #18253D; font-weight: 800; margin-bottom: 4px;">HOW RENALSCAN WORKS</h2>
        <p style="color: #64748B; font-size: 1rem; font-weight: 500; margin-bottom: 20px;">From abdominal CT scan input to AI-powered quantitative kidney stone measurement.</p>
    </div>
    """, unsafe_allow_html=True)

    # HTML/CSS/JS Interactive Animated Pipeline Visualization Component
    animated_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #EEF6FF;
                margin: 0;
                padding: 10px;
                color: #18253D;
            }}
            .card-container {{
                background-color: #FFFFFF;
                border: 1px solid #D7E6F5;
                border-radius: 20px;
                padding: 24px;
                box-shadow: 0 8px 30px rgba(60, 110, 170, 0.08);
            }}
            .ct-canvas {{
                background-color: #101827;
                border-radius: 18px;
                position: relative;
                width: 100%;
                height: 440px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 10px 28px rgba(0,0,0,0.3);
            }}
            .ct-img {{
                max-height: 420px;
                max-width: 420px;
                border-radius: 8px;
                transition: opacity 0.5s, filter 0.5s;
            }}
            /* Scanning Beam Line */
            .scan-line {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, #19B8B5, transparent);
                box-shadow: 0 0 12px #19B8B5;
                animation: scanMove 3s infinite linear;
                opacity: 0.8;
            }}
            @keyframes scanMove {{
                0% {{ top: 5%; }}
                50% {{ top: 90%; }}
                100% {{ top: 5%; }}
            }}
            /* SVG Contour & Vector Layer */
            .svg-layer {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }}
            .yolo-box {{
                stroke: #FFD9C7;
                stroke-width: 2.5;
                stroke-dasharray: 6 4;
                fill: rgba(255, 217, 199, 0.12);
                transition: all 0.5s;
            }}
            .otsu-contour {{
                stroke: #19B8B5;
                stroke-width: 3;
                fill: rgba(25, 184, 181, 0.25);
                stroke-dasharray: 400;
                stroke-dashoffset: 400;
                transition: stroke-dashoffset 1.5s ease-in-out;
            }}
            .draw-contour {{
                stroke-dashoffset: 0 !important;
            }}
            .meas-vector {{
                stroke: #3B82F6;
                stroke-width: 2.5;
                stroke-dasharray: 4;
            }}
            /* Floating Labels & Badges */
            .badge-floating {{
                position: absolute;
                background: rgba(16, 24, 39, 0.85);
                backdrop-filter: blur(4px);
                border: 1px solid #3B82F6;
                color: #FFFFFF;
                padding: 5px 12px;
                border-radius: 8px;
                font-size: 0.82rem;
                font-weight: 700;
                transition: opacity 0.5s, transform 0.5s;
            }}
            /* Step Control Buttons Bar */
            .ctrl-bar {{
                display: flex;
                gap: 12px;
                justify-content: center;
                margin-top: 20px;
            }}
            .step-btn {{
                background-color: #FFFFFF;
                border: 1px solid #D7E6F5;
                color: #18253D;
                font-weight: 700;
                font-size: 0.88rem;
                padding: 10px 18px;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .step-btn:hover, .step-btn.active {{
                background-color: #DDEEFF;
                border-color: #3B82F6;
                color: #3B82F6;
            }}
            /* Stage Timeline Bar */
            .timeline-bar {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 8px;
                margin-top: 20px;
                text-align: center;
            }}
            .t-stage {{
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 10px;
                font-size: 0.78rem;
                font-weight: 700;
                color: #64748B;
                transition: all 0.3s;
            }}
            .t-stage.active-stage {{
                background-color: #DDEEFF;
                border-color: #3B82F6;
                color: #3B82F6;
                transform: scale(1.03);
            }}
        </style>
    </head>
    <body>
        <div class="card-container">
            <div class="ct-canvas">
                <div class="scan-line"></div>
                <img src="data:image/jpeg;base64,{sample_b64}" class="ct-img" id="ctImg">
                
                <svg class="svg-layer" viewBox="0 0 600 440">
                    <rect id="yoloBox" x="250" y="160" width="100" height="90" class="yolo-box" opacity="0"/>
                    <path id="otsuContour" d="M 270,180 Q 320,165 335,200 T 310,235 T 265,220 Z" class="otsu-contour"/>
                    <line id="vecMajor" x1="260" y1="200" x2="340" y2="200" class="meas-vector" opacity="0"/>
                    <line id="vecMinor" x1="300" y1="170" x2="300" y2="230" class="meas-vector" opacity="0"/>
                </svg>

                <div id="stageBadge" class="badge-floating" style="top: 20px; left: 20px;">01 CT SCAN INPUT</div>
                <div id="confBadge" class="badge-floating" style="top: 20px; right: 20px; opacity: 0; background: rgba(25, 184, 181, 0.9);">CONFIDENCE: 87.4%</div>
                <div id="readoutBadge" class="badge-floating" style="bottom: 20px; right: 20px; opacity: 0; background: rgba(59, 130, 246, 0.9);">DIMENSIONS: 8.2mm × 5.4mm</div>
            </div>

            <div class="timeline-bar">
                <div id="t1" class="t-stage active-stage">01 CT Preprocess</div>
                <div id="t2" class="t-stage">02 YOLOv8 Detect</div>
                <div id="t3" class="t-stage">03 Otsu Segment</div>
                <div id="t4" class="t-stage">04 Measure Geometry</div>
                <div id="t5" class="t-stage">05 Analysis Report</div>
            </div>

            <div class="ctrl-bar">
                <button class="step-btn" onclick="jumpTo(1)">01 Detect</button>
                <button class="step-btn" onclick="jumpTo(2)">02 Segment</button>
                <button class="step-btn" onclick="jumpTo(3)">03 Measure</button>
                <button class="step-btn" onclick="jumpTo(4)">04 Result</button>
                <button class="step-btn" onclick="replay()">🔄 Replay Loop</button>
            </div>
        </div>

        <script>
            let currentStep = 1;
            let timer = null;

            function updateStage(step) {{
                currentStep = step;
                const badge = document.getElementById('stageBadge');
                const conf = document.getElementById('confBadge');
                const readout = document.getElementById('readoutBadge');
                const yolo = document.getElementById('yoloBox');
                const contour = document.getElementById('otsuContour');
                const vecMaj = document.getElementById('vecMajor');
                const vecMin = document.getElementById('vecMinor');

                for(let i=1; i<=5; i++) {{
                    document.getElementById('t' + i).classList.remove('active-stage');
                }}

                if (step === 1) {{
                    badge.innerText = "01 CT SCAN & PREPROCESSING";
                    document.getElementById('t1').classList.add('active-stage');
                    yolo.setAttribute('opacity', '0');
                    contour.classList.remove('draw-contour');
                    vecMaj.setAttribute('opacity', '0');
                    vecMin.setAttribute('opacity', '0');
                    conf.style.opacity = '0';
                    readout.style.opacity = '0';
                }} else if (step === 2) {{
                    badge.innerText = "02 YOLOV8 STONE DETECTION";
                    document.getElementById('t2').classList.add('active-stage');
                    yolo.setAttribute('opacity', '1');
                    conf.style.opacity = '1';
                    contour.classList.remove('draw-contour');
                    vecMaj.setAttribute('opacity', '0');
                    vecMin.setAttribute('opacity', '0');
                    readout.style.opacity = '0';
                }} else if (step === 3) {{
                    badge.innerText = "03 OTSU ROI SEGMENTATION";
                    document.getElementById('t3').classList.add('active-stage');
                    yolo.setAttribute('opacity', '1');
                    conf.style.opacity = '1';
                    contour.classList.add('draw-contour');
                    vecMaj.setAttribute('opacity', '0');
                    vecMin.setAttribute('opacity', '0');
                    readout.style.opacity = '0';
                }} else if (step === 4) {{
                    badge.innerText = "04 GEOMETRY AXIS MEASUREMENT";
                    document.getElementById('t4').classList.add('active-stage');
                    yolo.setAttribute('opacity', '1');
                    conf.style.opacity = '1';
                    contour.classList.add('draw-contour');
                    vecMaj.setAttribute('opacity', '1');
                    vecMin.setAttribute('opacity', '1');
                    readout.style.opacity = '1';
                }} else if (step === 5) {{
                    badge.innerText = "05 ANALYSIS REPORT GENERATION";
                    document.getElementById('t5').classList.add('active-stage');
                    yolo.setAttribute('opacity', '1');
                    conf.style.opacity = '1';
                    contour.classList.add('draw-contour');
                    vecMaj.setAttribute('opacity', '1');
                    vecMin.setAttribute('opacity', '1');
                    readout.style.opacity = '1';
                }}
            }}

            function autoLoop() {{
                currentStep = (currentStep % 5) + 1;
                updateStage(currentStep);
            }}

            function jumpTo(step) {{
                clearInterval(timer);
                updateStage(step === 4 ? 5 : step + 1);
            }}

            function replay() {{
                clearInterval(timer);
                currentStep = 1;
                updateStage(1);
                timer = setInterval(autoLoop, 4000);
            }}

            timer = setInterval(autoLoop, 4000);
        </script>
    </body>
    </html>
    """

    components.html(animated_html, height=620, scrolling=False)

# -----------------------------------------------------------------------------
# 2. RESEARCH & EDUCATIONAL PROTOTYPE DISCLAIMER BANNER
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="rs-notice-banner">
    <div>
        <span>ⓘ</span>
        <span><span class="rs-notice-tag">Research & Educational Prototype:</span> Measurements are literature-based estimates ({ASSUMED_MM_PER_PIXEL} mm/px FOV constant). This software is intended for technical evaluation and portfolio demonstration — not for clinical diagnosis or surgical decision-making.</span>
    </div>
    <div class="rs-notice-link">Learn more →</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. AI PIPELINE 5-STEP WORKFLOW BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-pipeline-bar">
    <div class="rs-step-item">
        <div class="rs-step-badge rs-sb-1">01</div>
        <div>
            <div class="rs-step-title">Preprocess</div>
            <div class="rs-step-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-step-line"></div>
    <div class="rs-step-item">
        <div class="rs-step-badge rs-sb-2">02</div>
        <div>
            <div class="rs-step-title">YOLOv8 Detect</div>
            <div class="rs-step-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-step-line"></div>
    <div class="rs-step-item">
        <div class="rs-step-badge rs-sb-3">03</div>
        <div>
            <div class="rs-step-title">Otsu Segment</div>
            <div class="rs-step-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-step-line"></div>
    <div class="rs-step-item">
        <div class="rs-step-badge rs-sb-4">04</div>
        <div>
            <div class="rs-step-title">Geometry Measure</div>
            <div class="rs-step-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-step-line"></div>
    <div class="rs-step-item">
        <div class="rs-step-badge rs-sb-5">05</div>
        <div>
            <div class="rs-step-title">Generate Report</div>
            <div class="rs-step-status">Complete ✓</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 1: WORKSTATION DASHBOARD WORKSPACE
# -----------------------------------------------------------------------------
with tab1:
    # OPTIMAL 3-COLUMN WORKSTATION PROPORTIONS (1.1 | 2.8 | 1.4)
    col_left, col_center, col_right = st.columns([1.1, 2.8, 1.4])

    # --- LEFT PANEL: CONTROLS & METADATA (1.1) ---
    with col_left:
        st.markdown('<div class="rs-ws-card"><div class="rs-ws-card-title">📤 Upload CT Scan</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload CT Scan Image (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            help="Drag & drop or browse for abdominal CT scan slice."
        )
        if uploaded_file is not None:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if bgr_img is not None:
                st.session_state['active_image'] = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = uploaded_file.name
        st.markdown('</div>', unsafe_allow_html=True)

        # Scan Information Metadata Grid
        st.markdown('<div class="rs-ws-card"><div class="rs-ws-card-title">ℹ️ Scan Information</div>', unsafe_allow_html=True)
        scan_name = st.session_state['active_sample_name'] if st.session_state['active_sample_name'] else "RS-2026-001"
        st.markdown(f"""
        <div class="rs-meta-grid">
            <div>
                <div class="rs-meta-label">Scan ID</div>
                <div class="rs-meta-val">RS-2026-001</div>
            </div>
            <div>
                <div class="rs-meta-label">Image Format</div>
                <div class="rs-meta-val">CT Abdominal</div>
            </div>
            <div>
                <div class="rs-meta-label">Slice</div>
                <div class="rs-meta-val">034 / 128</div>
            </div>
            <div>
                <div class="rs-meta-label">Processing</div>
                <div class="rs-meta-val">2.4 sec</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Sample Scans Selection
        st.markdown('<div class="rs-ws-card"><div class="rs-ws-card-title">🧪 Sample CT Scans</div>', unsafe_allow_html=True)
        if len(sample_files) >= 3:
            if st.button("Sample 01 (Multiple Stones)", key="b1", use_container_width=True):
                bgr = cv2.imread(str(sample_files[0]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[0].name
                st.rerun()
            if st.button("Sample 02 (Single Stone)", key="b2", use_container_width=True):
                bgr = cv2.imread(str(sample_files[1]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[1].name
                st.rerun()
            if st.button("Sample 03 (Normal Scan)", key="b3", use_container_width=True):
                bgr = cv2.imread(str(sample_files[2]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[2].name
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Analysis Controls
        st.markdown('<div class="rs-ws-card"><div class="rs-ws-card-title">🎛️ Analysis Controls</div>', unsafe_allow_html=True)
        conf_thresh = st.slider("Confidence Threshold", 0.10, 0.90, 0.40, step=0.05)
        
        overlay_mode = st.radio(
            "Visualization Overlay",
            options=["3. Measurement Axes", "2. Segmentation Masks", "1. YOLOv8 Detections", "Original CT Scan"],
            index=0
        )
        
        brightness = st.slider("Brightness", -50, 50, 0, step=5)
        contrast = st.slider("Contrast", -50, 50, 0, step=5)
        
        if st.button("Reset All Controls", use_container_width=True):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Apply image brightness/contrast adjustments
    processed_img = st.session_state['active_image'].copy() if st.session_state['active_image'] is not None else np.zeros((512,512,3), dtype=np.uint8)
    if brightness != 0 or contrast != 0:
        processed_img = cv2.convertScaleAbs(processed_img, alpha=1.0 + (contrast/100.0), beta=brightness)

    # Run End-to-End Model Pipeline
    with st.spinner("Analyzing CT scan — detecting, segmenting, and measuring stones..."):
        result = pipeline.analyze(processed_img, conf_thresh=conf_thresh)

    summary = result['summary']
    stones = result['stones']

    # --- CENTER PANEL: CT SCAN VIEWER WORKSTATION (2.8) ---
    with col_center:
        st.markdown("""
        <div class="rs-ct-canvas">
            <div class="rs-ct-canvas-header">
                <span class="rs-ct-slice-txt">CT ABDOMINAL SCAN | Slice 034 / 128</span>
                <span class="rs-ct-ready-txt">● AI ANALYSIS READY</span>
            </div>
        """, unsafe_allow_html=True)
        
        if overlay_mode == "1. YOLOv8 Detections":
            st.image(result['annotated_detection'], use_container_width=True)
        elif overlay_mode == "2. Segmentation Masks":
            st.image(result['annotated_segmentation'], use_container_width=True)
        elif overlay_mode == "3. Measurement Axes":
            st.image(result['annotated_measurement'], use_container_width=True)
        else:
            st.image(result['original_image'], use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

        # Before vs After Comparison Expander
        with st.expander("🔍 Before / After Segmentation Preview"):
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Original CT Scan")
                st.image(result['original_image'], use_container_width=True)
            with c2:
                st.caption("AI Segmentation Overlay")
                st.image(result['annotated_segmentation'], use_container_width=True)

    # --- RIGHT PANEL: AI ANALYSIS RESULTS (1.4) ---
    with col_right:
        st.markdown("### AI Analysis Results")
        st.markdown("<span style='color: #10B981; font-weight: 700; font-size: 0.85rem;'>● Analysis Complete</span>", unsafe_allow_html=True)
        st.write("")

        if not summary['has_stones']:
            st.warning(f"ℹ️ **No Stone Regions Detected**: No candidate stone regions detected above threshold {conf_thresh:.2f}.")
        else:
            largest_mm = summary['largest_stone_diameter_mm']
            largest_band = summary['largest_stone_size_band']
            stone_count = summary['stone_count']

            if "<4mm" in largest_band:
                guidance = "typically passes on its own with hydration"
            elif "4-6mm" in largest_band:
                guidance = "may require medical expulsion observation"
            elif "6-10mm" in largest_band:
                guidance = "usually requires a procedure"
            else:
                guidance = "usually requires surgical intervention"

            st.markdown(f"""
            <div class="rs-summary-banner">
                💡 Scan shows <span class="rs-blue-bold">{stone_count} stone(s)</span>. Largest is <span class="rs-blue-bold">{largest_mm:.2f} mm</span>, which {guidance}.
            </div>
            """, unsafe_allow_html=True)

            # 3 Pastel Top Metric Cards
            st.markdown("""
            <div class="rs-metrics-trio">
                <div class="rs-metric-box rs-mb-blue">
                    <div class="rs-metric-lbl" style="color: #3B82F6;">Total Stones</div>
                    <div class="rs-metric-num" style="color: #18253D;">{count}</div>
                </div>
                <div class="rs-metric-box rs-mb-lavender">
                    <div class="rs-metric-lbl">Largest Size</div>
                    <div class="rs-metric-num">{mm} mm</div>
                </div>
                <div class="rs-metric-box rs-mb-teal">
                    <div class="rs-metric-lbl">Confidence</div>
                    <div class="rs-metric-num">{conf}%</div>
                </div>
            </div>
            """.format(
                count=stone_count,
                mm=f"{largest_mm:.1f}",
                conf=f"{stones[0]['confidence']*100:.0f}" if len(stones)>0 else "0"
            ), unsafe_allow_html=True)

            # Compact Stone Findings Cards
            st.markdown("#### Detected Stone Regions")
            for s in stones:
                if s.get('status') == 'Success':
                    st.markdown(f"""
                    <div class="rs-finding-card">
                        <div class="rs-finding-head">
                            <span class="rs-finding-id">Stone #{s['stone_id']}</span>
                            <span class="rs-finding-conf">{s['confidence']*100:.1f}% Conf</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748B;">
                            • <strong>Location:</strong> Kidney Region ROI<br>
                            • <strong>Dimensions:</strong> {s['estimated_major_mm']:.1f} × {s['estimated_minor_mm']:.1f} mm<br>
                            • <strong>Est. Diameter:</strong> {s['estimated_diameter_mm']:.2f} mm*<br>
                            • <strong>Treatment Category:</strong> {s['clinical_size_band']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 5. LOWER SECTION: KIDNEY LOCATION & PHYSICAL MEASUREMENT TABLE (1 : 1.6)
    # -----------------------------------------------------------------------------
    st.markdown("---")
    low_col1, low_col2 = st.columns([1, 1.6])

    with low_col1:
        st.markdown("""
        <div class="rs-kidney-box">
            <div style="font-weight: 800; font-size: 1rem; color: #18253D;">🫘 Kidney Location Map</div>
            <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">Anatomical Renal Region Markers</div>
            <div class="rs-kidney-flex">
                <div class="rs-kidney-organ">
                    Left (L)
                    <div class="rs-stone-pulse-dot" style="top: 35px; left: 32px;"></div>
                </div>
                <div class="rs-kidney-organ">
                    Right (R)
                    <div class="rs-stone-pulse-dot" style="top: 55px; left: 38px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with low_col2:
        if summary['has_stones'] and len(stones) > 0 and stones[0].get('status') == 'Success':
            s1 = stones[0]
            st.markdown("""
            <div class="rs-meas-box">
                <div style="font-weight: 800; font-size: 1rem; color: #18253D; margin-bottom: 8px;">📊 Physical Measurements (Stone #1)</div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <table class="rs-meas-table">
                <thead>
                    <tr>
                        <th>Measurement Metric</th>
                        <th>Extracted Dimension Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Major Axis Length</td>
                        <td class="rs-meas-val-cell">{s1['estimated_major_mm']:.1f} mm ({s1['major_axis_px']:.1f} px)</td>
                    </tr>
                    <tr>
                        <td>Minor Axis Length</td>
                        <td class="rs-meas-val-cell">{s1['estimated_minor_mm']:.1f} mm ({s1['minor_axis_px']:.1f} px)</td>
                    </tr>
                    <tr>
                        <td>Mask Area</td>
                        <td class="rs-meas-val-cell">{s1['area_px']:.1f} px²</td>
                    </tr>
                    <tr>
                        <td>Equivalent Diameter</td>
                        <td class="rs-meas-val-cell">{s1['estimated_diameter_mm']:.2f} mm ({s1['equiv_diameter_px']:.1f} px)</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)
            st.caption(f"*DISCLAIMER: {NON_CLINICAL_DISCLAIMER}")
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 6. EXPORT SECTION
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📄 Export & Reports")

    if summary['has_stones']:
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            report_text = f"RenalScan AI Diagnostic Report\nScan: {st.session_state['active_sample_name']}\nStones: {summary['stone_count']}\nLargest: {summary['largest_stone_diameter_mm']} mm\n"
            for s in stones:
                report_text += f"- Stone #{s['stone_id']}: {s['estimated_diameter_mm']:.2f}mm ({s['clinical_size_band']})\n"
            report_text += f"\nDISCLAIMER: {NON_CLINICAL_DISCLAIMER}\n"
            
            st.download_button(
                "📄 Download Analysis Report (.txt)",
                data=report_text,
                file_name="RenalScan_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
        with exp_col2:
            df_export = pd.DataFrame([{
                'Stone ID': f"Stone #{s['stone_id']}",
                'Confidence': s['confidence'],
                'Area_px': s['area_px'],
                'Major_mm': s['estimated_major_mm'],
                'Minor_mm': s['estimated_minor_mm'],
                'Diameter_mm': s['estimated_diameter_mm'],
                'Category': s['clinical_size_band']
            } for s in stones if s.get('status') == 'Success'])
            
            st.download_button(
                "📊 Export Measurements CSV (.csv)",
                data=df_export.to_csv(index=False),
                file_name="RenalScan_Measurements.csv",
                mime="text/csv",
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-ws-footer">
    <strong>RenalScan</strong> — AI-Powered Kidney Stone Analysis Workstation | Research & Educational Prototype<br>
    Built for Technical Portfolio Evaluation & Medical Computer Vision Demonstration
</div>
""", unsafe_allow_html=True)
