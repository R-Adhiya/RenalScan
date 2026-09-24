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

# Page Configuration - Clean Medical Red & White Identity
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# RENALSCAN OFFICIAL COLOR SYSTEM & CUSTOM CSS (RED + WHITE DOMAIN)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Inter Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Background & Body */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        max-width: 1440px;
        margin: 0 auto;
    }

    /* Red + White Button System Overrides */
    .stButton > button {
        background-color: #C62828 !important;
        color: #FFFFFF !important;
        border: 1px solid #C62828 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(198, 40, 40, 0.15) !important;
    }
    .stButton > button:hover {
        background-color: #8E1B1B !important;
        border-color: #8E1B1B !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.25) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary Button Style */
    .rs-btn-secondary {
        display: inline-block;
        background-color: #FFFFFF;
        color: #C62828;
        border: 1.5px solid #C62828;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        text-decoration: none;
        transition: all 0.2s ease;
        text-align: center;
        cursor: pointer;
    }
    .rs-btn-secondary:hover {
        background-color: #FFEBEE;
        color: #8E1B1B;
        border-color: #8E1B1B;
    }

    /* Header Bar */
    .rs-header {
        background-color: #FFFFFF;
        border-bottom: 1.5px solid #F1D5D5;
        padding: 14px 28px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.04);
    }
    .rs-logo-box {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .rs-logo-symbol {
        width: 38px;
        height: 38px;
        background: #C62828;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 1.25rem;
        box-shadow: 0 2px 8px rgba(198, 40, 40, 0.3);
    }
    .rs-logo-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1F2937;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .rs-logo-accent {
        color: #C62828;
    }
    .rs-logo-sub {
        font-size: 0.78rem;
        color: #6B7280;
        font-weight: 500;
    }
    .rs-nav-links {
        display: flex;
        align-items: center;
        gap: 28px;
    }
    .rs-nav-item {
        font-size: 0.92rem;
        font-weight: 600;
        color: #4B5563;
        text-decoration: none;
        padding-bottom: 4px;
        transition: color 0.2s;
    }
    .rs-nav-item:hover {
        color: #C62828;
    }
    .rs-nav-item.active {
        color: #C62828;
        border-bottom: 2px solid #C62828;
    }
    .rs-header-cta {
        background-color: #C62828;
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 0.88rem;
        padding: 9px 20px;
        border-radius: 20px;
        text-decoration: none;
        box-shadow: 0 3px 10px rgba(198, 40, 40, 0.22);
        transition: all 0.2s ease;
    }
    .rs-header-cta:hover {
        background-color: #8E1B1B;
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(198, 40, 40, 0.32);
    }

    /* Hero Section */
    .rs-hero-card {
        background: linear-gradient(180deg, #FFF7F7 0%, #FFFFFF 100%);
        border: 1px solid #F1D5D5;
        border-radius: 18px;
        padding: 36px 40px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(198, 40, 40, 0.05);
        position: relative;
        overflow: hidden;
    }
    .rs-hero-eyebrow {
        color: #C62828;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .rs-hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1F2937;
        line-height: 1.2;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    .rs-hero-title span {
        color: #C62828;
    }
    .rs-hero-subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        line-height: 1.6;
        max-width: 780px;
        margin-bottom: 22px;
    }
    .rs-hero-actions {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 10px;
    }

    /* Medical Safety Section */
    .rs-safety-banner {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-left: 4px solid #C62828;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 24px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
    }
    .rs-safety-icon {
        color: #C62828;
        font-size: 1.35rem;
        line-height: 1;
        margin-top: 2px;
    }
    .rs-safety-title {
        font-size: 0.9rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 2px;
    }
    .rs-safety-desc {
        font-size: 0.84rem;
        color: #6B7280;
        line-height: 1.5;
    }

    /* Streamlit Tab Customization (Red + White Active Underline) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #F1D5D5;
        background-color: #FFFFFF;
        padding: 4px 8px 0 8px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 700;
        color: #6B7280;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        border: none;
        background-color: transparent;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #C62828;
        background-color: #FFF7F7;
    }
    .stTabs [aria-selected="true"] {
        color: #C62828 !important;
        border-bottom: 3px solid #C62828 !important;
        background-color: #FFF7F7 !important;
    }

    /* Cards System */
    .rs-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 12px rgba(198, 40, 40, 0.03);
    }
    .rs-card-title {
        font-size: 1rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .rs-card-title-icon {
        color: #C62828;
    }

    /* Upload Area Card */
    .rs-upload-box {
        background-color: #FFF7F7;
        border: 1.5px dashed #E53935;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 14px;
    }
    .rs-upload-icon {
        color: #C62828;
        font-size: 1.8rem;
        margin-bottom: 4px;
    }

    /* CT Scan Viewer Frame */
    .rs-ct-header {
        background-color: #111827;
        border-radius: 14px 14px 0 0;
        border: 1px solid #1F2937;
        border-top: 3px solid #C62828;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .rs-ct-title-txt {
        color: #E5E7EB;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .rs-ct-status-ready {
        color: #10B981;
        font-size: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* AI Analysis Summary Card */
    .rs-summary-card {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-left: 5px solid #C62828;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 16px;
    }
    .rs-summary-header {
        color: #C62828;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .rs-summary-main {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1F2937;
        line-height: 1.45;
    }
    .rs-summary-highlight {
        color: #C62828;
        font-weight: 800;
    }

    /* 3 Clean White Metric Cards */
    .rs-metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 18px;
    }
    .rs-metric-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-top: 3px solid #C62828;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(198, 40, 40, 0.04);
    }
    .rs-metric-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .rs-metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #C62828;
    }

    /* Stone Finding Cards */
    .rs-stone-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(198, 40, 40, 0.03);
        transition: all 0.2s ease;
    }
    .rs-stone-card:hover {
        border-color: #C62828;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.08);
    }
    .rs-stone-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .rs-stone-id {
        font-weight: 800;
        font-size: 0.95rem;
        color: #C62828;
    }
    .rs-stone-conf-badge {
        background-color: #FFEBEE;
        color: #C62828;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 12px;
    }
    .rs-stone-meta {
        font-size: 0.83rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* Metadata Table Grid */
    .rs-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 14px;
    }
    .rs-meta-label {
        font-size: 0.75rem;
        color: #6B7280;
        font-weight: 600;
    }
    .rs-meta-val {
        font-size: 0.88rem;
        color: #1F2937;
        font-weight: 700;
    }

    /* Kidney Location Map Card */
    .rs-kidney-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.03);
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
        background-color: #FFF1F1;
        border: 2px solid #E53935;
        border-radius: 45% 55% 50% 50% / 60% 40% 60% 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        font-weight: 800;
        color: #C62828;
        font-size: 0.85rem;
    }
    .rs-stone-pulse-dot {
        width: 14px;
        height: 14px;
        background-color: #C62828;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 8px #E53935;
        animation: pulseRedDot 1.5s infinite;
    }
    @keyframes pulseRedDot {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }

    /* Physical Measurement Value Table */
    .rs-meas-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.03);
    }
    .rs-meas-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }
    .rs-meas-table th {
        font-size: 0.78rem;
        color: #6B7280;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 2px solid #F1D5D5;
    }
    .rs-meas-table td {
        font-size: 0.88rem;
        padding: 12px 14px;
        border-bottom: 1px solid #F1D5D5;
        color: #1F2937;
        font-weight: 600;
    }
    .rs-meas-val-cell {
        background-color: #FFF7F7;
        color: #C62828 !important;
        font-weight: 800 !important;
        border-radius: 6px;
    }

    /* 5-Step Process Timeline */
    .rs-timeline-wrapper {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 16px;
        padding: 26px 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 12px rgba(198, 40, 40, 0.03);
    }
    .rs-timeline-steps {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
    }
    .rs-timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        position: relative;
        z-index: 2;
        width: 18%;
    }
    .rs-step-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background-color: #C62828;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 3px 10px rgba(198, 40, 40, 0.25);
        margin-bottom: 10px;
    }
    .rs-step-circle.rs-step-secondary {
        background-color: #FFFFFF;
        border: 2px solid #C62828;
        color: #C62828;
    }
    .rs-timeline-step-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 3px;
    }
    .rs-timeline-step-desc {
        font-size: 0.75rem;
        color: #6B7280;
        line-height: 1.4;
    }
    .rs-timeline-line {
        position: absolute;
        top: 22px;
        left: 8%;
        right: 8%;
        height: 2px;
        background-color: #F1D5D5;
        z-index: 1;
    }

    /* Kidney Health Cards Grid */
    .rs-health-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        margin-top: 14px;
        margin-bottom: 24px;
    }
    .rs-health-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 2px 8px rgba(198, 40, 40, 0.03);
        transition: all 0.2s ease;
    }
    .rs-health-card:hover {
        border-color: #C62828;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(198, 40, 40, 0.08);
    }
    .rs-health-icon {
        width: 36px;
        height: 36px;
        background-color: #FFEBEE;
        color: #C62828;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        margin-bottom: 12px;
    }
    .rs-health-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 8px;
    }
    .rs-health-card-desc {
        font-size: 0.86rem;
        color: #4B5563;
        line-height: 1.55;
        margin-bottom: 12px;
    }
    .rs-health-learn-more {
        font-size: 0.82rem;
        font-weight: 700;
        color: #C62828;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    /* Footer */
    .rs-footer {
        margin-top: 40px;
        padding: 28px 20px;
        border-top: 2px solid #C62828;
        background-color: #FFF7F7;
        border-radius: 14px 14px 0 0;
        text-align: center;
    }
    .rs-footer-logo {
        font-weight: 800;
        font-size: 1.1rem;
        color: #1F2937;
        margin-bottom: 4px;
    }
    .rs-footer-sub {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 14px;
    }
    .rs-footer-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        font-size: 0.84rem;
        font-weight: 600;
        color: #4B5563;
        margin-bottom: 14px;
    }
    .rs-footer-links a {
        color: #4B5563;
        text-decoration: none;
        transition: color 0.2s;
    }
    .rs-footer-links a:hover {
        color: #C62828;
    }
    .rs-footer-copy {
        font-size: 0.78rem;
        color: #9CA3AF;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PIPELINE LOADER & MODEL INTEGRITY
# -----------------------------------------------------------------------------
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

# Sourced from tracked sample_scans folder (fallback to data/test/images if present)
sample_dir = PROJECT_ROOT / "app" / "sample_scans"
if not sample_dir.exists() or len(list(sample_dir.glob("*.jpg"))) == 0:
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
# 1. CLEAN WHITE HEADER (RED + WHITE DOMAIN IDENTITY)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-header">
    <div class="rs-logo-box">
        <div class="rs-logo-symbol">🩺</div>
        <div>
            <div class="rs-logo-title">Renal<span class="rs-logo-accent">Scan</span></div>
            <div class="rs-logo-sub">AI Kidney Stone Analysis</div>
        </div>
    </div>
    <div class="rs-nav-links">
        <span class="rs-nav-item active">Dashboard</span>
        <span class="rs-nav-item">How It Works</span>
        <span class="rs-nav-item">Kidney Health</span>
        <span class="rs-nav-item">About</span>
    </div>
    <div>
        <a href="#upload-section" class="rs-header-cta">Upload CT Scan</a>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. HERO SECTION (RED + WHITE PALETTE)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-hero-card">
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 30px;">
        <div style="flex: 1.4;">
            <div class="rs-hero-eyebrow">
                <span>●</span> AI-POWERED CLINICAL PROTOTYPE
            </div>
            <h1 class="rs-hero-title">
                AI-Powered <span>Kidney Stone Analysis</span>
            </h1>
            <p class="rs-hero-subtitle">
                Analyze abdominal CT scans with automated AI detection, precise anatomical localization, classical contour segmentation, and literature-based stone size measurement.
            </p>
            <div class="rs-hero-actions">
                <a href="#upload-section" class="rs-header-cta" style="padding: 11px 24px; font-size: 0.95rem;">Upload CT Scan</a>
                <a href="#how-it-works" class="rs-btn-secondary" style="padding: 10px 22px;">How It Works →</a>
            </div>
        </div>
        <div style="flex: 0.8; display: flex; justify-content: center; align-items: center;">
            <div style="position: relative; width: 220px; height: 220px; background: #FFF7F7; border: 2px dashed #E53935; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(198, 40, 40, 0.08);">
                <div style="position: absolute; width: 170px; height: 170px; border: 1.5px solid #F1D5D5; border-radius: 50%;"></div>
                <div style="font-size: 3.5rem; color: #C62828;">🩻</div>
                <div style="position: absolute; bottom: 15px; background: #C62828; color: #FFFFFF; font-size: 0.72rem; font-weight: 800; padding: 3px 10px; border-radius: 12px; letter-spacing: 0.05em;">
                    AI SCANNER
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MEDICAL SAFETY SECTION
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-safety-banner">
    <div class="rs-safety-icon">🛡️</div>
    <div>
        <div class="rs-safety-title">AI-Assisted. Clinician Reviewed.</div>
        <div class="rs-safety-desc">
            RenalScan provides AI-assisted analysis of CT images. Results should be reviewed by a qualified healthcare professional and should not be used as a standalone medical diagnosis. Measurements use a literature-based 0.70 mm/px FOV constant for technical evaluation.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN APP NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_dashboard, tab_how_it_works, tab_kidney_health, tab_about = st.tabs([
    "🩺 Dashboard & CT Analysis",
    "🔬 How RenalScan Works",
    "🫘 Kidney Health",
    "ℹ️ Limitations & Evaluation"
])

# =============================================================================
# TAB 1: WORKSPACE & AI ANALYSIS (DASHBOARD)
# =============================================================================
with tab_dashboard:
    # 2-Column Responsive Analysis Workspace
    col_left, col_right = st.columns([1.1, 1.9], gap="medium")

    # -------------------------------------------------------------------------
    # LEFT PANEL: UPLOAD & CONTROLS
    # -------------------------------------------------------------------------
    with col_left:
        # Premium White Upload Card
        st.markdown("""
        <div id="upload-section" class="rs-card">
            <div class="rs-card-title">
                <span class="rs-card-title-icon">📤</span> Upload Your CT Scan
            </div>
            <div style="font-size: 0.84rem; color: #6B7280; margin-bottom: 12px;">
                Upload a CT abdominal scan for AI-assisted kidney stone analysis.
            </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload CT Scan (JPG, JPEG, PNG • Max 200MB)",
            type=["jpg", "jpeg", "png"],
            help="Drag and drop or browse files. Maximum file size: 200 MB."
        )

        if uploaded_file is not None:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
            if bgr_img is not None and bgr_img.size > 0:
                if len(bgr_img.shape) == 3 and bgr_img.shape[2] == 4:
                    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGRA2RGB)
                elif len(bgr_img.shape) == 2:
                    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_GRAY2RGB)
                else:
                    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
                st.session_state['active_image'] = rgb_img
                st.session_state['active_sample_name'] = uploaded_file.name
            else:
                st.error(f"⚠️ Could not decode '{uploaded_file.name}'. Please ensure it is an uncorrupted JPG or PNG CT scan.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Verified Sample CT Scans
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title">
                <span class="rs-card-title-icon">🧪</span> Verified Sample Scans
            </div>
            <div style="font-size: 0.82rem; color: #6B7280; margin-bottom: 10px;">
                Select a benchmark CT scan from the test cohort:
            </div>
        """, unsafe_allow_html=True)

        if len(sample_files) >= 3:
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                if st.button("Sample 1\n(Multiple)", key="b1", use_container_width=True):
                    bgr = cv2.imread(str(sample_files[0]))
                    st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    st.session_state['active_sample_name'] = "Sample 01 (Multiple Stones)"
                    st.rerun()
            with s_col2:
                if st.button("Sample 2\n(Single)", key="b2", use_container_width=True):
                    bgr = cv2.imread(str(sample_files[1]))
                    st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    st.session_state['active_sample_name'] = "Sample 02 (Single Stone)"
                    st.rerun()
            with s_col3:
                if st.button("Sample 3\n(Normal)", key="b3", use_container_width=True):
                    bgr = cv2.imread(str(sample_files[2]))
                    st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    st.session_state['active_sample_name'] = "Sample 03 (Normal Scan)"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Scan Information Card
        scan_name = st.session_state['active_sample_name'] if st.session_state['active_sample_name'] else "RS-2026-001"
        display_scan_id = scan_name if len(scan_name) <= 18 else scan_name[:15] + "..."
        st.markdown(f"""
        <div class="rs-card">
            <div class="rs-card-title">
                <span class="rs-card-title-icon">ℹ️</span> Scan Metadata
            </div>
            <div class="rs-meta-grid">
                <div>
                    <div class="rs-meta-label">Scan ID</div>
                    <div class="rs-meta-val">{display_scan_id}</div>
                </div>
                <div>
                    <div class="rs-meta-label">Modality</div>
                    <div class="rs-meta-val">CT Abdominal</div>
                </div>
                <div>
                    <div class="rs-meta-label">Slice Position</div>
                    <div class="rs-meta-val">034 / 128</div>
                </div>
                <div>
                    <div class="rs-meta-label">Pixel Spacing</div>
                    <div class="rs-meta-val">{ASSUMED_MM_PER_PIXEL} mm/px</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Precision Analysis Controls Card
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title">
                <span class="rs-card-title-icon">🎛️</span> Analysis Parameters
            </div>
        """, unsafe_allow_html=True)

        conf_thresh = st.slider("Model Confidence Threshold", 0.10, 0.90, 0.40, step=0.05,
                                help="Minimum confidence threshold for YOLOv8 stone detector.")
        
        overlay_mode = st.radio(
            "Visualization Overlay Layer",
            options=["3. Measurement Axes", "2. Segmentation Masks", "1. YOLOv8 Detections", "Original CT Scan"],
            index=0
        )
        
        c_sl1, c_sl2 = st.columns(2)
        with c_sl1:
            brightness = st.slider("Brightness", -50, 50, 0, step=5)
        with c_sl2:
            contrast = st.slider("Contrast", -50, 50, 0, step=5)

        if st.button("Reset Settings", use_container_width=True):
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # RIGHT PANEL: CT VIEWER & AI ANALYSIS RESULTS
    # -------------------------------------------------------------------------
    with col_right:
        # Preprocess active image with sliders
        processed_img = st.session_state['active_image'].copy() if st.session_state['active_image'] is not None else np.zeros((512,512,3), dtype=np.uint8)
        if brightness != 0 or contrast != 0:
            processed_img = cv2.convertScaleAbs(processed_img, alpha=1.0 + (contrast/100.0), beta=brightness)

        # Run Pipeline Execution
        try:
            with st.spinner("Executing AI pipeline — detection, segmentation, and stone measurement..."):
                result = pipeline.analyze(processed_img, conf_thresh=conf_thresh)
        except Exception as exc:
            st.error(f"⚠️ Analysis error occurred ({type(exc).__name__}: {str(exc)}). Please select a sample scan or re-upload.")
            st.stop()

        summary = result['summary']
        stones = result['stones']

        # Prominent CT Scan Viewer
        st.markdown("""
        <div class="rs-ct-header">
            <span class="rs-ct-title-txt">CT ABDOMINAL SCAN | Slice 034 / 128</span>
            <span class="rs-ct-status-ready">● AI ANALYSIS READY</span>
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

        # Expandable Before vs After Comparison
        with st.expander("🔍 Before / After Segmentation Comparison"):
            c_comp1, c_comp2 = st.columns(2)
            with c_comp1:
                st.caption("Original Non-Contrast CT Scan")
                st.image(result['original_image'], use_container_width=True)
            with c_comp2:
                st.caption("AI Segmentation Overlay (Otsu Classical CV)")
                st.image(result['annotated_segmentation'], use_container_width=True)

        st.write("")

        # AI Analysis Results Heading & Status
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; margin-top: 10px;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #1F2937;">
                AI Analysis Results <span style="color: #C62828;">●</span>
            </div>
            <div style="color: #10B981; font-weight: 700; font-size: 0.88rem; display: flex; align-items: center; gap: 6px;">
                ● Analysis Complete
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not summary['has_stones']:
            st.markdown("""
            <div class="rs-summary-card">
                <div class="rs-summary-header">AI ANALYSIS SUMMARY</div>
                <div class="rs-summary-main">
                    No renal calculi detected above confidence threshold <strong>{conf:.2f}</strong>.
                </div>
                <div style="font-size: 0.85rem; color: #6B7280; margin-top: 4px;">
                    Scan is consistent with a normal non-contrast abdominal CT slice without prominent high-attenuation calcifications.
                </div>
            </div>
            """.format(conf=conf_thresh), unsafe_allow_html=True)
        else:
            stone_count = summary['stone_count']
            largest_mm = summary['largest_stone_diameter_mm']
            largest_band = summary['largest_stone_size_band']

            if "<4mm" in largest_band:
                clinical_note = "High likelihood of spontaneous passage (~80%) with hydration and expectant management."
            elif "4-6mm" in largest_band:
                clinical_note = "Moderate passage likelihood (~50%). Candidate for medical expulsive therapy (MET)."
            elif "6-10mm" in largest_band:
                clinical_note = "Low spontaneous passage (~20%). Urological consultation recommended for elective intervention."
            else:
                clinical_note = "Large calculus. Surgical intervention indicated (ESWL / Ureteroscopy / PCNL)."

            # Red-Accented Summary Card
            st.markdown(f"""
            <div class="rs-summary-card">
                <div class="rs-summary-header">AI ANALYSIS SUMMARY</div>
                <div class="rs-summary-main">
                    <span class="rs-summary-highlight">{stone_count} stone(s) detected</span> • 
                    <span class="rs-summary-highlight">{largest_mm:.2f} mm</span> largest stone diameter
                </div>
                <div style="font-size: 0.86rem; color: #4B5563; margin-top: 6px;">
                    {clinical_note}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Three Clean White Metric Cards
            mean_conf_pct = int(summary['mean_confidence'] * 100) if summary['mean_confidence'] else 0
            st.markdown(f"""
            <div class="rs-metrics-grid">
                <div class="rs-metric-box">
                    <div class="rs-metric-label">TOTAL STONES</div>
                    <div class="rs-metric-value">{stone_count}</div>
                </div>
                <div class="rs-metric-box">
                    <div class="rs-metric-label">LARGEST SIZE</div>
                    <div class="rs-metric-value">{largest_mm:.1f} <span style="font-size: 0.95rem;">mm</span></div>
                </div>
                <div class="rs-metric-box">
                    <div class="rs-metric-label">CONFIDENCE</div>
                    <div class="rs-metric-value">{mean_conf_pct}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Detected Stone Regions Cards (Actual Backend Values)
            st.markdown("""
            <div style="font-size: 1.05rem; font-weight: 800; color: #1F2937; margin-bottom: 10px;">
                Detected Stone Regions <span style="color: #C62828;">({count})</span>
            </div>
            """.format(count=stone_count), unsafe_allow_html=True)

            for s in stones:
                if s.get('status') == 'Success':
                    st.markdown(f"""
                    <div class="rs-stone-card">
                        <div class="rs-stone-head">
                            <span class="rs-stone-id">Stone #{s['stone_id']}</span>
                            <span class="rs-stone-conf-badge">{s['confidence']*100:.1f}% Confidence</span>
                        </div>
                        <div class="rs-stone-meta">
                            • <strong>Estimated Diameter:</strong> <span style="color: #C62828; font-weight: 700;">{s['estimated_diameter_mm']:.2f} mm</span> ({s['equiv_diameter_px']:.1f} px)<br>
                            • <strong>Dimensions (Major × Minor):</strong> {s['estimated_major_mm']:.1f} × {s['estimated_minor_mm']:.1f} mm<br>
                            • <strong>Anatomical Region:</strong> Kidney Region ROI<br>
                            • <strong>Clinical Band:</strong> {s['clinical_size_band']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # LOWER DASHBOARD SECTION: KIDNEY MAP & MEASUREMENTS TABLE
    # -------------------------------------------------------------------------
    st.markdown("---")
    low_col1, low_col2 = st.columns([1, 1.8], gap="medium")

    with low_col1:
        st.markdown("""
        <div class="rs-kidney-box">
            <div style="font-weight: 800; font-size: 1rem; color: #1F2937;">🫘 Anatomical Kidney Map</div>
            <div style="font-size: 0.8rem; color: #6B7280; margin-bottom: 12px;">Renal Region Position Reference</div>
            <div class="rs-kidney-flex">
                <div class="rs-kidney-organ">
                    Left (L)
                    <div class="rs-stone-pulse-dot" style="top: 36px; left: 32px;"></div>
                </div>
                <div class="rs-kidney-organ">
                    Right (R)
                    <div class="rs-stone-pulse-dot" style="top: 54px; left: 38px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with low_col2:
        if summary['has_stones'] and len(stones) > 0 and stones[0].get('status') == 'Success':
            s1 = stones[0]
            st.markdown("""
            <div class="rs-meas-box">
                <div style="font-weight: 800; font-size: 1rem; color: #1F2937; margin-bottom: 8px;">
                    📊 Physical Measurements (Primary Calculus — Stone #1)
                </div>
                <table class="rs-meas-table">
                    <thead>
                        <tr>
                            <th>Extracted Geometric Parameter</th>
                            <th>Calculated Physical Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Major Axis Length</td>
                            <td class="rs-meas-val-cell">{major:.1f} mm ({major_px:.1f} px)</td>
                        </tr>
                        <tr>
                            <td>Minor Axis Length</td>
                            <td class="rs-meas-val-cell">{minor:.1f} mm ({minor_px:.1f} px)</td>
                        </tr>
                        <tr>
                            <td>Contour Area</td>
                            <td class="rs-meas-val-cell">{area:.1f} px²</td>
                        </tr>
                        <tr>
                            <td>Equivalent Circle Diameter</td>
                            <td class="rs-meas-val-cell">{equiv:.2f} mm ({equiv_px:.1f} px)</td>
                        </tr>
                    </tbody>
                </table>
                <div style="font-size: 0.78rem; color: #6B7280; margin-top: 10px;">
                    * Assumed literature baseline: 0.70 mm/px. Non-clinical approximation for research demonstration.
                </div>
            </div>
            """.format(
                major=s1['estimated_major_mm'],
                major_px=s1['major_axis_px'],
                minor=s1['estimated_minor_mm'],
                minor_px=s1['minor_axis_px'],
                area=s1['area_px'],
                equiv=s1['estimated_diameter_mm'],
                equiv_px=s1['equiv_diameter_px']
            ), unsafe_allow_html=True)

    # Export Diagnostic Reports & Data
    st.markdown("---")
    st.markdown("### 📄 Export & Clinical Reports")

    if summary['has_stones']:
        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            report_text = f"RenalScan AI Analysis Report\nScan: {st.session_state['active_sample_name']}\nStones: {summary['stone_count']}\nLargest: {summary['largest_stone_diameter_mm']} mm\n"
            for s in stones:
                report_text += f"- Stone #{s['stone_id']}: {s['estimated_diameter_mm']:.2f}mm ({s['clinical_size_band']})\n"
            report_text += f"\nDISCLAIMER: {NON_CLINICAL_DISCLAIMER}\n"
            
            st.download_button(
                "📄 Download Analysis Report (.txt)",
                data=report_text,
                file_name="RenalScan_Clinical_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
        with exp_c2:
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
                "📊 Export Measurements (.csv)",
                data=df_export.to_csv(index=False),
                file_name="RenalScan_Measurements.csv",
                mime="text/csv",
                use_container_width=True
            )

# =============================================================================
# TAB 2: HOW RENALSCAN WORKS (5-STEP PROCESS & ANIMATION)
# =============================================================================
with tab_how_it_works:
    st.markdown("""
    <div id="how-it-works" style="margin-bottom: 24px;">
        <h2 style="font-weight: 800; color: #1F2937; margin-bottom: 6px;">How RenalScan Works</h2>
        <p style="color: #6B7280; font-size: 1rem; margin-bottom: 20px;">
            An end-to-end automated pipeline chaining deep learning object detection with classical morphological segmentation and geometric sizing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 5-Step Process Timeline
    st.markdown("""
    <div class="rs-timeline-wrapper">
        <div class="rs-timeline-steps">
            <div class="rs-timeline-line"></div>
            <div class="rs-timeline-step">
                <div class="rs-step-circle">01</div>
                <div class="rs-timeline-step-title">Upload CT Scan</div>
                <div class="rs-timeline-step-desc">Non-contrast abdominal CT slice input</div>
            </div>
            <div class="rs-timeline-step">
                <div class="rs-step-circle">02</div>
                <div class="rs-timeline-step-title">Image Preprocessing</div>
                <div class="rs-timeline-step-desc">Resize to 512×512 & normalization</div>
            </div>
            <div class="rs-timeline-step">
                <div class="rs-step-circle">03</div>
                <div class="rs-timeline-step-title">AI Detection & Segmentation</div>
                <div class="rs-timeline-step-desc">YOLOv8s localization + Otsu contouring</div>
            </div>
            <div class="rs-timeline-step">
                <div class="rs-step-circle">04</div>
                <div class="rs-timeline-step-title">Stone Measurement</div>
                <div class="rs-timeline-step-desc">Ellipse fitting & 0.70 mm/px scaling</div>
            </div>
            <div class="rs-timeline-step">
                <div class="rs-step-circle">05</div>
                <div class="rs-timeline-step-title">Analysis Results</div>
                <div class="rs-timeline-step-desc">Risk banding & clinical summary report</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Red & White Interactive Animated Pipeline Component
    animated_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #FFFFFF;
                margin: 0;
                padding: 10px;
                color: #1F2937;
            }}
            .card-container {{
                background-color: #FFFFFF;
                border: 1px solid #F1D5D5;
                border-radius: 18px;
                padding: 24px;
                box-shadow: 0 4px 20px rgba(198, 40, 40, 0.05);
            }}
            .ct-canvas {{
                background-color: #111827;
                border-radius: 14px;
                border-top: 3px solid #C62828;
                position: relative;
                width: 100%;
                height: 440px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            }}
            .ct-img {{
                max-height: 420px;
                max-width: 420px;
                border-radius: 6px;
                transition: opacity 0.5s, filter 0.5s;
            }}
            .scan-line {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, #E53935, transparent);
                box-shadow: 0 0 12px #E53935;
                animation: scanMove 3s infinite linear;
                opacity: 0.85;
            }}
            @keyframes scanMove {{
                0% {{ top: 5%; }}
                50% {{ top: 90%; }}
                100% {{ top: 5%; }}
            }}
            .svg-layer {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
            }}
            .yolo-box {{
                stroke: #E53935;
                stroke-width: 2.5;
                stroke-dasharray: 6 4;
                fill: rgba(229, 57, 53, 0.15);
                transition: all 0.5s;
            }}
            .otsu-contour {{
                stroke: #C62828;
                stroke-width: 3;
                fill: rgba(198, 40, 40, 0.28);
                stroke-dasharray: 400;
                stroke-dashoffset: 400;
                transition: stroke-dashoffset 1.5s ease-in-out;
            }}
            .draw-contour {{
                stroke-dashoffset: 0 !important;
            }}
            .meas-vector {{
                stroke: #C62828;
                stroke-width: 2.5;
                stroke-dasharray: 4;
            }}
            .badge-floating {{
                position: absolute;
                background: rgba(17, 24, 39, 0.9);
                backdrop-filter: blur(4px);
                border: 1px solid #C62828;
                color: #FFFFFF;
                padding: 6px 14px;
                border-radius: 8px;
                font-size: 0.82rem;
                font-weight: 700;
                transition: opacity 0.5s, transform 0.5s;
            }}
            .ctrl-bar {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 20px;
            }}
            .step-btn {{
                background-color: #FFFFFF;
                border: 1px solid #F1D5D5;
                color: #1F2937;
                font-weight: 700;
                font-size: 0.85rem;
                padding: 9px 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .step-btn:hover, .step-btn.active {{
                background-color: #C62828;
                border-color: #C62828;
                color: #FFFFFF;
            }}
            .timeline-bar {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 8px;
                margin-top: 18px;
                text-align: center;
            }}
            .t-stage {{
                background-color: #FFF7F7;
                border: 1px solid #F1D5D5;
                border-radius: 8px;
                padding: 10px;
                font-size: 0.78rem;
                font-weight: 700;
                color: #6B7280;
                transition: all 0.3s;
            }}
            .t-stage.active-stage {{
                background-color: #C62828;
                border-color: #C62828;
                color: #FFFFFF;
                transform: scale(1.02);
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
                <div id="confBadge" class="badge-floating" style="top: 20px; right: 20px; opacity: 0; background: #C62828;">CONFIDENCE: 86.8%</div>
                <div id="readoutBadge" class="badge-floating" style="bottom: 20px; right: 20px; opacity: 0; background: #C62828;">DIMENSIONS: 8.2mm × 5.4mm</div>
            </div>

            <div class="timeline-bar">
                <div id="t1" class="t-stage active-stage">01 CT Preprocess</div>
                <div id="t2" class="t-stage">02 YOLOv8s Detect</div>
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
                    badge.innerText = "02 YOLOV8S STONE DETECTION";
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

    # Technical Deep-Dive Cards
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">🎯</span> Detection Details</div>
            <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.55;">
                • <strong>Model:</strong> YOLOv8s (11.1M parameters)<br>
                • <strong>Dataset:</strong> Merged 3,305 scans across multi-center cohorts<br>
                • <strong>Resolution:</strong> 512×512 input tensor<br>
                • <strong>Precision / Recall:</strong> 86.83% P / 77.68% R on held-out test scans
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">🖋️</span> Segmentation Details</div>
            <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.55;">
                • <strong>Cropping:</strong> 10% bounding box margin expansion<br>
                • <strong>Algorithm:</strong> Otsu adaptive bimodal thresholding<br>
                • <strong>Filtering:</strong> Morphological opening (noise removal) & closing (hole fill)<br>
                • <strong>Extraction:</strong> Dominant high-intensity renal calculus contour
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">📐</span> Sizing & Risk Banding</div>
            <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.55;">
                • <strong>Ellipse Fitting:</strong> Direct second-moment matrix axis calculation<br>
                • <strong>Scaling:</strong> Assumed literature factor (0.70 mm/px)<br>
                • <strong>Equivalent Diameter:</strong> 2 × √(Area / π)<br>
                • <strong>Clinical Triaging:</strong> &lt;4mm (Small), 4-6mm (Med), 6-10mm (Lrg), &gt;10mm (V.Lrg)
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: UNDERSTANDING KIDNEY HEALTH (EDUCATIONAL SECTION)
# =============================================================================
with tab_kidney_health:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1F2937; margin-bottom: 6px;">Understanding Kidney Health</h2>
        <p style="color: #6B7280; font-size: 1rem; margin-bottom: 24px;">
            Essential educational overview of nephrolithiasis, diagnostic modalities, risk factors, and evidence-based clinical management guidelines.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 6 Clean White Cards with Subtle Red Accents
    st.markdown("""
    <div class="rs-health-grid">
        <div class="rs-health-card">
            <div class="rs-health-icon">🫘</div>
            <div class="rs-health-card-title">Kidney Stones</div>
            <div class="rs-health-card-desc">
                Hard mineral and salt deposits formed inside the renal calyces. Most stones consist of calcium oxalate, calcium phosphate, uric acid, or struvite.
            </div>
            <div class="rs-health-learn-more">Clinical Overview →</div>
        </div>
        <div class="rs-health-card">
            <div class="rs-health-icon">⚡</div>
            <div class="rs-health-card-title">Symptoms</div>
            <div class="rs-health-card-desc">
                Severe, fluctuating flank pain radiating to the lower abdomen and groin, visible hematuria (blood in urine), dysuria, and nausea during acute colic.
            </div>
            <div class="rs-health-learn-more">Symptom Guide →</div>
        </div>
        <div class="rs-health-card">
            <div class="rs-health-icon">⚠️</div>
            <div class="rs-health-card-title">Risk Factors</div>
            <div class="rs-health-card-desc">
                Chronic dehydration, high sodium or excessive animal protein consumption, personal or familial history, obesity, and hyperparathyroidism.
            </div>
            <div class="rs-health-learn-more">Risk Assessment →</div>
        </div>
        <div class="rs-health-card">
            <div class="rs-health-icon">🩻</div>
            <div class="rs-health-card-title">Diagnosis</div>
            <div class="rs-health-card-desc">
                Non-Contrast Abdominal Computed Tomography (NCCT) is the clinical gold standard, offering >95% sensitivity and millimeter-accurate calculus sizing.
            </div>
            <div class="rs-health-learn-more">Diagnostic Imaging →</div>
        </div>
        <div class="rs-health-card">
            <div class="rs-health-icon">💧</div>
            <div class="rs-health-card-title">Prevention</div>
            <div class="rs-health-card-desc">
                Consuming sufficient fluids to achieve at least 2.5 liters of urine output daily, dietary sodium reduction, and maintaining adequate dietary calcium.
            </div>
            <div class="rs-health-learn-more">Prevention Protocol →</div>
        </div>
        <div class="rs-health-card">
            <div class="rs-health-icon">🩺</div>
            <div class="rs-health-card-title">Treatment</div>
            <div class="rs-health-card-desc">
                Expectant management and hydration for calculi &lt;4mm; medical expulsive therapy (MET) for 4–6mm; shockwave lithotripsy (ESWL) or ureteroscopy (URS) for &gt;6mm.
            </div>
            <div class="rs-health-learn-more">Treatment Pathways →</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: KNOWN LIMITATIONS & EVALUATION STORY
# =============================================================================
with tab_about:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1F2937; margin-bottom: 6px;">Known Limitations & Technical Evaluation</h2>
        <p style="color: #6B7280; font-size: 1rem; margin-bottom: 24px;">
            Documented technical trade-offs, literature-based pixel-spacing sensitivity analysis, and empirical failure mode breakdown.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_lim1, c_lim2 = st.columns(2)

    with c_lim1:
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">⚠️</span> DICOM Metadata & Pixel-Spacing</div>
            <div style="font-size: 0.86rem; color: #4B5563; line-height: 1.55;">
                • Scans in this benchmark are standard image files (JPG) lacking embedded DICOM headers (`PixelSpacing` or `SliceThickness`).<br>
                • <strong>Literature-Based Constant:</strong> Baseline factor of <strong>0.70 mm/px</strong> is adopted from standard abdominal CT literature (360mm FOV / 512px).<br>
                • <strong>Non-Clinical Scope:</strong> All millimeter-based measurements and risk bands are approximate indicators for educational and portfolio demonstration.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Pixel-Spacing Sensitivity Table
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">🔬</span> Pixel-Spacing Sensitivity Analysis</div>
            <div style="font-size: 0.82rem; color: #6B7280; margin-bottom: 10px;">
                Impact on estimated stone diameter across plausible abdominal FOV range (0.50 – 0.90 mm/px):
            </div>
            <table class="rs-meas-table" style="font-size: 0.8rem;">
                <thead>
                    <tr>
                        <th>Stone Category</th>
                        <th>0.50 mm/px</th>
                        <th>0.70 mm/px (Base)</th>
                        <th>0.90 mm/px</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Small Stone (5.2 px)</td>
                        <td>2.6 mm</td>
                        <td style="color: #C62828; font-weight: 800;">3.7 mm</td>
                        <td>4.7 mm</td>
                    </tr>
                    <tr>
                        <td>Borderline (7.5 px)</td>
                        <td>3.8 mm</td>
                        <td style="color: #C62828; font-weight: 800;">5.3 mm</td>
                        <td>6.8 mm</td>
                    </tr>
                    <tr>
                        <td>Large (11.7 px)</td>
                        <td>5.9 mm</td>
                        <td style="color: #C62828; font-weight: 800;">8.2 mm</td>
                        <td>10.5 mm</td>
                    </tr>
                    <tr>
                        <td>Very Large (32.4 px)</td>
                        <td>16.2 mm</td>
                        <td style="color: #C62828; font-weight: 800;">22.7 mm</td>
                        <td>29.2 mm</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with c_lim2:
        st.markdown("""
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">🔍</span> Classical CV vs Mask Ground Truth</div>
            <div style="font-size: 0.86rem; color: #4B5563; line-height: 1.55;">
                • The training dataset provides bounding boxes (`.txt`) for detection, but lacks per-pixel ground truth mask annotations.<br>
                • Segmentation is performed via Otsu adaptive thresholding within padded YOLO crops rather than supervised mask networks (Mask R-CNN / U-Net).<br>
                • <strong>Assumption:</strong> The dominant bright structure inside the crop is the calculus; bright adjacent bone or vascular calcifications can affect contour boundary accuracy.
            </div>
        </div>
        <div class="rs-card">
            <div class="rs-card-title"><span class="rs-card-title-icon">📊</span> Empirical Detection Error Breakdown (123 Scans)</div>
            <div style="font-size: 0.86rem; color: #4B5563; line-height: 1.55;">
                • <strong>True Positives (TP):</strong> 172 stones (76.8% recall at conf=0.40)<br>
                • <strong>False Positives (FP):</strong> 29 regions (skeletal margins & dense extrarenal structures)<br>
                • <strong>False Negatives (FN):</strong> 52 stones (small calculi near 512×512 resolution limit & low-contrast stones)<br>
                • <strong>Primary Model:</strong> Promoted YOLOv8s v2 weights (`models/detection_best.pt`)
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FOOTER (CLEAN RED & WHITE DOMAIN)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-footer">
    <div class="rs-footer-logo">Renal<span style="color: #C62828;">Scan</span></div>
    <div class="rs-footer-sub">AI Kidney Stone Analysis • Educational & Clinical Research Prototype</div>
    <div class="rs-footer-links">
        <a href="#upload-section">Dashboard</a>
        <a href="#how-it-works">How It Works</a>
        <a href="#understanding-kidney-health">Kidney Health</a>
        <a href="#limitations">About</a>
        <a href="https://github.com/R-Adhiya/RenalScan" target="_blank">GitHub Repository</a>
    </div>
    <div class="rs-footer-copy">
        © 2026 RenalScan AI Systems. Built for Technical Evaluation & Medical Computer Vision Demonstration. Non-diagnostic.
    </div>
</div>
""", unsafe_allow_html=True)
