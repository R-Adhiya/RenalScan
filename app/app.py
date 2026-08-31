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

# Page Configuration - Light Theme Default
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Diagnostic System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS — Light Medical AI Theme (#F7F9FC Background, #FFFFFF Surfaces, #0EA5A4 Medical Cyan)
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Global Light Background */
    .stApp {
        background-color: #F7F9FC;
        color: #0F172A;
    }
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* Top Navigation Bar */
    .rs-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        padding: 14px 32px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 24px;
    }
    .rs-logo-group {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rs-logo-icon {
        width: 32px;
        height: 32px;
        background-color: rgba(14, 165, 164, 0.12);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0EA5A4;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .rs-logo-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .rs-logo-badge {
        font-size: 0.72rem;
        font-weight: 600;
        background-color: #F1F5F9;
        color: #64748B;
        padding: 2px 8px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    .rs-nav-links {
        display: flex;
        gap: 28px;
        font-size: 0.92rem;
        font-weight: 500;
        color: #475569;
    }
    .rs-nav-link {
        color: #475569;
        text-decoration: none;
        transition: color 0.2s;
    }
    .rs-nav-link:hover {
        color: #0EA5A4;
    }
    .rs-nav-link.active {
        color: #0EA5A4;
        font-weight: 600;
    }

    /* Hero Landing Section */
    .rs-hero-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 40px 48px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);
    }
    .rs-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(14, 165, 164, 0.08);
        color: #0EA5A4;
        border: 1px solid rgba(14, 165, 164, 0.2);
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 16px;
    }
    .rs-hero-headline {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin-bottom: 12px;
    }
    .rs-hero-subheadline {
        font-size: 1.1rem;
        color: #64748B;
        max-width: 680px;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    /* Research Prototype Notice Strip */
    .rs-notice-strip {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 4px solid #D97706;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #92400E;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 24px;
    }
    .rs-notice-tag {
        font-weight: 700;
        color: #B45309;
    }

    /* Sample CT Scan Cards */
    .rs-sample-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .rs-sample-card:hover {
        border-color: #0EA5A4;
        box-shadow: 0 4px 12px rgba(14, 165, 164, 0.12);
        transform: translateY(-2px);
    }
    .rs-sample-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .rs-sample-desc {
        font-size: 0.82rem;
        color: #64748B;
    }

    /* 5-Step Pipeline Bar */
    .rs-pipeline-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 28px;
        margin-bottom: 24px;
    }
    .rs-step-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #64748B;
    }
    .rs-step-item.active {
        color: #0EA5A4;
    }
    .rs-step-num {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background-color: #F1F5F9;
        color: #64748B;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .rs-step-item.active .rs-step-num {
        background-color: #0EA5A4;
        color: #FFFFFF;
    }

    /* CT Scan Viewer Canvas Container (Dark Charcoal Imaging Surface) */
    .rs-viewer-container {
        background-color: #0B0F19;
        border-radius: 12px;
        border: 1px solid #1E293B;
        padding: 16px;
        position: relative;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .rs-viewer-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 12px;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 12px;
    }
    .rs-viewer-title {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .rs-viewer-status {
        color: #0EA5A4;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* Summary Card */
    .rs-summary-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0EA5A4;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .rs-teal-text {
        color: #0EA5A4;
        font-weight: 700;
    }

    /* Control Panel Cards */
    .rs-panel-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .rs-panel-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Stone Result Cards */
    .rs-stone-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .rs-stone-card:hover {
        border-color: #0EA5A4;
    }
    .rs-stone-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .rs-stone-id {
        font-weight: 700;
        color: #0F172A;
        font-size: 0.95rem;
    }
    .rs-stone-conf {
        background-color: rgba(14, 165, 164, 0.1);
        color: #0EA5A4;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 2px 8px;
        border-radius: 10px;
    }

    /* Footer */
    .rs-footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        color: #94A3B8;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP NAVIGATION BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-navbar">
    <div class="rs-logo-group">
        <div class="rs-logo-icon">🩺</div>
        <div class="rs-logo-text">RenalScan</div>
        <div class="rs-logo-badge">AI Imaging Workstation</div>
    </div>
    <div class="rs-nav-links">
        <span class="rs-nav-link active">Analysis</span>
        <span class="rs-nav-link">Pipeline Architecture</span>
        <span class="rs-nav-link">Technology Stack</span>
        <span class="rs-nav-link">Research & About</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# RESEARCH PROTOTYPE NOTICE STRIP
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="rs-notice-strip">
    <span>ⓘ</span>
    <span><span class="rs-notice-tag">Research & Educational Prototype:</span> Physical dimension measurements and urological size classifications are literature-based estimations ({ASSUMED_MM_PER_PIXEL} mm/px FOV constant). This software is intended for technical evaluation and portfolio demonstration — not for clinical diagnosis or surgical decision-making.</span>
</div>
""", unsafe_allow_html=True)

# Pipeline Model Loader
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

# Sample files directory
sample_dir = PROJECT_ROOT / "data" / "test" / "images"
sample_files = sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []

# -----------------------------------------------------------------------------
# HERO LANDING SECTION (When no scan is loaded)
# -----------------------------------------------------------------------------
if st.session_state['active_image'] is None:
    hero_col1, hero_col2 = st.columns([1.6, 1])
    
    with hero_col1:
        st.markdown("""
        <div class="rs-hero-card">
            <div class="rs-hero-badge">● AI Computer Vision Pipeline v2.0</div>
            <div class="rs-hero-headline">AI-Powered Kidney Stone Diagnostic & Measurement System</div>
            <div class="rs-hero-subheadline">
                Locate, segment, and quantitatively measure kidney stones from abdominal CT scans using YOLOv8 deep learning detection and classical CV contour analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with hero_col2:
        st.markdown("### 📤 Upload Abdominal CT Scan")
        uploaded_file = st.file_uploader(
            "Drag & drop CT scan image (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            help="Upload plain 512x512 or 640x640 abdominal CT image slice."
        )
        
        if uploaded_file is not None:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if bgr_img is not None:
                st.session_state['active_image'] = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = uploaded_file.name
                st.rerun()

    st.markdown("---")
    st.markdown("### 🧪 Explore with Sample CT Scans")
    st.write("Click any sample scan below to load it into the interactive AI workstation:")
    
    scol1, scol2, scol3 = st.columns(3)
    
    if len(sample_files) >= 3:
        with scol1:
            st.markdown("""
            <div class="rs-sample-card">
                <div class="rs-sample-title">Sample 01 — Multiple Stones</div>
                <div class="rs-sample-desc">CT scan with multiple kidney stone candidates</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Analyze Sample 01", key="btn_sample1", use_container_width=True):
                bgr = cv2.imread(str(sample_files[0]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[0].name
                st.rerun()
                
        with scol2:
            st.markdown("""
            <div class="rs-sample-card">
                <div class="rs-sample-title">Sample 02 — Single Stone</div>
                <div class="rs-sample-desc">CT scan with a prominent solitary renal calculus</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Analyze Sample 02", key="btn_sample2", use_container_width=True):
                bgr = cv2.imread(str(sample_files[1]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[1].name
                st.rerun()
                
        with scol3:
            st.markdown("""
            <div class="rs-sample-card">
                <div class="rs-sample-title">Sample 03 — Normal / Small Scan</div>
                <div class="rs-sample-desc">CT scan slice for edge case & threshold testing</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Analyze Sample 03", key="btn_sample3", use_container_width=True):
                bgr = cv2.imread(str(sample_files[2]))
                st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                st.session_state['active_sample_name'] = sample_files[2].name
                st.rerun()

# -----------------------------------------------------------------------------
# MAIN ANALYSIS WORKSPACE (When a CT scan image is active)
# -----------------------------------------------------------------------------
else:
    # Top Actions Bar
    tcol1, tcol2 = st.columns([3, 1])
    with tcol1:
        st.markdown(f"**Loaded Scan:** `{st.session_state['active_sample_name']}`")
    with tcol2:
        if st.button("🔄 Upload New CT Scan", use_container_width=True):
            st.session_state['active_image'] = None
            st.session_state['active_sample_name'] = None
            st.rerun()
            
    # 5-Step Pipeline Bar
    st.markdown("""
    <div class="rs-pipeline-bar">
        <div class="rs-step-item active"><span class="rs-step-num">01</span> Preprocess ✓</div>
        <div class="rs-step-item active"><span class="rs-step-num">02</span> YOLOv8 Detect ✓</div>
        <div class="rs-step-item active"><span class="rs-step-num">03</span> Otsu Segment ✓</div>
        <div class="rs-step-item active"><span class="rs-step-num">04</span> Geometry Measure ✓</div>
        <div class="rs-step-item active"><span class="rs-step-num">05</span> Clinical Report ✓</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3-COLUMN WORKSPACE LAYOUT
    ctrl_col, view_col, res_col = st.columns([1, 2.2, 1.4])
    
    # --- LEFT COLUMN: ANALYSIS CONTROLS ---
    with ctrl_col:
        st.markdown('<div class="rs-panel-card"><div class="rs-panel-title">⚙️ Detection Controls</div>', unsafe_allow_html=True)
        conf_thresh = st.slider(
            "Confidence Threshold",
            min_value=0.10,
            max_value=0.90,
            value=0.40,
            step=0.05,
            help="Filters YOLOv8 detections below this minimum confidence score."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="rs-panel-card"><div class="rs-panel-title">👁️ Visualization Mode</div>', unsafe_allow_html=True)
        overlay_mode = st.radio(
            "Select Diagnostic Overlay",
            options=["3. Axis Measurement Vectors", "2. Classical CV Masks", "1. YOLOv8 Detections", "Original CT Scan Only"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="rs-panel-card"><div class="rs-panel-title">🎛️ Image Adjustments</div>', unsafe_allow_html=True)
        brightness = st.slider("Brightness", -50, 50, 0, step=5)
        contrast = st.slider("Contrast", -50, 50, 0, step=5)
        st.markdown('</div>', unsafe_allow_html=True)

    # Apply Image Adjustments to Active CT Array
    processed_img = st.session_state['active_image'].copy()
    if brightness != 0 or contrast != 0:
        processed_img = cv2.convertScaleAbs(processed_img, alpha=1.0 + (contrast/100.0), beta=brightness)

    # Run End-to-End Pipeline
    with st.spinner("Analyzing CT scan — detecting, segmenting, and measuring stones..."):
        result = pipeline.analyze(processed_img, conf_thresh=conf_thresh)
        
    summary = result['summary']
    stones = result['stones']

    # --- CENTER COLUMN: CT SCAN VIEWER WORKSTATION ---
    with view_col:
        st.markdown("""
        <div class="rs-viewer-container">
            <div class="rs-viewer-header">
                <span class="rs-viewer-title">CT ABDOMINAL SCAN | Slice 034 / 128</span>
                <span class="rs-viewer-status">● AI ANALYSIS READY</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Display Active Image based on Overlay Control Choice
        if overlay_mode == "1. YOLOv8 Detections":
            st.image(result['annotated_detection'], use_container_width=True)
        elif overlay_mode == "2. Classical CV Masks":
            st.image(result['annotated_segmentation'], use_container_width=True)
        elif overlay_mode == "3. Axis Measurement Vectors":
            st.image(result['annotated_measurement'], use_container_width=True)
        else:
            st.image(result['original_image'], use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparison Expander (Before vs After)
        with st.expander("🔍 Before / After Segmentation Comparison View"):
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                st.caption("Original Input CT Scan")
                st.image(result['original_image'], use_container_width=True)
            with comp_col2:
                st.caption("AI Segmentation Mask Overlay")
                st.image(result['annotated_segmentation'], use_container_width=True)

    # --- RIGHT COLUMN: AI ANALYSIS RESULTS & METRICS ---
    with res_col:
        # Plain-English Summary Sentence Banner
        if not summary['has_stones']:
            st.warning(f"ℹ️ **No Stone Regions Detected**: No high-confidence candidate stone regions were detected in this CT scan slice (Confidence Threshold: {conf_thresh:.2f}).")
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
            <div class="rs-summary-box">
                💡 <strong>Analysis Summary:</strong> Detected <span class="rs-teal-text">{stone_count} stone(s)</span>. The largest is estimated at <span class="rs-teal-text">{largest_mm:.2f} mm</span>, which {guidance}.
            </div>
            """, unsafe_allow_html=True)
            
            # Metric Cards
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Total Stones", f"{stone_count}")
            with m2:
                st.metric("Largest Size", f"{largest_mm} mm*")
                
            st.markdown("#### 💎 Detected Stone Regions")
            
            for s in stones:
                if s.get('status') == 'Success':
                    st.markdown(f"""
                    <div class="rs-stone-card">
                        <div class="rs-stone-header">
                            <span class="rs-stone-id">Stone #{s['stone_id']}</span>
                            <span class="rs-stone-conf">{s['confidence']*100:.1f}% Conf</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #475569;">
                            • <strong>Est. Diameter:</strong> {s['estimated_diameter_mm']:.2f} mm*<br>
                            • <strong>Major × Minor:</strong> {s['estimated_major_mm']:.1f} × {s['estimated_minor_mm']:.1f} mm<br>
                            • <strong>Treatment Category:</strong> {s['clinical_size_band']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # -----------------------------------------------------------------------------
    # DETAILED QUANTITATIVE MEASUREMENT TABLE & REPORT EXPORT
    # -----------------------------------------------------------------------------
    st.markdown("### 📊 Per-Stone Quantitative Measurement Breakdown")
    
    if summary['has_stones']:
        df_records = []
        for s in stones:
            if s.get('status') == 'Success':
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'AI Confidence': s['confidence'],
                    'Mask Area (px²)': s['area_px'],
                    'Major Axis (px)': s['major_axis_px'],
                    'Minor Axis (px)': s['minor_axis_px'],
                    'Est. Diameter (mm)*': s['estimated_diameter_mm'],
                    'Clinical Size Band & Outlook': s['clinical_size_band']
                })
        df_display = pd.DataFrame(df_records)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "AI Confidence": st.column_config.NumberColumn("AI Confidence", format="%.2f"),
                "Mask Area (px²)": st.column_config.NumberColumn("Mask Area (px²)", format="%.1f px²"),
                "Major Axis (px)": st.column_config.NumberColumn("Major Axis (px)", format="%.1f px"),
                "Minor Axis (px)": st.column_config.NumberColumn("Minor Axis (px)", format="%.1f px"),
                "Est. Diameter (mm)*": st.column_config.NumberColumn("Est. Diameter (mm)*", format="%.2f mm"),
                "Clinical Size Band & Outlook": st.column_config.TextColumn("Clinical Size Band & Outlook")
            }
        )
        st.caption(f"*DISCLAIMER: {NON_CLINICAL_DISCLAIMER}")

        # REPORT EXPORT PANEL
        st.markdown("### 📄 Export Diagnostic Analysis Report")
        ex_col1, ex_col2 = st.columns(2)
        
        with ex_col1:
            # Generate Downloadable Markdown Report
            report_text = f"# RenalScan AI Diagnostic Report\n"
            report_text += f"Scan ID: {st.session_state['active_sample_name']}\n"
            report_text += f"Confidence Threshold: {conf_thresh}\n"
            report_text += f"Stones Detected: {summary['stone_count']}\n"
            report_text += f"Largest Stone: {summary['largest_stone_diameter_mm']} mm ({summary['largest_stone_size_band']})\n\n"
            report_text += "## Detailed Stone Measurements\n"
            for s in stones:
                report_text += f"- Stone #{s['stone_id']}: Confidence={s['confidence']*100:.1f}%, Est Diam={s['estimated_diameter_mm']:.2f}mm, Band={s['clinical_size_band']}\n"
            report_text += f"\nDISCLAIMER: {NON_CLINICAL_DISCLAIMER}\n"
            
            st.download_button(
                "📥 Download Analysis Summary Report (.txt)",
                data=report_text,
                file_name=f"RenalScan_Report_{st.session_state['active_sample_name']}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with ex_col2:
            # Export CSV Data
            csv_data = df_display.to_csv(index=False)
            st.download_button(
                "📊 Export Measurements CSV (.csv)",
                data=csv_data,
                file_name=f"RenalScan_Measurements_{st.session_state['active_sample_name']}.csv",
                mime="text/csv",
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="rs-footer">
    <strong>RenalScan</strong> — AI-Powered Kidney Stone Analysis System | Research & Educational Prototype<br>
    Built for Technical Portfolio Evaluation & Medical Computer Vision Demonstration
</div>
""", unsafe_allow_html=True)
