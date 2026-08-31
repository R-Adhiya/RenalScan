import sys
import io
import time
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import streamlit as st

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
        max-width: 1540px;
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
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #3B82F6 0%, #19B8B5 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.15rem;
    }
    .rs-logo-title-navy {
        font-size: 1.4rem;
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
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 6px 24px rgba(60, 110, 170, 0.06);
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
        padding: 18px;
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
        padding: 16px;
        text-align: center;
    }
    .rs-kidney-flex {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 8px;
    }
    .rs-kidney-organ {
        width: 85px;
        height: 110px;
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
    .rs-meas-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }
    .rs-meas-table th {
        font-size: 0.78rem;
        color: #64748B;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 2px solid #E2E8F0;
    }
    .rs-meas-table td {
        font-size: 0.88rem;
        padding: 10px 12px;
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

# -----------------------------------------------------------------------------
# 1. WORKSTATION TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-ws-navbar">
    <div class="rs-logo-group">
        <div class="rs-logo-icon">🩺</div>
        <div>
            <div><span class="rs-logo-title-navy">Renal</span><span class="rs-logo-title-blue">Scan</span></div>
            <div class="rs-logo-sub">AI Kidney Stone Analysis</div>
        </div>
    </div>
    <div>
        <button class="rs-btn-upload-nav">📤 Upload New CT Scan</button>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. NOTICE DISCLAIMER BANNER
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

# -----------------------------------------------------------------------------
# 4. MAIN WORKSPACE (3-COLUMN ALIGNED GRID: 20% | 55% | 25%)
# -----------------------------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 2.7, 1.3])

# --- LEFT PANEL: CONTROLS & METADATA (20%) ---
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

    # Sample Scans Dropdown Selection
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

# --- CENTER PANEL: CT SCAN VIEWER WORKSTATION (55%) ---
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

# --- RIGHT PANEL: AI ANALYSIS RESULTS (25%) ---
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
# 5. LOWER SECTION: KIDNEY LOCATION & PHYSICAL MEASUREMENT TABLE
# -----------------------------------------------------------------------------
st.markdown("---")
low_col1, low_col2 = st.columns([1, 1.4])

with low_col1:
    st.markdown("""
    <div class="rs-kidney-box">
        <div style="font-weight: 800; font-size: 0.95rem; color: #18253D;">🫘 Kidney Location Map</div>
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 8px;">Anatomical Renal Region Markers</div>
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
        st.markdown("### Physical Measurements (Stone #1)")
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

# -----------------------------------------------------------------------------
# 6. EXPORT SECTION & FOOTER
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

st.markdown("""
<div class="rs-ws-footer">
    <strong>RenalScan</strong> — AI-Powered Kidney Stone Analysis Workstation | Research & Educational Prototype<br>
    Built for Technical Portfolio Evaluation & Medical Computer Vision Demonstration
</div>
""", unsafe_allow_html=True)
