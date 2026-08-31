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

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .disclaimer-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 0.92rem;
        color: #991B1B;
        line-height: 1.4;
    }
    .summary-banner {
        background-color: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 15px 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #0369A1;
        line-height: 1.5;
    }
    .step-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 4px;
    }
    .step-caption {
        font-size: 0.88rem;
        color: #4B5563;
        margin-bottom: 12px;
        min-height: 38px;
    }
    .metric-card {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main Title & Header (Rendered on EVERY view)
st.markdown('<div class="main-title">🩺 RenalScan — AI Kidney Stone Diagnostic System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Automated 3-Step Analysis of Abdominal CT Scans: Find Stones ➔ Outline Boundaries ➔ Measure Physical Dimensions</div>', unsafe_allow_html=True)

# Non-Clinical Disclaimer Banner (Rendered Unconditionally on EVERY View)
st.markdown(f"""
<div class="disclaimer-box">
    <strong>⚠️ NON-CLINICAL PORTFOLIO DISCLAIMER:</strong> All millimeter measurements and clinical size classifications are estimates based on a literature-derived constant (fixed at <strong>{ASSUMED_MM_PER_PIXEL} mm/px</strong> FOV). This application is built for technical portfolio evaluation and must <strong>NOT</strong> be used for actual medical diagnosis or surgical treatment decisions.
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar Configuration
st.sidebar.title("⚙️ Diagnostic Controls")

# Fixed Pipeline Loader
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
    help="Controls how strictly the AI filters candidate stone detections."
)

pipeline = load_pipeline()

st.sidebar.markdown("---")
st.sidebar.subheader("📷 Input CT Scan Selection")

# Sample CT Scans Dropdown Option
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

# Helper function to generate plain-English guidance sentence
def get_plain_english_summary(stone_count, largest_mm, largest_band):
    if stone_count == 0:
        return "ℹ️ **Analysis Summary:** No kidney stones were detected in this CT scan."
    
    if "<4mm" in largest_band:
        guidance = "typically passes on its own with plenty of fluid intake."
    elif "4-6mm" in largest_band:
        guidance = "may need medical observation or medication to help it pass."
    elif "6-10mm" in largest_band:
        guidance = "usually requires a procedure or specialized urological treatment."
    else: # >10mm
        guidance = "usually requires surgical intervention to break up or remove."
        
    return f"💡 **Analysis Summary:** This scan shows **{stone_count} kidney stone(s)**. The largest is estimated at **{largest_mm} mm**, which {guidance}"

# Main Application Flow
if input_img_array is None:
    st.info("👈 Please select a sample CT scan from the sidebar menu or upload your own image file to run the diagnostic pipeline.")
    
    st.markdown("### 📋 How the 3-Step AI Analysis Works")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 1️⃣ Step 1: Locate Stones")
        st.write("Scans the CT image to pinpoint candidate kidney stone regions of interest.")
    with col_b:
        st.markdown("#### 2️⃣ Step 2: Trace Boundaries")
        st.write("Outlines the exact physical shape and edge contour of every detected stone.")
    with col_c:
        st.markdown("#### 3️⃣ Step 3: Measure Dimensions")
        st.write("Calculates length, width, and estimated millimeter size to determine treatment guidance.")
else:
    # Run End-to-End Pipeline
    with st.spinner("Analyzing CT scan through 3-step diagnostic pipeline..."):
        result = pipeline.analyze(input_img_array, conf_thresh=conf_thresh)
        
    summary = result['summary']
    stones = result['stones']
    
    # 1. Plain-English Summary Sentence at the Very Top
    summary_sentence = get_plain_english_summary(
        summary['stone_count'],
        summary['largest_stone_diameter_mm'],
        summary['largest_stone_size_band']
    )
    st.markdown(f'<div class="summary-banner">{summary_sentence}</div>', unsafe_allow_html=True)
    
    # 0-Stones View
    if not summary['has_stones']:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original CT Scan")
            st.image(result['original_image'], use_container_width=True)
        with col2:
            st.subheader("AI Detection Output")
            st.image(result['annotated_detection'], use_container_width=True)
    else:
        # 2. Styled Top Metric Cards
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Total Stones Detected", f"{summary['stone_count']} Stone(s)")
        with mcol2:
            st.metric("Largest Stone Est. Size", f"{summary['largest_stone_diameter_mm']} mm*")
        with mcol3:
            st.metric("Treatment Category", summary['largest_stone_size_band'])
            
        st.divider()
        
        # 3. Visually Connected 3-Step Diagnostic Panel Sequence (Side-by-Side Columns)
        st.markdown("### 🔬 Diagnostic Pipeline Stage Visualizations")
        pcol1, pcol2, pcol3 = st.columns(3)
        
        with pcol1:
            st.markdown('<div class="step-header">1️⃣ Step 1: Locate Stones ➔</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-caption">Pinpoints stone locations on the CT image.</div>', unsafe_allow_html=True)
            st.image(result['annotated_detection'], caption="YOLOv8 Detection Boxes", use_container_width=True)
            
        with pcol2:
            st.markdown('<div class="step-header">2️⃣ Step 2: Trace Boundary ➔</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-caption">Outlines exact stone edges and shapes.</div>', unsafe_allow_html=True)
            st.image(result['annotated_segmentation'], caption="Classical CV Mask Overlays", use_container_width=True)
            
        with pcol3:
            st.markdown('<div class="step-header">3️⃣ Step 3: Measure Size</div>', unsafe_allow_html=True)
            st.markdown('<div class="step-caption">Measures physical length & width vectors.</div>', unsafe_allow_html=True)
            st.image(result['annotated_measurement'], caption="Measurement Axis Vectors", use_container_width=True)
            
        st.divider()
        
        # 4. Detailed Per-Stone Quantitative Measurement Log
        st.markdown("### 📊 Individual Stone Measurement Breakdown")
        
        df_records = []
        for s in stones:
            if s.get('status') == 'Success':
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'AI Confidence': f"{s['confidence']*100:.1f}%",
                    'Area (px²)': f"{s['area_px']:.1f}",
                    'Major Axis (px)': f"{s['major_axis_px']:.1f}",
                    'Minor Axis (px)': f"{s['minor_axis_px']:.1f}",
                    'Est. Diameter (mm)*': f"{s['estimated_diameter_mm']:.2f} mm",
                    'Clinical Treatment Band & Outlook': s['clinical_size_band']
                })
            else:
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'AI Confidence': f"{s['confidence']*100:.1f}%",
                    'Area (px²)': "N/A",
                    'Major Axis (px)': "N/A",
                    'Minor Axis (px)': "N/A",
                    'Est. Diameter (mm)*': "N/A",
                    'Clinical Treatment Band & Outlook': s['status']
                })
                
        df_display = pd.DataFrame(df_records)
        st.dataframe(df_display, use_container_width=True)
        st.caption(f"*DISCLAIMER: {NON_CLINICAL_DISCLAIMER}")

    st.divider()

    # Methodological Rationale Expander (Technical Details for Technical Reviewers)
    with st.expander("ℹ️ Technical Methodology & Pixel Spacing Rationale"):
        st.markdown(f"""
        - **Pipeline Architecture**: YOLOv8 Deep Learning Object Detector ➔ 10% Padded ROI Crop ➔ Otsu Adaptive Thresholding & Morphological Filter ➔ Contour Axis Geometry Analysis.
        - **Fixed Baseline Factor**: Physical millimeter estimations use a constant factor of **`{ASSUMED_MM_PER_PIXEL} mm/px`**, derived from typical $360\\text{{ mm}}$ abdominal CT Field of View (FOV) over a $512\\text{{ px}}$ image matrix ($360 / 512 = 0.703\\text{{ mm/px}}$).
        - **Non-Clinical Design**: Plain JPG CT images lack DICOM `PixelSpacing` header metadata. Thus, all mm values represent literature-based estimations and are non-clinical.
        """)
