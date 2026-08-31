import sys
import io
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

# Page Configuration - Light Pastel Blue Theme Default
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS — Full Overhaul into Light Pastel Blue Design System
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
        background: linear-gradient(180deg, #EEF5FF 0%, #F5F9FF 50%, #EDF7FA 100%);
        color: #16233B;
    }
    
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1520px;
    }

    /* Top Navigation Bar */
    .rs-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #D9E6F5;
        border-radius: 18px;
        padding: 12px 28px;
        margin-bottom: 20px;
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
        background: linear-gradient(135deg, #2F80ED 0%, #20B8B5 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.15rem;
    }
    .rs-logo-text-main {
        font-size: 1.4rem;
        font-weight: 800;
        color: #16233B;
        letter-spacing: -0.02em;
    }
    .rs-logo-text-accent {
        color: #2F80ED;
        font-weight: 800;
    }
    .rs-logo-subtitle {
        font-size: 0.78rem;
        color: #60708A;
        font-weight: 500;
    }
    .rs-nav-links {
        display: flex;
        gap: 32px;
        font-size: 0.92rem;
        font-weight: 600;
        color: #60708A;
    }
    .rs-nav-link {
        color: #60708A;
        text-decoration: none;
        cursor: pointer;
        transition: color 0.2s;
    }
    .rs-nav-link:hover, .rs-nav-link.active {
        color: #2F80ED;
    }
    .rs-btn-upload {
        background: linear-gradient(135deg, #2F80ED 0%, #4AA3FF 100%);
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 9px 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(47, 128, 237, 0.25);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .rs-btn-upload:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(47, 128, 237, 0.35);
    }

    /* Disclaimer Banner (Pastel Amber Notice) */
    .rs-disclaimer-banner {
        background-color: #FFF8E8;
        border: 1px solid #F2D39A;
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.88rem;
        color: #785412;
    }
    .rs-disclaimer-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rs-disclaimer-tag {
        font-weight: 800;
        color: #92400E;
    }
    .rs-disclaimer-link {
        font-weight: 700;
        color: #2F80ED;
        cursor: pointer;
    }

    /* 5-Step Workflow Bar */
    .rs-workflow-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #D9E6F5;
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(60, 110, 170, 0.04);
    }
    .rs-wf-step {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rs-wf-badge {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.82rem;
        font-weight: 800;
    }
    .rs-wf-1 { background-color: #DCEEFF; color: #2F80ED; }
    .rs-wf-2 { background-color: #D5F5F4; color: #20B8B5; }
    .rs-wf-3 { background-color: #EAE4FF; color: #8B5CF6; }
    .rs-wf-4 { background-color: #FFEBE0; color: #F97316; }
    .rs-wf-5 { background-color: #E2F7ED; color: #10B981; }

    .rs-wf-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #16233B;
    }
    .rs-wf-status {
        font-size: 0.75rem;
        color: #10B981;
        font-weight: 600;
    }
    .rs-wf-line {
        flex-grow: 1;
        height: 2px;
        background-color: #E2E8F0;
        margin: 0 16px;
    }

    /* General Card Design */
    .rs-card {
        background-color: #FFFFFF;
        border: 1px solid #D9E6F5;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 24px rgba(60, 110, 170, 0.06);
        margin-bottom: 20px;
    }
    .rs-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #16233B;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Drag & Drop Pastel Upload Zone */
    .rs-upload-zone {
        border: 2px dashed #7DB8FF;
        background-color: #EAF4FF;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        transition: all 0.2s;
    }
    .rs-upload-zone:hover {
        border-color: #2F80ED;
        background-color: #DCEEFF;
    }
    .rs-upload-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #16233B;
        margin-bottom: 4px;
    }
    .rs-upload-sub {
        font-size: 0.8rem;
        color: #60708A;
        margin-bottom: 12px;
    }

    /* CT Scan Viewer Canvas Container (Dark Charcoal Surface) */
    .rs-ct-viewer {
        background-color: #101827;
        border-radius: 20px;
        border: 1px solid #1F2937;
        padding: 18px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    }
    .rs-ct-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 1px solid #1F2937;
        margin-bottom: 14px;
    }
    .rs-ct-slice-info {
        color: #9CA3AF;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .rs-ct-status {
        color: #20B8B5;
        font-size: 0.82rem;
        font-weight: 700;
    }

    /* Top Plain-English Summary Card */
    .rs-summary-card {
        background-color: #FFFFFF;
        border: 1px solid #D9E6F5;
        border-left: 5px solid #2F80ED;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
        font-size: 1.05rem;
        font-weight: 600;
        color: #16233B;
        line-height: 1.5;
        box-shadow: 0 4px 14px rgba(60, 110, 170, 0.05);
    }
    .rs-blue-bold {
        color: #2F80ED;
        font-weight: 800;
    }

    /* Pastel Metric Cards */
    .rs-metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }
    .rs-metric-card {
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }
    .rs-metric-blue { background-color: #DCEEFF; border: 1px solid #B8D9FF; }
    .rs-metric-purple { background-color: #EAE4FF; border: 1px solid #D4C7FF; }
    .rs-metric-teal { background-color: #D5F5F4; border: 1px solid #A6ECE9; }
    .rs-metric-peach { background-color: #FFEBE0; border: 1px solid #FFD1BA; }
    .rs-metric-green { background-color: #E2F7ED; border: 1px solid #B7EED4; }

    .rs-metric-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #60708A;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .rs-metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #16233B;
    }

    /* Expandable Stone Result Cards */
    .rs-stone-item {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    .rs-stone-item:hover {
        border-color: #2F80ED;
        background-color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(47, 128, 237, 0.08);
    }
    .rs-stone-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .rs-stone-title {
        font-weight: 800;
        font-size: 0.95rem;
        color: #16233B;
    }
    .rs-stone-conf-badge {
        background-color: #D5F5F4;
        color: #0D9488;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 3px 10px;
        border-radius: 12px;
    }

    /* Anatomical Kidney Map Representation */
    .rs-kidney-map-box {
        background-color: #FFFFFF;
        border: 1px solid #D9E6F5;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        margin-bottom: 20px;
    }
    .rs-kidney-flex {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 10px;
    }
    .rs-kidney-organ {
        width: 90px;
        height: 120px;
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
    .rs-stone-dot {
        width: 14px;
        height: 14px;
        background-color: #2F80ED;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 8px #2F80ED;
        animation: pulseDot 1.5s infinite;
    }
    @keyframes pulseDot {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }

    /* Footer */
    .rs-footer-container {
        margin-top: 40px;
        padding: 24px;
        border-top: 1px solid #D9E6F5;
        text-align: center;
        color: #60708A;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-navbar">
    <div class="rs-logo-group">
        <div class="rs-logo-icon">🩺</div>
        <div>
            <div><span class="rs-logo-text-main">Renal</span><span class="rs-logo-text-accent">Scan</span></div>
            <div class="rs-logo-subtitle">AI Kidney Stone Analysis</div>
        </div>
    </div>
    <div class="rs-nav-links">
        <span class="rs-nav-link active">Dashboard</span>
        <span class="rs-nav-link">How It Works</span>
        <span class="rs-nav-link">Technology</span>
        <span class="rs-nav-link">About</span>
    </div>
    <div>
        <button class="rs-btn-upload">📤 Upload New CT Scan</button>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. RESEARCH & EDUCATIONAL PROTOTYPE DISCLAIMER BANNER
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="rs-disclaimer-banner">
    <div class="rs-disclaimer-left">
        <span>ⓘ</span>
        <span><span class="rs-disclaimer-tag">Research & Educational Prototype:</span> Measurements and classifications are literature-based estimates ({ASSUMED_MM_PER_PIXEL} mm/px FOV constant). This software is intended for technical evaluation and portfolio demonstration — not for clinical diagnosis or surgical decision-making.</span>
    </div>
    <div class="rs-disclaimer-link">Learn more →</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 5-STEP WORKFLOW BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-workflow-bar">
    <div class="rs-wf-step">
        <div class="rs-wf-badge rs-wf-1">01</div>
        <div>
            <div class="rs-wf-title">Preprocess</div>
            <div class="rs-wf-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-wf-line"></div>
    <div class="rs-wf-step">
        <div class="rs-wf-badge rs-wf-2">02</div>
        <div>
            <div class="rs-wf-title">Detect Stones</div>
            <div class="rs-wf-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-wf-line"></div>
    <div class="rs-wf-step">
        <div class="rs-wf-badge rs-wf-3">03</div>
        <div>
            <div class="rs-wf-title">Segment Stones</div>
            <div class="rs-wf-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-wf-line"></div>
    <div class="rs-wf-step">
        <div class="rs-wf-badge rs-wf-4">04</div>
        <div>
            <div class="rs-wf-title">Measure Stones</div>
            <div class="rs-wf-status">Complete ✓</div>
        </div>
    </div>
    <div class="rs-wf-line"></div>
    <div class="rs-wf-step">
        <div class="rs-wf-badge rs-wf-5">05</div>
        <div>
            <div class="rs-wf-title">Generate Report</div>
            <div class="rs-wf-status">Complete ✓</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Pipeline Loader
@st.cache_resource
def load_pipeline():
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=ASSUMED_MM_PER_PIXEL)

pipeline = load_pipeline()

# Session state management
if 'active_image' not in st.session_state:
    st.session_state['active_image'] = None
if 'active_sample_name' not in st.session_state:
    st.session_state['active_sample_name'] = None

sample_dir = PROJECT_ROOT / "data" / "test" / "images"
sample_files = sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []

# -----------------------------------------------------------------------------
# 4. MAIN WORKSPACE (3-COLUMN LAYOUT: 20% | 55% | 25%)
# -----------------------------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 2.7, 1.3])

# --- LEFT PANEL: CONTROLS & UPLOAD ZONE (20%) ---
with col_left:
    st.markdown('<div class="rs-card"><div class="rs-card-title">📤 Upload & Scan</div>', unsafe_allow_html=True)
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

    # Sample CT Scans Quick Selection
    st.markdown('<div class="rs-card"><div class="rs-card-title">🧪 Explore Sample Scans</div>', unsafe_allow_html=True)
    if len(sample_files) >= 3:
        if st.button("Analyze Sample 01 (Multiple)", key="btn_s1", use_container_width=True):
            bgr = cv2.imread(str(sample_files[0]))
            st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            st.session_state['active_sample_name'] = sample_files[0].name
            st.rerun()
        if st.button("Analyze Sample 02 (Single)", key="btn_s2", use_container_width=True):
            bgr = cv2.imread(str(sample_files[1]))
            st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            st.session_state['active_sample_name'] = sample_files[1].name
            st.rerun()
        if st.button("Analyze Sample 03 (Normal)", key="btn_s3", use_container_width=True):
            bgr = cv2.imread(str(sample_files[2]))
            st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            st.session_state['active_sample_name'] = sample_files[2].name
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Analysis Controls
    st.markdown('<div class="rs-card"><div class="rs-card-title">🎛️ Analysis Controls</div>', unsafe_allow_html=True)
    conf_thresh = st.slider(
        "Confidence Threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.40,
        step=0.05,
        help="Confidence cutoff for YOLOv8 stone detections."
    )
    
    st.markdown("**Visualization Overlay**")
    overlay_mode = st.radio(
        "Select CT Overlay View",
        options=["3. Measurement Axes", "2. Segmentation Masks", "1. YOLOv8 Detections", "Original CT Scan Only"],
        index=0
    )
    
    st.markdown("**Image Adjustments**")
    brightness = st.slider("Brightness", -50, 50, 0, step=5)
    contrast = st.slider("Contrast", -50, 50, 0, step=5)
    
    if st.button("Reset All Controls", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Default to first sample if active_image is None
if st.session_state['active_image'] is None and len(sample_files) > 0:
    bgr = cv2.imread(str(sample_files[0]))
    st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    st.session_state['active_sample_name'] = sample_files[0].name

# Apply brightness/contrast adjustments
processed_img = st.session_state['active_image'].copy() if st.session_state['active_image'] is not None else np.zeros((512,512,3), dtype=np.uint8)
if brightness != 0 or contrast != 0:
    processed_img = cv2.convertScaleAbs(processed_img, alpha=1.0 + (contrast/100.0), beta=brightness)

# Run Model Pipeline
with st.spinner("Analyzing CT scan — detecting, segmenting, and measuring stones..."):
    result = pipeline.analyze(processed_img, conf_thresh=conf_thresh)

summary = result['summary']
stones = result['stones']

# --- CENTER PANEL: CT SCAN VIEWER WORKSTATION (55%) ---
with col_center:
    st.markdown("""
    <div class="rs-ct-viewer">
        <div class="rs-ct-header">
            <span class="rs-ct-slice-info">CT ABDOMINAL SCAN | Slice 034 / 128</span>
            <span class="rs-ct-status">● AI ANALYSIS READY | RenalScan v2.0</span>
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

    # Before vs After Comparison View
    with st.expander("🔍 Before / After Segmentation Preview"):
        cc1, cc2 = st.columns(2)
        with cc1:
            st.caption("Original CT Scan")
            st.image(result['original_image'], use_container_width=True)
        with cc2:
            st.caption("AI Segmentation Mask Overlay")
            st.image(result['annotated_segmentation'], use_container_width=True)

# --- RIGHT PANEL: AI ANALYSIS RESULTS & METRICS (25%) ---
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
        <div class="rs-summary-card">
            💡 Scan shows <span class="rs-blue-bold">{stone_count} stone(s)</span>. Largest is <span class="rs-blue-bold">{largest_mm:.2f} mm</span>, which {guidance}.
        </div>
        """, unsafe_allow_html=True)

        # 3 Pastel Top Metric Cards
        st.markdown("""
        <div class="rs-metric-grid">
            <div class="rs-metric-card rs-metric-blue">
                <div class="rs-metric-label">Stones</div>
                <div class="rs-metric-value">{count}</div>
            </div>
            <div class="rs-metric-card rs-metric-purple">
                <div class="rs-metric-label">Largest</div>
                <div class="rs-metric-value">{mm} mm</div>
            </div>
            <div class="rs-metric-card rs-metric-teal">
                <div class="rs-metric-label">Conf</div>
                <div class="rs-metric-value">{conf}%</div>
            </div>
        </div>
        """.format(
            count=stone_count,
            mm=f"{largest_mm:.1f}",
            conf=f"{stones[0]['confidence']*100:.0f}" if len(stones)>0 else "0"
        ), unsafe_allow_html=True)

        # Expandable Stone Detail Cards
        st.markdown("#### Detected Stone Regions")
        for s in stones:
            if s.get('status') == 'Success':
                st.markdown(f"""
                <div class="rs-stone-item">
                    <div class="rs-stone-top">
                        <span class="rs-stone-title">Stone #{s['stone_id']}</span>
                        <span class="rs-stone-conf-badge">{s['confidence']*100:.1f}% Conf</span>
                    </div>
                    <div style="font-size: 0.84rem; color: #60708A;">
                        • <strong>Est. Diameter:</strong> {s['estimated_diameter_mm']:.2f} mm*<br>
                        • <strong>Major × Minor:</strong> {s['estimated_major_mm']:.1f} × {s['estimated_minor_mm']:.1f} mm<br>
                        • <strong>Treatment Category:</strong> {s['clinical_size_band']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Anatomical Kidney Location Map
    st.markdown("""
    <div class="rs-kidney-map-box">
        <div style="font-weight: 800; font-size: 0.9rem; color: #16233B;">🫘 Anatomical Kidney Map Representation</div>
        <div class="rs-kidney-flex">
            <div class="rs-kidney-organ">
                L
                <div class="rs-stone-dot" style="top: 30px; left: 35px;"></div>
            </div>
            <div class="rs-kidney-organ">
                R
                <div class="rs-stone-dot" style="top: 55px; left: 40px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Physical Measurements Cards (Stone #1 Baseline)
    if summary['has_stones'] and len(stones) > 0 and stones[0].get('status') == 'Success':
        s1 = stones[0]
        st.markdown("#### Physical Measurements (Stone #1)")
        pgrid1, pgrid2 = st.columns(2)
        with pgrid1:
            st.markdown(f"""
            <div class="rs-metric-card rs-metric-blue" style="margin-bottom: 8px;">
                <div class="rs-metric-label">Major Axis</div>
                <div class="rs-metric-value" style="font-size: 1.3rem;">{s1['estimated_major_mm']:.1f} mm</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="rs-metric-card rs-metric-peach">
                <div class="rs-metric-label">Mask Area</div>
                <div class="rs-metric-value" style="font-size: 1.3rem;">{s1['area_px']:.1f} px²</div>
            </div>
            """, unsafe_allow_html=True)
        with pgrid2:
            st.markdown(f"""
            <div class="rs-metric-card rs-metric-purple" style="margin-bottom: 8px;">
                <div class="rs-metric-label">Minor Axis</div>
                <div class="rs-metric-value" style="font-size: 1.3rem;">{s1['estimated_minor_mm']:.1f} mm</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="rs-metric-card rs-metric-green">
                <div class="rs-metric-label">Equiv Diam</div>
                <div class="rs-metric-value" style="font-size: 1.3rem;">{s1['estimated_diameter_mm']:.1f} mm</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Export & Reports")
    
    if summary['has_stones']:
        report_text = f"RenalScan AI Diagnostic Report\nScan: {st.session_state['active_sample_name']}\nStones: {summary['stone_count']}\nLargest: {summary['largest_stone_diameter_mm']} mm\n"
        for s in stones:
            report_text += f"- Stone #{s['stone_id']}: {s['estimated_diameter_mm']:.2f}mm ({s['clinical_size_band']})\n"
        report_text += f"\nDISCLAIMER: {NON_CLINICAL_DISCLAIMER}\n"
        
        st.download_button(
            "📄 Download Report (.txt)",
            data=report_text,
            file_name="RenalScan_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# 5. FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-footer-container">
    <strong>RenalScan</strong> — AI-Powered Kidney Stone Analysis Platform | Research & Educational Prototype<br>
    Built for Technical Portfolio Evaluation & Medical Computer Vision Demonstration
</div>
""", unsafe_allow_html=True)
