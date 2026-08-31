import sys
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

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
        margin-bottom: 1.5rem;
    }
    .disclaimer-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 25px;
        font-size: 0.9rem;
        color: #991B1B;
    }
</style>
""", unsafe_allow_html=True)

# Main Title & Header
st.markdown('<div class="main-title">🩺 RenalScan — AI Kidney Stone Detection & Physical Measurement</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">End-to-End Pipeline: YOLOv8 Bounding Box Detection ➔ Classical CV Otsu Segmentation ➔ Quantitative Dimension Analysis</div>', unsafe_allow_html=True)

# Non-Clinical Disclaimer Banner
st.markdown(f"""
<div class="disclaimer-box">
    <strong>⚠️ NON-CLINICAL PORTFOLIO DISCLAIMER:</strong> All millimeter-based measurements and urological size classifications are estimated using a literature-based baseline constant ({ASSUMED_MM_PER_PIXEL} mm/px FOV). This application is designed strictly for portfolio evaluation and technical demonstration. It must <strong>NOT</strong> be used for clinical diagnosis or surgical decision-making.
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ Pipeline Settings")

# Model Loading Helper
@st.cache_resource
def load_pipeline(mm_per_pixel=ASSUMED_MM_PER_PIXEL):
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=mm_per_pixel)

conf_thresh = st.sidebar.slider(
    "YOLO Confidence Threshold",
    min_value=0.10,
    max_value=0.90,
    value=0.40,
    step=0.05,
    help="Detections below this confidence score are filtered out before segmentation."
)

mm_factor = st.sidebar.slider(
    "Assumed Pixel Spacing (mm/px)",
    min_value=0.50,
    max_value=1.00,
    value=ASSUMED_MM_PER_PIXEL,
    step=0.01,
    help="Literature-based pixel spacing conversion constant for plain CT images."
)

pipeline = load_pipeline(mm_per_pixel=mm_factor)

st.sidebar.markdown("---")
st.sidebar.subheader("📷 Input CT Scan Selection")

# Sample CT Scans Dropdown Option
sample_dir = PROJECT_ROOT / "data" / "test" / "images"
sample_files = sorted(list(sample_dir.glob("*.jpg")))[:10] if sample_dir.exists() else []

sample_options = ["None (Upload Own File)"] + [f.name for f in sample_files]
selected_sample = st.sidebar.selectbox("Choose Sample Test Image", sample_options)

uploaded_file = st.sidebar.file_uploader("Or Upload Custom CT Scan (JPG/PNG)", type=["jpg", "jpeg", "png"])

input_img_array = None

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=uint8) if 'uint8' in globals() else np.frombuffer(uploaded_file.read(), np.uint8)
    bgr_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if bgr_img is not None:
        input_img_array = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
elif selected_sample != "None (Upload Own File)":
    sample_path = sample_dir / selected_sample
    bgr_img = cv2.imread(str(sample_path))
    if bgr_img is not None:
        input_img_array = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)

# Main Application Flow
if input_img_array is None:
    st.info("👈 Please select a sample CT image from the sidebar or upload your own file to run the diagnostic pipeline.")
    
    st.markdown("### 📋 Pipeline Architecture Overview")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 1. YOLOv8 Detection")
        st.write("Identifies candidate kidney stone regions of interest using trained deep learning bounding box detectors.")
    with col_b:
        st.markdown("#### 2. Classical CV Segmentation")
        st.write("Crops 10% padded ROIs, applies Otsu adaptive thresholding & morphological filtering to extract precise stone masks.")
    with col_c:
        st.markdown("#### 3. Physical Measurement")
        st.write("Extracts major/minor axes, mask area, equivalent diameter, and maps to clinical urological treatment bands.")
else:
    # Run End-to-End Pipeline
    with st.spinner("Processing CT scan through RenalScan pipeline..."):
        result = pipeline.analyze(input_img_array, conf_thresh=conf_thresh)
        
    summary = result['summary']
    stones = result['stones']
    
    st.markdown("---")
    
    # 0-Stones Edge Case View
    if not summary['has_stones']:
        st.info("ℹ️ **No Kidney Stones Detected**: No high-confidence stone candidates were detected in this CT scan.")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original CT Scan")
            st.image(result['original_image'], use_container_width=True)
        with col2:
            st.subheader("YOLOv8 Detection Output")
            st.image(result['annotated_detection'], use_container_width=True)
    else:
        # Top Metric Cards Summary
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Total Stones Detected", f"{summary['stone_count']}")
        with mcol2:
            st.metric("Largest Stone Est. Diameter", f"{summary['largest_stone_diameter_mm']} mm*")
        with mcol3:
            st.metric("Largest Stone Treatment Band", summary['largest_stone_size_band'])
            
        st.markdown("### 🔬 Visual Diagnostic Pipeline Stages")
        
        # Side-by-Side Visual Tabs
        tab1, tab2, tab3 = st.tabs([
            "🎯 1. YOLOv8 Bounding Box Detections",
            "🔬 2. Classical CV Stone Mask Overlays",
            "📐 3. Physical Measurement Vectors"
        ])
        
        with tab1:
            st.image(result['annotated_detection'], caption="YOLOv8 Bounding Box Detections", use_container_width=True)
        with tab2:
            st.image(result['annotated_segmentation'], caption="Classical CV Otsu Mask Overlay (Cyan Boundary / Red Fill)", use_container_width=True)
        with tab3:
            st.image(result['annotated_measurement'], caption="Measurement Axis Vectors (Cyan=Major Axis, Yellow=Minor Axis, Red=Centroid)", use_container_width=True)
            
        st.markdown("---")
        st.markdown("### 📊 Per-Stone Quantitative Measurement Log")
        
        df_records = []
        for s in stones:
            if s.get('status') == 'Success':
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'Confidence': f"{s['confidence']:.2f}",
                    'Box Coordinates': str(s['box_xyxy']),
                    'Mask Area (px²)': f"{s['area_px']:.1f}",
                    'Major Axis (px)': f"{s['major_axis_px']:.1f}",
                    'Minor Axis (px)': f"{s['minor_axis_px']:.1f}",
                    'Est. Diameter (mm)*': f"{s['estimated_diameter_mm']:.2f}",
                    'Clinical Treatment Band': s['clinical_size_band']
                })
            else:
                df_records.append({
                    'Stone ID': f"Stone #{s['stone_id']}",
                    'Confidence': f"{s['confidence']:.2f}",
                    'Box Coordinates': str(s['box_xyxy']),
                    'Mask Area (px²)': "N/A",
                    'Major Axis (px)': "N/A",
                    'Minor Axis (px)': "N/A",
                    'Est. Diameter (mm)*': "N/A",
                    'Clinical Treatment Band': s['status']
                })
                
        df_display = pd.DataFrame(df_records)
        st.dataframe(df_display, use_container_width=True)
        st.caption(f"*DISCLAIMER: {NON_CLINICAL_DISCLAIMER}")
