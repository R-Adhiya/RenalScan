import sys
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

# Configure Streamlit Page
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Diagnostics",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling Pass (Clinical Slate Navy & Medical Teal Palette)
st.markdown("""
<style>
    /* Global Container Adjustments */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }
    
    /* Header Styling */
    .title-primary {
        color: #0D9488;
        font-size: 2.3rem;
        font-weight: 800;
        display: inline;
    }
    .title-secondary {
        color: #E2E8F0;
        font-size: 2.3rem;
        font-weight: 700;
        display: inline;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 6px;
        margin-bottom: 16px;
        opacity: 0.85;
    }
    .header-divider {
        height: 1px;
        background-color: rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }

    /* Disclaimer Notice Card */
    .disclaimer-notice {
        background-color: rgba(239, 68, 68, 0.08);
        border-left: 3px solid #F87171;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 0.92rem;
        color: #CBD5E1;
        line-height: 1.5;
    }
    .disclaimer-tag {
        color: #FCA5A5;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    /* 3-Step Process Guide Cards */
    .step-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px 18px;
        height: 100%;
        transition: border-color 0.2s ease;
    }
    .step-card:hover {
        border-color: #0D9488;
    }
    .step-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #0D9488;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 8px;
    }
    .step-title {
        color: #E2E8F0;
        font-weight: 700;
        font-size: 1.05rem;
        display: inline-block;
        vertical-align: middle;
    }
    .step-arrow {
        color: #0D9488;
        font-size: 1.2rem;
        float: right;
    }
    .step-desc {
        color: #CBD5E1;
        font-size: 0.88rem;
        margin-top: 10px;
        line-height: 1.4;
        opacity: 0.85;
    }

    /* Summary Sentence Focal Card */
    .summary-card {
        background-color: #1E293B;
        border: 1px solid #0D9488;
        border-left: 5px solid #0D9488;
        padding: 18px 22px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #E2E8F0;
        line-height: 1.5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .highlight-teal {
        color: #0D9488;
        font-weight: 700;
    }

    /* Panel Card Wrappers */
    .panel-card {
        background-color: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .panel-card:hover {
        border-color: #0D9488;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15);
    }
    .panel-header {
        color: #E2E8F0;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .panel-subtitle {
        color: #94A3B8;
        font-size: 0.85rem;
        margin-bottom: 12px;
        min-height: 36px;
    }

    /* Results Animation Container */
    .results-container {
        animation: fadeIn 0.4s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# 1. HEADER SECTION
st.markdown("""
<div>
    <span class="title-primary">RenalScan</span>
    <span class="title-secondary"> — AI Kidney Stone Diagnostic System</span>
</div>
<div class="header-subtitle">
    Automated 3-Step CT Scan Analysis: Locate Stones ➔ Outline Boundaries ➔ Measure Physical Dimensions
</div>
<div class="header-divider"></div>
""", unsafe_allow_html=True)

# 2. DISCLAIMER BANNER (Notice Style, Unconditional on Every View)
st.markdown(f"""
<div class="disclaimer-notice">
    <span class="disclaimer-tag">⚠️ NON-CLINICAL PORTFOLIO DISCLAIMER:</span>
    All millimeter measurements and clinical size classifications are estimates derived from a literature-based baseline constant (fixed at {ASSUMED_MM_PER_PIXEL} mm/px FOV). This application is designed exclusively for technical portfolio evaluation and must not be used for medical diagnosis or surgical treatment decisions.
</div>
""", unsafe_allow_html=True)

# 3. SIDEBAR CONTROLS
st.sidebar.title("⚙️ Diagnostic Controls")

@st.cache_resource
def load_pipeline():
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=ASSUMED_MM_PER_PIXEL)

conf_thresh = st.sidebar.slider(
    "Sensitivity / Confidence Threshold",
    min_value=0.10,
    max_value=0.90,
    value=0.40,
    step=0.05,
    help="Controls how strictly candidate kidney stone detections are filtered."
)

pipeline = load_pipeline()

st.sidebar.markdown("---")
st.sidebar.subheader("📷 Input CT Scan Selection")

sample_dir = PROJECT_ROOT / "data" / "test" / "images"
sample_files = sorted(list(sample_dir.glob("*.jpg")))[:10] if sample_dir.exists() else []

sample_options = ["None (Upload Own File)"] + [f.name for f in sample_files]
selected_sample = st.sidebar.selectbox("Choose Sample Test CT Image", sample_options)

uploaded_file = st.sidebar.file_uploader("Or Upload Custom CT Scan (JPG/PNG)", type=["jpg", "jpeg", "png"])

input_img_array = None

if uploaded_file is not None:
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if bgr_img is not None:
        input_img_array = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
elif selected_sample != "None (Upload Own File)":
    sample_path = sample_dir / selected_sample
    bgr_img = cv2.imread(str(sample_path))
    if bgr_img is not None:
        input_img_array = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)

# Helper function for plain-English summary sentence
def get_plain_english_summary(stone_count, largest_mm, largest_band):
    if stone_count == 0:
        return "ℹ️ <strong>Analysis Summary:</strong> No kidney stones were detected in this CT scan."
    
    if "<4mm" in largest_band:
        guidance = "typically passes on its own with hydration"
        treatment = "conservative observation is recommended"
    elif "4-6mm" in largest_band:
        guidance = "may require medical expulsion therapy"
        treatment = "observation or medication is typically advised"
    elif "6-10mm" in largest_band:
        guidance = "has a low likelihood of spontaneous passage"
        treatment = "specialized urological procedure is usually indicated"
    else: # >10mm
        guidance = "is unlikely to pass spontaneously"
        treatment = "surgical intervention (ESWL/URS/PCNL) is typically required"
        
    return (
        f"💡 <strong>Analysis Summary:</strong> This scan shows <span class=\"highlight-teal\">{stone_count} kidney stone(s)</span>. "
        f"The largest is about <span class=\"highlight-teal\">{largest_mm:.2f} mm</span>, which {guidance} — {treatment}."
    )

# 4. MAIN APPLICATION FLOW
if input_img_array is None:
    st.info("👈 Select a sample CT scan from the sidebar or upload your own file to run the diagnostic pipeline.")
    
    st.markdown("### 📋 How the 3-Step Analysis Works")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("""
        <div class="step-card">
            <div>
                <span class="step-circle">1</span>
                <span class="step-title">Locate Stones</span>
                <span class="step-arrow">➔</span>
            </div>
            <div class="step-desc">AI scans the abdominal CT image to pinpoint exact kidney stone locations.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown("""
        <div class="step-card">
            <div>
                <span class="step-circle">2</span>
                <span class="step-title">Trace Boundaries</span>
                <span class="step-arrow">➔</span>
            </div>
            <div class="step-desc">Computer vision algorithms outline precise stone edge contours and shapes.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c:
        st.markdown("""
        <div class="step-card">
            <div>
                <span class="step-circle">3</span>
                <span class="step-title">Measure Size</span>
            </div>
            <div class="step-desc">Calculates major/minor axes and maps physical dimensions to urological bands.</div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Specific Loading Spinner
    with st.spinner("Analyzing CT scan — detecting, segmenting, and measuring stones..."):
        result = pipeline.analyze(input_img_array, conf_thresh=conf_thresh)
        
    summary = result['summary']
    stones = result['stones']
    
    # Results Fade-In Container
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Plain-English Summary Focal Card
    summary_html = get_plain_english_summary(
        summary['stone_count'],
        summary['largest_stone_diameter_mm'],
        summary['largest_stone_size_band']
    )
    st.markdown(f'<div class="summary-card">{summary_html}</div>', unsafe_allow_html=True)
    
    # Zero-Stones View vs Results View
    if not summary['has_stones']:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="panel-card"><div class="panel-header">Original CT Scan</div><div class="panel-subtitle">Input abdominal CT scan image.</div></div>', unsafe_allow_html=True)
            st.image(result['original_image'], use_container_width=True)
        with col2:
            st.markdown('<div class="panel-card"><div class="panel-header">AI Detection Output</div><div class="panel-subtitle">Zero stone candidates detected above confidence threshold.</div></div>', unsafe_allow_html=True)
            st.image(result['annotated_detection'], use_container_width=True)
    else:
        # Styled Metric Cards
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Total Stones Detected", f"{summary['stone_count']} Stone(s)")
        with mcol2:
            st.metric("Largest Stone Est. Size", f"{summary['largest_stone_diameter_mm']} mm*")
        with mcol3:
            st.metric("Treatment Category", summary['largest_stone_size_band'])
            
        st.divider()
        
        # Visually Connected 3-Step Diagnostic Grid
        st.markdown("### 🔬 Diagnostic Pipeline Stage Visualizations")
        pcol1, pcol2, pcol3 = st.columns(3)
        
        with pcol1:
            st.markdown("""
            <div class="panel-card">
                <div class="panel-header"><span class="step-circle">1</span> Step 1: Locate Stones <span class="step-arrow">➔</span></div>
                <div class="panel-subtitle">AI scans the CT image to pinpoint candidate stone regions.</div>
            </div>
            """, unsafe_allow_html=True)
            st.image(result['annotated_detection'], caption="YOLOv8 Detection Boxes", use_container_width=True)
            
        with pcol2:
            st.markdown("""
            <div class="panel-card">
                <div class="panel-header"><span class="step-circle">2</span> Step 2: Trace Boundary <span class="step-arrow">➔</span></div>
                <div class="panel-subtitle">Algorithms outline exact stone edges and contours.</div>
            </div>
            """, unsafe_allow_html=True)
            st.image(result['annotated_segmentation'], caption="Classical CV Mask Overlays", use_container_width=True)
            
        with pcol3:
            st.markdown("""
            <div class="panel-card">
                <div class="panel-header"><span class="step-circle">3</span> Step 3: Measure Size</div>
                <div class="panel-subtitle">Calculates physical major & minor dimension axes.</div>
            </div>
            """, unsafe_allow_html=True)
            st.image(result['annotated_measurement'], caption="Measurement Axis Vectors", use_container_width=True)
            
        st.divider()
        
        # Results Data Table with Column Config
        st.markdown("### 📊 Individual Stone Measurement Breakdown")
        
        df_records = []
        for s in stones:
            if s.get('status') == 'Success':
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'AI Confidence': s['confidence'],
                    'Area (px²)': s['area_px'],
                    'Major Axis (px)': s['major_axis_px'],
                    'Minor Axis (px)': s['minor_axis_px'],
                    'Est. Diameter (mm)*': s['estimated_diameter_mm'],
                    'Clinical Treatment Band & Outlook': s['clinical_size_band']
                })
            else:
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'AI Confidence': s['confidence'],
                    'Area (px²)': 0.0,
                    'Major Axis (px)': 0.0,
                    'Minor Axis (px)': 0.0,
                    'Est. Diameter (mm)*': 0.0,
                    'Clinical Treatment Band & Outlook': s['status']
                })
                
        df_display = pd.DataFrame(df_records)
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "AI Confidence": st.column_config.NumberColumn("AI Confidence", format="%.2f"),
                "Area (px²)": st.column_config.NumberColumn("Area (px²)", format="%.1f px²"),
                "Major Axis (px)": st.column_config.NumberColumn("Major Axis (px)", format="%.1f px"),
                "Minor Axis (px)": st.column_config.NumberColumn("Minor Axis (px)", format="%.1f px"),
                "Est. Diameter (mm)*": st.column_config.NumberColumn("Est. Diameter (mm)*", format="%.2f mm"),
                "Clinical Treatment Band & Outlook": st.column_config.TextColumn("Clinical Treatment Band & Outlook")
            }
        )
        st.caption(f"*DISCLAIMER: {NON_CLINICAL_DISCLAIMER}")

    # Close Results Animation Container
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # Methodological Rationale Expander (Technical Details)
    with st.expander("ℹ️ Technical Methodology & Pixel Spacing Rationale"):
        st.markdown(f"""
        - **Pipeline Architecture**: YOLOv8 Object Detector ➔ 10% Padded ROI Crop ➔ Otsu Adaptive Thresholding & Morphological Filter ➔ Contour Axis Geometry Analysis.
        - **Fixed Baseline Factor**: Physical millimeter estimations use a constant factor of **`{ASSUMED_MM_PER_PIXEL} mm/px`**, derived from typical $360\\text{{ mm}}$ abdominal CT Field of View (FOV) over a $512\\text{{ px}}$ image matrix ($360 / 512 = 0.703\\text{{ mm/px}}$).
        - **Non-Clinical Design**: Plain JPG CT images lack DICOM `PixelSpacing` header metadata. Thus, all mm values represent literature-based estimations and are non-clinical.
        """)
