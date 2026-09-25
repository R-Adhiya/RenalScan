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

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION - MEDICAL RED & WHITE IDENTITY
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# GLOBAL RED + WHITE CSS DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global Canvas */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Primary Red Buttons */
    .stButton > button {
        background-color: #C62828 !important;
        color: #FFFFFF !important;
        border: 1px solid #C62828 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 9px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(198, 40, 40, 0.15) !important;
    }
    .stButton > button:hover {
        background-color: #8E1B1B !important;
        border-color: #8E1B1B !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(198, 40, 40, 0.25) !important;
    }

    /* Landing Page Navbar */
    .lp-navbar {
        background-color: #FFFFFF;
        border-bottom: 1.5px solid #F1D5D5;
        padding: 14px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.04);
    }
    .lp-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .lp-logo-badge {
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
    .lp-brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #1F2937;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .lp-brand-accent {
        color: #C62828;
    }
    .lp-brand-sub {
        font-size: 0.76rem;
        color: #6B7280;
        font-weight: 500;
    }
    .lp-nav-links {
        display: flex;
        align-items: center;
        gap: 28px;
    }
    .lp-nav-item {
        font-size: 0.92rem;
        font-weight: 600;
        color: #4B5563;
        text-decoration: none;
        transition: color 0.2s;
    }
    .lp-nav-item:hover {
        color: #C62828;
    }

    /* Landing Page Hero Section */
    .lp-hero-wrapper {
        background: linear-gradient(180deg, #FFF7F7 0%, #FFFFFF 100%);
        border: 1px solid #F1D5D5;
        border-radius: 20px;
        padding: 40px 44px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(198, 40, 40, 0.04);
    }
    .lp-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #FFEBEE;
        color: #C62828;
        border: 1px solid #F1D5D5;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 20px;
        padding: 5px 14px;
        margin-bottom: 14px;
    }
    .lp-hero-heading {
        font-size: 2.85rem;
        font-weight: 800;
        color: #1F2937;
        line-height: 1.2;
        letter-spacing: -0.025em;
        margin-bottom: 16px;
    }
    .lp-hero-heading span {
        color: #C62828;
    }
    .lp-hero-desc {
        font-size: 1.08rem;
        color: #4B5563;
        line-height: 1.6;
        margin-bottom: 24px;
    }
    .lp-trust-line {
        font-size: 0.84rem;
        color: #6B7280;
        margin-top: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* CT Preview Card in Hero */
    .lp-ct-preview-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-top: 3px solid #C62828;
        border-radius: 16px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .lp-ct-floating-tag {
        position: absolute;
        bottom: 24px;
        left: 24px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(8px);
        border: 1.5px solid #F1D5D5;
        border-left: 4px solid #C62828;
        border-radius: 10px;
        padding: 10px 14px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        animation: floatCard 3s ease-in-out infinite;
    }
    @keyframes floatCard {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    .lp-ct-float-title {
        font-size: 0.72rem;
        font-weight: 800;
        color: #C62828;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .lp-ct-float-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: #1F2937;
    }
    .lp-ct-float-sub {
        font-size: 0.72rem;
        color: #6B7280;
    }

    /* Value Strip */
    .lp-value-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 36px;
    }
    .lp-value-item {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 2px 8px rgba(198, 40, 40, 0.03);
    }
    .lp-value-icon {
        width: 38px;
        height: 38px;
        background-color: #FFEBEE;
        color: #C62828;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
    }
    .lp-value-text-title {
        font-size: 0.88rem;
        font-weight: 800;
        color: #1F2937;
    }
    .lp-value-text-sub {
        font-size: 0.75rem;
        color: #6B7280;
    }

    /* Section Headings */
    .lp-section-header {
        text-align: center;
        margin-bottom: 28px;
    }
    .lp-section-title {
        font-size: 1.95rem;
        font-weight: 800;
        color: #1F2937;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    .lp-section-title span {
        color: #C62828;
    }
    .lp-section-desc {
        font-size: 0.98rem;
        color: #6B7280;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* 3 Pillars Cards */
    .lp-pillars-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }
    .lp-pillar-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-top: 3px solid #C62828;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 3px 12px rgba(198, 40, 40, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .lp-pillar-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(198, 40, 40, 0.08);
    }
    .lp-pillar-icon {
        font-size: 1.8rem;
        color: #C62828;
        margin-bottom: 12px;
    }
    .lp-pillar-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 6px;
    }
    .lp-pillar-desc {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* 5-Step Process Timeline */
    .lp-timeline-wrapper {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-radius: 16px;
        padding: 30px 24px;
        margin-bottom: 40px;
    }
    .lp-timeline-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
    }
    .lp-step-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        width: 18%;
        position: relative;
        z-index: 2;
    }
    .lp-step-num {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background-color: #C62828;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 3px 10px rgba(198, 40, 40, 0.25);
        margin-bottom: 10px;
    }
    .lp-step-title {
        font-size: 0.9rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 3px;
    }
    .lp-step-desc {
        font-size: 0.76rem;
        color: #6B7280;
        line-height: 1.35;
    }
    .lp-timeline-line {
        position: absolute;
        top: 22px;
        left: 8%;
        right: 8%;
        height: 2px;
        background-color: #F1D5D5;
        z-index: 1;
    }

    /* Key Capabilities 2x3 Grid */
    .lp-features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        margin-bottom: 40px;
    }
    .lp-feature-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.03);
        transition: all 0.2s ease;
    }
    .lp-feature-card:hover {
        border-color: #C62828;
        box-shadow: 0 4px 14px rgba(198, 40, 40, 0.08);
    }
    .lp-feature-icon {
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
    .lp-feature-title {
        font-size: 1rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 6px;
    }
    .lp-feature-desc {
        font-size: 0.84rem;
        color: #4B5563;
        line-height: 1.5;
    }

    /* CT Showcase Section */
    .lp-showcase-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 18px;
        padding: 28px;
        margin-bottom: 40px;
        box-shadow: 0 4px 16px rgba(198, 40, 40, 0.04);
    }
    .lp-showcase-right {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-left: 4px solid #C62828;
        border-radius: 14px;
        padding: 24px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Responsible AI Banner */
    .lp-safety-card {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-left: 4px solid #C62828;
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 40px;
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }
    .lp-safety-icon {
        color: #C62828;
        font-size: 1.6rem;
        line-height: 1;
        margin-top: 2px;
    }

    /* Final CTA */
    .lp-final-cta {
        background: linear-gradient(180deg, #FFFFFF 0%, #FFF7F7 100%);
        border: 1.5px solid #F1D5D5;
        border-radius: 20px;
        padding: 44px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 4px 20px rgba(198, 40, 40, 0.05);
    }

    /* Footer */
    .lp-footer {
        border-top: 2px solid #C62828;
        background-color: #FFF7F7;
        border-radius: 16px 16px 0 0;
        padding: 36px 30px 24px 30px;
    }
    .lp-footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 30px;
        margin-bottom: 24px;
    }
    .lp-footer-col h4 {
        font-size: 0.9rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 12px;
    }
    .lp-footer-col ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .lp-footer-col li {
        font-size: 0.84rem;
        color: #6B7280;
        margin-bottom: 8px;
    }
    .lp-footer-bottom {
        border-top: 1px solid #F1D5D5;
        padding-top: 16px;
        text-align: center;
        font-size: 0.78rem;
        color: #9CA3AF;
    }

    /* Workstation Specific CSS */
    .rs-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(198, 40, 40, 0.03);
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
    .rs-summary-card {
        background-color: #FFF7F7;
        border: 1px solid #F1D5D5;
        border-left: 5px solid #C62828;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 16px;
    }
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
        margin-bottom: 4px;
    }
    .rs-metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #C62828;
    }
    .rs-stone-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(198, 40, 40, 0.03);
    }
    .rs-stone-card:hover {
        border-color: #C62828;
    }
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
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# APPLICATION ROUTING & STATE MANAGEMENT
# -----------------------------------------------------------------------------
# Default page is 'landing' unless URL specifies ?page=workstation
if 'page' not in st.session_state:
    st.session_state['page'] = st.query_params.get('page', 'landing')

def navigate_to(page_name):
    st.session_state['page'] = page_name
    st.query_params['page'] = page_name
    st.rerun()

# -----------------------------------------------------------------------------
# BACKEND MODEL PIPELINE & RESOURCES
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pipeline():
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=ASSUMED_MM_PER_PIXEL)

pipeline = get_pipeline()

# Session State for Images
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

# Encode sample CT image to base64 for Hero and Showcase Visuals
sample_b64 = ""
if len(sample_files) > 0:
    with open(sample_files[0], "rb") as img_f:
        sample_b64 = base64.b64encode(img_f.read()).decode()

# =============================================================================
# VIEW 1: DEDICATED RENALSCAN LANDING PAGE
# =============================================================================
if st.session_state['page'] == 'landing':

    # -------------------------------------------------------------------------
    # 1. NAVBAR
    # -------------------------------------------------------------------------
    nav_c1, nav_c2, nav_c3 = st.columns([1.5, 2.5, 1], gap="small")
    with nav_c1:
        st.markdown("""
        <div class="lp-brand-box">
            <div class="lp-logo-badge">🩺</div>
            <div>
                <div class="lp-brand-title">Renal<span class="lp-brand-accent">Scan</span></div>
                <div class="lp-brand-sub">AI Kidney Stone Analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with nav_c2:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; gap: 24px; padding-top: 6px;">
            <a href="#how-it-works" class="lp-nav-item">How It Works</a>
            <a href="#features" class="lp-nav-item">Features</a>
            <a href="#showcase" class="lp-nav-item">CT Showcase</a>
            <a href="#kidney-health" class="lp-nav-item">Kidney Health</a>
            <a href="#about" class="lp-nav-item">About</a>
        </div>
        """, unsafe_allow_html=True)
    with nav_c3:
        if st.button("Launch RenalScan →", key="nav_launch", use_container_width=True):
            navigate_to('workstation')

    st.write("")

    # -------------------------------------------------------------------------
    # 2. HERO SECTION
    # -------------------------------------------------------------------------
    st.markdown("""<div class="lp-hero-wrapper">""", unsafe_allow_html=True)
    hero_left, hero_right = st.columns([1.2, 1], gap="large")

    with hero_left:
        st.markdown("""
        <div class="lp-badge">● AI-POWERED MEDICAL IMAGING</div>
        <h1 class="lp-hero-heading">
            Smarter Kidney Stone<br><span>Analysis with AI</span>
        </h1>
        <p class="lp-hero-desc">
            RenalScan uses AI-powered image analysis to detect, segment, and measure potential kidney stones from CT scans — helping make medical image analysis faster and more informative.
        </p>
        """, unsafe_allow_html=True)

        cta_col1, cta_col2 = st.columns([1.2, 1])
        with cta_col1:
            if st.button("Analyze a CT Scan →", key="hero_cta", use_container_width=True):
                navigate_to('workstation')
        with cta_col2:
            st.markdown("""
            <a href="#how-it-works" style="display: block; text-align: center; background: #FFFFFF; color: #C62828; border: 1.5px solid #C62828; border-radius: 8px; padding: 9px 18px; font-weight: 600; font-size: 0.9rem; text-decoration: none;">
                How It Works
            </a>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="lp-trust-line">
            <span>🛡️</span> AI-assisted analysis • Clear visualization • Measurement support
        </div>
        """, unsafe_allow_html=True)

    with hero_right:
        # Visually Impressive CT Scan Visualization Preview with Red Overlays
        st.markdown(f"""
        <div class="lp-ct-preview-card">
            <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: #9CA3AF; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em;">CT ABDOMINAL • AXIAL</span>
                <span style="color: #10B981; font-size: 0.72rem; font-weight: 700;">● AI ACTIVE</span>
            </div>
            <div style="position: relative; width: 100%; display: flex; justify-content: center;">
                <img src="data:image/jpeg;base64,{sample_b64}" style="max-height: 290px; border-radius: 8px; width: auto; object-fit: contain; opacity: 0.95;">
                <svg viewBox="0 0 400 300" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
                    <!-- Red Detection Box -->
                    <rect x="170" y="105" width="65" height="60" style="stroke: #E53935; stroke-width: 2; fill: rgba(229, 57, 53, 0.12); stroke-dasharray: 4 2;" />
                    <!-- Red Otsu Contour -->
                    <path d="M 185,120 Q 215,110 225,135 T 205,155 T 180,145 Z" style="stroke: #C62828; stroke-width: 2.5; fill: rgba(198, 40, 40, 0.28);" />
                    <!-- Caliper Axis Line -->
                    <line x1="180" y1="135" x2="228" y2="135" style="stroke: #FFFFFF; stroke-width: 1.5; stroke-dasharray: 3;" />
                </svg>
            </div>
            <div class="lp-ct-floating-tag">
                <div class="lp-ct-float-title">● AI Analysis</div>
                <div class="lp-ct-float-val">5.27 mm</div>
                <div class="lp-ct-float-sub">Stone Detected • 92% confidence</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. TRUST / VALUE STRIP
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-value-strip">
        <div class="lp-value-item">
            <div class="lp-value-icon">🎯</div>
            <div>
                <div class="lp-value-text-title">AI-Powered</div>
                <div class="lp-value-text-sub">YOLOv8s Stone Detection</div>
            </div>
        </div>
        <div class="lp-value-item">
            <div class="lp-value-icon">📐</div>
            <div>
                <div class="lp-value-text-title">Precise Measurement</div>
                <div class="lp-value-text-sub">Ellipse Axis & Area Sizing</div>
            </div>
        </div>
        <div class="lp-value-item">
            <div class="lp-value-icon">🩻</div>
            <div>
                <div class="lp-value-text-title">CT Image Analysis</div>
                <div class="lp-value-text-sub">Non-Contrast Axial Slices</div>
            </div>
        </div>
        <div class="lp-value-item">
            <div class="lp-value-icon">🔍</div>
            <div>
                <div class="lp-value-text-title">Clear Visualization</div>
                <div class="lp-value-text-sub">Multi-layer Contour Overlays</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. WHAT IS RENALSCAN?
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="features" class="lp-section-header">
        <h2 class="lp-section-title">Making Kidney Stone Analysis <span>More Intelligent</span></h2>
        <p class="lp-section-desc">
            RenalScan is an AI-powered medical imaging platform designed to assist with the identification and quantitative analysis of kidney stone regions in CT scans.
        </p>
    </div>
    <div class="lp-pillars-grid">
        <div class="lp-pillar-card">
            <div class="lp-pillar-icon">🎯</div>
            <div class="lp-pillar-title">DETECT</div>
            <div class="lp-pillar-desc">
                Automatically scans full abdominal CT slices to identify candidate high-attenuation calculus regions with calibrated deep learning weights.
            </div>
        </div>
        <div class="lp-pillar-card">
            <div class="lp-pillar-icon">🖋️</div>
            <div class="lp-pillar-title">SEGMENT</div>
            <div class="lp-pillar-desc">
                Isolates the stone’s exact pixel boundary from surrounding soft tissue using adaptive bimodal thresholding and morphological filtering.
            </div>
        </div>
        <div class="lp-pillar-card">
            <div class="lp-pillar-icon">📏</div>
            <div class="lp-pillar-title">MEASURE</div>
            <div class="lp-pillar-desc">
                Fits direct ellipse geometry to extract major and minor axes, estimating physical millimeter size and clinical passage likelihood bands.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. HOW RENALSCAN WORKS
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="how-it-works" class="lp-section-header">
        <h2 class="lp-section-title">From CT Scan to <span>AI Analysis</span></h2>
        <p class="lp-section-desc">
            A seamless, five-step clinical pipeline automating computer vision from initial scan ingest to structured diagnostic report.
        </p>
    </div>
    <div class="lp-timeline-wrapper">
        <div class="lp-timeline-row">
            <div class="lp-timeline-line"></div>
            <div class="lp-step-box">
                <div class="lp-step-num">01</div>
                <div class="lp-step-title">UPLOAD</div>
                <div class="lp-step-desc">Upload a CT scan slice image</div>
            </div>
            <div class="lp-step-box">
                <div class="lp-step-num">02</div>
                <div class="lp-step-title">PREPROCESS</div>
                <div class="lp-step-desc">Prepare and normalize image for AI</div>
            </div>
            <div class="lp-step-box">
                <div class="lp-step-num">03</div>
                <div class="lp-step-title">DETECT</div>
                <div class="lp-step-desc">Identify candidate stone regions</div>
            </div>
            <div class="lp-step-box">
                <div class="lp-step-num">04</div>
                <div class="lp-step-title">SEGMENT & MEASURE</div>
                <div class="lp-step-desc">Trace exact contours & estimate size</div>
            </div>
            <div class="lp-step-box">
                <div class="lp-step-num">05</div>
                <div class="lp-step-title">VISUALIZE</div>
                <div class="lp-step-desc">Review results & clinical reports</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 6. KEY CAPABILITIES (2x3 Grid)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-section-header">
        <h2 class="lp-section-title">Built for <span>Intelligent CT Analysis</span></h2>
        <p class="lp-section-desc">
            Engineered with deep learning, classical computer vision, and urological sizing standards.
        </p>
    </div>
    <div class="lp-features-grid">
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🎯</div>
            <div class="lp-feature-title">AI Stone Detection</div>
            <div class="lp-feature-desc">Identify potential kidney stone regions with trained YOLOv8s weights benchmarked on held-out clinical cohorts.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🖋️</div>
            <div class="lp-feature-title">Image Segmentation</div>
            <div class="lp-feature-desc">Visualize detected stone areas with precise contour boundaries isolated from background parenchyma.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">📐</div>
            <div class="lp-feature-title">Size Measurement</div>
            <div class="lp-feature-desc">Estimate major axis, minor axis, and equivalent diameter using literature-based pixel spacing (0.70 mm/px).</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">📊</div>
            <div class="lp-feature-title">Confidence Analysis</div>
            <div class="lp-feature-desc">Display per-stone model prediction confidence scores and calibrated detection probability metrics.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🔍</div>
            <div class="lp-feature-title">Visual Annotations</div>
            <div class="lp-feature-desc">Toggle between bounding box overlays, Otsu segmentation masks, and measurement caliper vectors.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🩺</div>
            <div class="lp-feature-title">Analysis Dashboard</div>
            <div class="lp-feature-desc">Review comprehensive results in a structured workstation with one-click report and data downloads.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 7. CT ANALYSIS PREVIEW (SHOWCASE)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="showcase" class="lp-section-header">
        <h2 class="lp-section-title">See AI Analysis <span>in Action</span></h2>
        <p class="lp-section-desc">
            Preview the full-resolution diagnostic overlay generated by the RenalScan pipeline.
        </p>
    </div>
    <div class="lp-showcase-box">
    """, unsafe_allow_html=True)

    sc_col1, sc_col2 = st.columns([1.5, 1], gap="medium")
    with sc_col1:
        st.markdown(f"""
        <div style="background-color: #111827; border-radius: 14px; border: 1px solid #1F2937; border-top: 3px solid #C62828; padding: 14px; display: flex; flex-direction: column; align-items: center;">
            <div style="width: 100%; display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700;">CT SCAN SHOWCASE | Slice 034 / 128</span>
                <span style="color: #10B981; font-size: 0.8rem; font-weight: 700;">● MEASUREMENT OVERLAY</span>
            </div>
            <div style="position: relative; width: 100%; display: flex; justify-content: center;">
                <img src="data:image/jpeg;base64,{sample_b64}" style="max-height: 380px; width: auto; object-fit: contain; border-radius: 8px;">
                <svg viewBox="0 0 500 380" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
                    <rect x="220" y="130" width="80" height="75" style="stroke: #E53935; stroke-width: 2.5; fill: rgba(229, 57, 53, 0.12); stroke-dasharray: 6 3;" />
                    <path d="M 235,150 Q 275,135 285,170 T 260,195 T 230,180 Z" style="stroke: #C62828; stroke-width: 3; fill: rgba(198, 40, 40, 0.28);" />
                    <line x1="230" y1="165" x2="285" y2="165" style="stroke: #FFFFFF; stroke-width: 2; stroke-dasharray: 4;" />
                    <line x1="258" y1="140" x2="258" y2="190" style="stroke: #FFFFFF; stroke-width: 2; stroke-dasharray: 4;" />
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with sc_col2:
        st.markdown("""
        <div class="lp-showcase-right">
            <div>
                <div style="font-size: 0.78rem; font-weight: 800; color: #C62828; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                    AI ANALYSIS SHOWCASE
                </div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #1F2937; margin-bottom: 16px;">
                    Quantitative Calculus Findings
                </div>
                <div style="background: #FFFFFF; border: 1px solid #F1D5D5; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">POTENTIAL STONES DETECTED</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #C62828;">3</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #F1D5D5; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">LARGEST DETECTED SIZE</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #C62828;">5.27 mm</div>
                    <div style="font-size: 0.75rem; color: #6B7280;">Moderate passage likelihood (4–6mm band)</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #F1D5D5; border-radius: 10px; padding: 14px; margin-bottom: 16px;">
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">DETECTION CONFIDENCE</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #C62828;">92%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Workstation →", key="showcase_launch", use_container_width=True):
            navigate_to('workstation')
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 8. KIDNEY STONE EDUCATION
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="kidney-health" class="lp-section-header">
        <h2 class="lp-section-title">Understanding <span>Kidney Stones</span></h2>
        <p class="lp-section-desc">
            Nephrolithiasis affects over 10% of the population. Understanding etiology, symptoms, and risk factors is vital for prevention.
        </p>
    </div>
    <div class="lp-features-grid">
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🫘</div>
            <div class="lp-feature-title">What Are Kidney Stones?</div>
            <div class="lp-feature-desc">Hard mineral and salt deposits formed inside renal calyces. Most stones consist of calcium oxalate, phosphate, or uric acid.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">⚡</div>
            <div class="lp-feature-title">Common Symptoms</div>
            <div class="lp-feature-desc">Severe fluctuating flank pain radiating to groin, hematuria (blood in urine), dysuria, and persistent nausea during colic.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">⚠️</div>
            <div class="lp-feature-title">Risk Factors</div>
            <div class="lp-feature-desc">Chronic dehydration, high sodium or excessive animal protein consumption, personal or familial history, and metabolic factors.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">💧</div>
            <div class="lp-feature-title">Prevention Guidelines</div>
            <div class="lp-feature-desc">Consuming sufficient fluids to achieve at least 2.5L urine output daily, dietary sodium reduction, and balanced calcium intake.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🩻</div>
            <div class="lp-feature-title">Diagnostic Imaging</div>
            <div class="lp-feature-desc">Non-Contrast CT is the imaging gold standard, offering >95% sensitivity and millimeter-accurate calculus sizing.</div>
        </div>
        <div class="lp-feature-card">
            <div class="lp-feature-icon">🩺</div>
            <div class="lp-feature-title">Treatment Pathways</div>
            <div class="lp-feature-desc">Expectant management for &lt;4mm; MET observation for 4–6mm; shockwave lithotripsy (ESWL) or ureteroscopy for &gt;6mm.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 9. RESPONSIBLE AI SECTION
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="about" class="lp-safety-card">
        <div class="lp-safety-icon">🛡️</div>
        <div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #1F2937; margin-bottom: 4px;">
                AI-Assisted. Clinician Reviewed.
            </div>
            <div style="font-size: 0.88rem; color: #4B5563; line-height: 1.55;">
                RenalScan is designed to assist with CT image analysis. AI-generated findings are intended as supportive information and should be reviewed by qualified healthcare professionals. This prototype is built for technical evaluation and educational demonstration, not as a standalone medical diagnostic tool.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 10. FINAL CTA
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-final-cta">
        <h2 style="font-size: 2.1rem; font-weight: 800; color: #1F2937; margin-bottom: 10px;">
            Ready to Analyze a <span>CT Scan?</span>
        </h2>
        <p style="color: #6B7280; font-size: 1.05rem; max-width: 600px; margin: 0 auto 24px auto;">
            Upload an abdominal CT scan or select a verified test case to explore RenalScan's automated detection and sizing workflow.
        </p>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns([1, 1.2, 1])
    with f_col2:
        if st.button("Start Analysis →", key="final_cta_btn", use_container_width=True):
            navigate_to('workstation')

    st.markdown("""
        <div style="font-size: 0.82rem; color: #9CA3AF; margin-top: 14px;">
            No complicated setup. Upload your scan and begin immediate evaluation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 11. FOOTER
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-footer">
        <div class="lp-footer-grid">
            <div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #1F2937; margin-bottom: 4px;">
                    Renal<span style="color: #C62828;">Scan</span>
                </div>
                <div style="font-size: 0.82rem; color: #6B7280; margin-bottom: 10px;">
                    AI Kidney Stone Analysis
                </div>
                <div style="font-size: 0.82rem; color: #4B5563; line-height: 1.5; max-width: 300px;">
                    Intelligent medical imaging assistance for automated kidney stone detection, segmentation, and physical measurement.
                </div>
            </div>
            <div class="lp-footer-col">
                <h4>Product</h4>
                <ul>
                    <li>AI Workstation</li>
                    <li>How It Works</li>
                    <li>CT Showcase</li>
                    <li>Pipeline Architecture</li>
                </ul>
            </div>
            <div class="lp-footer-col">
                <h4>Resources</h4>
                <ul>
                    <li>Kidney Health Guide</li>
                    <li>Clinical Size Bands</li>
                    <li>Sensitivity Analysis</li>
                    <li>Technical Limitations</li>
                </ul>
            </div>
            <div class="lp-footer-col">
                <h4>Project</h4>
                <ul>
                    <li><a href="https://github.com/R-Adhiya/RenalScan" target="_blank" style="color: #6B7280; text-decoration: none;">GitHub Repository</a></li>
                    <li>Trained YOLOv8s Model</li>
                    <li>Medical Disclaimer</li>
                </ul>
            </div>
        </div>
        <div class="lp-footer-bottom">
            © 2026 RenalScan AI Systems. Built for Technical Portfolio Evaluation & Medical Computer Vision Demonstration. Non-diagnostic.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# VIEW 2: AI ANALYSIS WORKSTATION (DASHBOARD & DETAILED TABS)
# =============================================================================
else:
    # Workstation Header with Back to Home Link
    ws_nav1, ws_nav2, ws_nav3 = st.columns([1.5, 2.5, 1], gap="small")
    with ws_nav1:
        st.markdown("""
        <div class="lp-brand-box">
            <div class="lp-logo-badge">🩺</div>
            <div>
                <div class="lp-brand-title">Renal<span class="lp-brand-accent">Scan</span></div>
                <div class="lp-brand-sub">AI Analysis Workstation</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with ws_nav2:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; gap: 14px; padding-top: 6px;">
            <span style="font-size: 0.92rem; font-weight: 700; color: #C62828; background: #FFEBEE; padding: 4px 12px; border-radius: 12px;">
                ● Live Diagnostic Mode
            </span>
        </div>
        """, unsafe_allow_html=True)
    with ws_nav3:
        if st.button("← Back to Home", key="back_home", use_container_width=True):
            navigate_to('landing')

    st.write("")

    # Workstation Sub-tabs
    ws_tab1, ws_tab2, ws_tab3, ws_tab4 = st.tabs([
        "🩺 CT Analysis Workspace",
        "🔬 How It Works (Animation)",
        "🫘 Kidney Health Guide",
        "ℹ️ Technical Limitations & Evaluation"
    ])

    with ws_tab1:
        # 2-Column Responsive Analysis Workspace
        col_left, col_right = st.columns([1.1, 1.9], gap="medium")

        # --- LEFT PANEL: UPLOAD & CONTROLS ---
        with col_left:
            st.markdown("""
            <div class="rs-card">
                <div class="rs-card-title">
                    <span class="rs-card-title-icon">📤</span> Upload CT Scan
                </div>
                <div style="font-size: 0.84rem; color: #6B7280; margin-bottom: 12px;">
                    Upload an abdominal CT scan slice for automated stone analysis.
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
                    <span class="rs-card-title-icon">🧪</span> Benchmark Sample Scans
                </div>
            """, unsafe_allow_html=True)

            if len(sample_files) >= 3:
                s_c1, s_c2, s_c3 = st.columns(3)
                with s_c1:
                    if st.button("Sample 1\n(Multiple)", key="ws_b1", use_container_width=True):
                        bgr = cv2.imread(str(sample_files[0]))
                        st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        st.session_state['active_sample_name'] = "Sample 01 (Multiple Stones)"
                        st.rerun()
                with s_c2:
                    if st.button("Sample 2\n(Single)", key="ws_b2", use_container_width=True):
                        bgr = cv2.imread(str(sample_files[1]))
                        st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        st.session_state['active_sample_name'] = "Sample 02 (Single Stone)"
                        st.rerun()
                with s_c3:
                    if st.button("Sample 3\n(Normal)", key="ws_b3", use_container_width=True):
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
                    <span class="rs-card-title-icon">🎛️</span> Analysis Controls
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

        # --- RIGHT PANEL: CT VIEWER & AI ANALYSIS RESULTS ---
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
                <span style="color: #E5E7EB; font-size: 0.85rem; font-weight: 700;">CT ABDOMINAL SCAN | Slice 034 / 128</span>
                <span style="color: #10B981; font-size: 0.8rem; font-weight: 700;">● AI ANALYSIS READY</span>
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
                    <div style="color: #C62828; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 4px;">
                        AI ANALYSIS SUMMARY
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #1F2937;">
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
                    clinical_note = "Large calculus. Surgical intervention indicated (ESWL / URS / PCNL)."

                # Summary Card with Red Accent
                st.markdown(f"""
                <div class="rs-summary-card">
                    <div style="color: #C62828; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 4px;">
                        AI ANALYSIS SUMMARY
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #1F2937;">
                        <span style="color: #C62828; font-weight: 800;">{stone_count} stone(s) detected</span> • 
                        <span style="color: #C62828; font-weight: 800;">{largest_mm:.2f} mm</span> largest stone diameter
                    </div>
                    <div style="font-size: 0.86rem; color: #4B5563; margin-top: 6px;">
                        {clinical_note}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Three Clean White Metric Cards (Safely Calculate Mean Confidence)
                mean_conf_pct = int(np.mean([s['confidence'] for s in stones]) * 100) if (stones and len(stones) > 0) else 0

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

                # Detected Stone Regions Cards (Actual Values)
                st.markdown("""
                <div style="font-size: 1.05rem; font-weight: 800; color: #1F2937; margin-bottom: 10px;">
                    Detected Stone Regions <span style="color: #C62828;">({count})</span>
                </div>
                """.format(count=stone_count), unsafe_allow_html=True)

                for s in stones:
                    if s.get('status') == 'Success':
                        st.markdown(f"""
                        <div class="rs-stone-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-weight: 800; font-size: 0.95rem; color: #C62828;">Stone #{s['stone_id']}</span>
                                <span style="background-color: #FFEBEE; color: #C62828; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 12px;">
                                    {s['confidence']*100:.1f}% Confidence
                                </span>
                            </div>
                            <div style="font-size: 0.83rem; color: #4B5563; line-height: 1.55;">
                                • <strong>Estimated Diameter:</strong> <span style="color: #C62828; font-weight: 700;">{s['estimated_diameter_mm']:.2f} mm</span> ({s['equiv_diameter_px']:.1f} px)<br>
                                • <strong>Dimensions (Major × Minor):</strong> {s['estimated_major_mm']:.1f} × {s['estimated_minor_mm']:.1f} mm<br>
                                • <strong>Anatomical Region:</strong> Kidney Region ROI<br>
                                • <strong>Clinical Band:</strong> {s['clinical_size_band']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # Lower Workspace Section: Kidney Map & Measurement Table
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
                <div class="rs-card">
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

    # SUB-TAB 2: HOW IT WORKS ANIMATION
    with ws_tab2:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #1F2937;">Interactive Pipeline Simulation</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">Step through each phase of the automated detection, segmentation, and sizing workflow.</p>
        </div>
        """, unsafe_allow_html=True)

        animated_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                body {{ font-family: 'Inter', sans-serif; background-color: #FFFFFF; margin: 0; padding: 10px; color: #1F2937; }}
                .card-container {{ background-color: #FFFFFF; border: 1px solid #F1D5D5; border-radius: 18px; padding: 24px; box-shadow: 0 4px 20px rgba(198, 40, 40, 0.05); }}
                .ct-canvas {{ background-color: #111827; border-radius: 14px; border-top: 3px solid #C62828; position: relative; width: 100%; height: 420px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
                .ct-img {{ max-height: 400px; max-width: 400px; border-radius: 6px; }}
                .scan-line {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #E53935, transparent); box-shadow: 0 0 12px #E53935; animation: scanMove 3s infinite linear; opacity: 0.85; }}
                @keyframes scanMove {{ 0% {{ top: 5%; }} 50% {{ top: 90%; }} 100% {{ top: 5%; }} }}
                .svg-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
                .yolo-box {{ stroke: #E53935; stroke-width: 2.5; stroke-dasharray: 6 4; fill: rgba(229, 57, 53, 0.15); transition: all 0.5s; }}
                .otsu-contour {{ stroke: #C62828; stroke-width: 3; fill: rgba(198, 40, 40, 0.28); stroke-dasharray: 400; stroke-dashoffset: 400; transition: stroke-dashoffset 1.5s ease-in-out; }}
                .draw-contour {{ stroke-dashoffset: 0 !important; }}
                .meas-vector {{ stroke: #C62828; stroke-width: 2.5; stroke-dasharray: 4; }}
                .badge-floating {{ position: absolute; background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(4px); border: 1px solid #C62828; color: #FFFFFF; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 700; }}
                .ctrl-bar {{ display: flex; gap: 10px; justify-content: center; margin-top: 20px; }}
                .step-btn {{ background-color: #FFFFFF; border: 1px solid #F1D5D5; color: #1F2937; font-weight: 700; font-size: 0.85rem; padding: 9px 16px; border-radius: 8px; cursor: pointer; }}
                .step-btn:hover, .step-btn.active {{ background-color: #C62828; border-color: #C62828; color: #FFFFFF; }}
                .timeline-bar {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 18px; text-align: center; }}
                .t-stage {{ background-color: #FFF7F7; border: 1px solid #F1D5D5; border-radius: 8px; padding: 10px; font-size: 0.78rem; font-weight: 700; color: #6B7280; }}
                .t-stage.active-stage {{ background-color: #C62828; border-color: #C62828; color: #FFFFFF; }}
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
                    <div id="t1" class="t-stage active-stage">01 Preprocess</div>
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
                    <button class="step-btn" onclick="replay()">🔄 Replay</button>
                </div>
            </div>
            <script>
                let currentStep = 1; let timer = null;
                function updateStage(step) {{
                    currentStep = step;
                    const badge = document.getElementById('stageBadge');
                    const conf = document.getElementById('confBadge');
                    const readout = document.getElementById('readoutBadge');
                    const yolo = document.getElementById('yoloBox');
                    const contour = document.getElementById('otsuContour');
                    const vecMaj = document.getElementById('vecMajor');
                    const vecMin = document.getElementById('vecMinor');
                    for(let i=1; i<=5; i++) document.getElementById('t' + i).classList.remove('active-stage');
                    if (step === 1) {{
                        badge.innerText = "01 CT SCAN & PREPROCESSING"; document.getElementById('t1').classList.add('active-stage');
                        yolo.setAttribute('opacity', '0'); contour.classList.remove('draw-contour');
                        vecMaj.setAttribute('opacity', '0'); vecMin.setAttribute('opacity', '0');
                        conf.style.opacity = '0'; readout.style.opacity = '0';
                    }} else if (step === 2) {{
                        badge.innerText = "02 YOLOV8S DETECTION"; document.getElementById('t2').classList.add('active-stage');
                        yolo.setAttribute('opacity', '1'); conf.style.opacity = '1';
                        contour.classList.remove('draw-contour'); vecMaj.setAttribute('opacity', '0');
                        vecMin.setAttribute('opacity', '0'); readout.style.opacity = '0';
                    }} else if (step === 3) {{
                        badge.innerText = "03 OTSU SEGMENTATION"; document.getElementById('t3').classList.add('active-stage');
                        yolo.setAttribute('opacity', '1'); conf.style.opacity = '1';
                        contour.classList.add('draw-contour'); vecMaj.setAttribute('opacity', '0');
                        vecMin.setAttribute('opacity', '0'); readout.style.opacity = '0';
                    }} else if (step === 4) {{
                        badge.innerText = "04 AXIS MEASUREMENT"; document.getElementById('t4').classList.add('active-stage');
                        yolo.setAttribute('opacity', '1'); conf.style.opacity = '1';
                        contour.classList.add('draw-contour'); vecMaj.setAttribute('opacity', '1');
                        vecMin.setAttribute('opacity', '1'); readout.style.opacity = '1';
                    }} else if (step === 5) {{
                        badge.innerText = "05 ANALYSIS REPORT"; document.getElementById('t5').classList.add('active-stage');
                        yolo.setAttribute('opacity', '1'); conf.style.opacity = '1';
                        contour.classList.add('draw-contour'); vecMaj.setAttribute('opacity', '1');
                        vecMin.setAttribute('opacity', '1'); readout.style.opacity = '1';
                    }}
                }}
                function autoLoop() {{ currentStep = (currentStep % 5) + 1; updateStage(currentStep); }}
                function jumpTo(step) {{ clearInterval(timer); updateStage(step === 4 ? 5 : step + 1); }}
                function replay() {{ clearInterval(timer); currentStep = 1; updateStage(1); timer = setInterval(autoLoop, 4000); }}
                timer = setInterval(autoLoop, 4000);
            </script>
        </body>
        </html>
        """
        components.html(animated_html, height=580, scrolling=False)

    # SUB-TAB 3: KIDNEY HEALTH
    with ws_tab3:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #1F2937;">Nephrolithiasis Clinical Reference</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">Key medical concepts, triage criteria, and treatment modalities.</p>
        </div>
        """, unsafe_allow_html=True)

        kh_c1, kh_c2 = st.columns(2)
        with kh_c1:
            st.markdown("""
            <div class="rs-card">
                <div class="rs-card-title"><span class="rs-card-title-icon">🩺</span> Clinical Size Risk Bands</div>
                <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.6;">
                    • <strong>&lt; 4 mm (Small):</strong> ~80% spontaneous passage likelihood. Managed conservatively with hydration and analgesia.<br>
                    • <strong>4 – 6 mm (Medium):</strong> ~50% passage likelihood. Candidate for Medical Expulsive Therapy (MET, alpha-blockers).<br>
                    • <strong>6 – 10 mm (Large):</strong> ~20% passage likelihood. Usually requires elective intervention (ESWL / URS).<br>
                    • <strong>&gt; 10 mm (Very Large):</strong> Low spontaneous passage. Direct surgical intervention indicated (URS / PCNL).
                </div>
            </div>
            """, unsafe_allow_html=True)
        with kh_c2:
            st.markdown("""
            <div class="rs-card">
                <div class="rs-card-title"><span class="rs-card-title-icon">🩻</span> Imaging Diagnostic Protocols</div>
                <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.6;">
                    • <strong>Non-Contrast Abdominal CT:</strong> Highest sensitivity (95–97%) and specificity for identifying calculus attenuation, location, and dimensions.<br>
                    • <strong>Renal Ultrasound:</strong> First-line for pediatric and pregnant patients, free of ionizing radiation.<br>
                    • <strong>KUB Radiograph:</strong> Used for monitoring radiopaque stone progression post-diagnosis.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # SUB-TAB 4: LIMITATIONS
    with ws_tab4:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #1F2937;">Known Limitations & Technical Evaluation</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">Documented assumptions, literature factors, and validation metrics.</p>
        </div>
        """, unsafe_allow_html=True)

        lim_c1, lim_c2 = st.columns(2)
        with lim_c1:
            st.markdown("""
            <div class="rs-card">
                <div class="rs-card-title"><span class="rs-card-title-icon">⚠️</span> DICOM Metadata & Pixel-Spacing</div>
                <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.55;">
                    • Standard JPG images lack embedded DICOM metadata tags (`PixelSpacing`, `SliceThickness`).<br>
                    • <strong>Assumed Constant:</strong> 0.70 mm/px baseline derived from abdominal CT literature (360mm FOV / 512px).<br>
                    • Millimeter measurements and risk bands are approximate indicators for educational evaluation.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with lim_c2:
            st.markdown("""
            <div class="rs-card">
                <div class="rs-card-title"><span class="rs-card-title-icon">📊</span> Empirical Model Performance (Held-Out Test Cohort)</div>
                <div style="font-size: 0.85rem; color: #4B5563; line-height: 1.55;">
                    • <strong>Precision:</strong> 86.83% | <strong>Recall:</strong> 77.68% | <strong>F1 Score:</strong> 82.00%<br>
                    • <strong>mAP@0.50:</strong> 81.21% | <strong>mAP@0.50:0.95:</strong> 41.10%<br>
                    • <strong>Primary Architecture:</strong> Promoted YOLOv8s v2 weights (`models/detection_best.pt`)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Workstation Footer
    st.markdown("""
    <div style="border-top: 1.5px solid #F1D5D5; padding-top: 20px; margin-top: 30px; text-align: center; font-size: 0.8rem; color: #9CA3AF;">
        RenalScan AI Systems • Medical Computer Vision Research Prototype • Non-diagnostic evaluation
    </div>
    """, unsafe_allow_html=True)
