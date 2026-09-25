"""
workstation_page.py - Existing CT Analysis Workstation (100% Preserved)
Intelligent CT Analysis, Detection, Segmentation, Measurement & Reports.
"""

from pathlib import Path
import base64
import cv2
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from src.pipeline.pipeline import RenalScanPipeline
from src.measurement.measure import ASSUMED_MM_PER_PIXEL, NON_CLINICAL_DISCLAIMER

@st.cache_resource
def get_pipeline():
    model_path = PROJECT_ROOT / "models" / "detection_best.pt"
    return RenalScanPipeline(model_path=model_path, mm_per_pixel=ASSUMED_MM_PER_PIXEL)

def get_sample_files():
    sample_dir = PROJECT_ROOT / "app" / "sample_scans"
    if not sample_dir.exists() or len(list(sample_dir.glob("*.jpg"))) == 0:
        sample_dir = PROJECT_ROOT / "data" / "test" / "images"
    return sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []

def render_workstation_page(page_landing=None):
    """Renders the full CT Analysis Workstation with complete state preservation."""
    
    pipeline = get_pipeline()
    sample_files = get_sample_files()

    def go_to_home():
        if page_landing is not None:
            st.switch_page(page_landing)
        else:
            st.switch_page("")

    # Session State for Images
    if 'active_image' not in st.session_state:
        st.session_state['active_image'] = None
    if 'active_sample_name' not in st.session_state:
        st.session_state['active_sample_name'] = None

    # Default to first sample if active_image is None
    if st.session_state['active_image'] is None and len(sample_files) > 0:
        bgr = cv2.imread(str(sample_files[0]))
        st.session_state['active_image'] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        st.session_state['active_sample_name'] = sample_files[0].name

    # Encode sample CT image to base64 for interactive tab animation
    sample_b64 = ""
    if len(sample_files) > 0:
        with open(sample_files[0], "rb") as img_f:
            sample_b64 = base64.b64encode(img_f.read()).decode()

    # -------------------------------------------------------------------------
    # WORKSTATION TOP BAR
    # -------------------------------------------------------------------------
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
            <span style="font-size: 0.92rem; font-weight: 700; color: #B9362F; background: #FCEDEC; padding: 4px 14px; border-radius: 12px; border: 1px solid #F1D5D5;">
                ● Live Diagnostic Mode
            </span>
        </div>
        """, unsafe_allow_html=True)
    with ws_nav3:
        if st.button("← Back to Home", key="ws_back_home_btn", use_container_width=True):
            go_to_home()

    st.write("")

    # -------------------------------------------------------------------------
    # WORKSTATION TABS
    # -------------------------------------------------------------------------
    ws_tab1, ws_tab2, ws_tab3, ws_tab4 = st.tabs([
        "🩺 CT Analysis Workspace",
        "🔬 How It Works (Animation)",
        "🫘 Kidney Health Guide",
        "ℹ️ Technical Limitations & Evaluation"
    ])

    # -------------------------------------------------------------------------
    # SUB-TAB 1: CT ANALYSIS WORKSPACE
    # -------------------------------------------------------------------------
    with ws_tab1:
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

            # Benchmark Sample Scans
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

            # Scan Metadata Card
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

            # Analysis Controls Card
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
            processed_img = st.session_state['active_image'].copy() if st.session_state['active_image'] is not None else np.zeros((512,512,3), dtype=np.uint8)
            if brightness != 0 or contrast != 0:
                processed_img = cv2.convertScaleAbs(processed_img, alpha=1.0 + (contrast/100.0), beta=brightness)

            # Pipeline Execution
            try:
                with st.spinner("Executing AI pipeline — detection, segmentation, and stone measurement..."):
                    result = pipeline.analyze(processed_img, conf_thresh=conf_thresh)
            except Exception as exc:
                st.error(f"⚠️ Analysis error occurred ({type(exc).__name__}: {str(exc)}). Please select a sample scan or re-upload.")
                st.stop()

            summary = result['summary']
            stones = result['stones']

            # CT Scan Viewer
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

            # Before / After Comparison
            with st.expander("🔍 Before / After Segmentation Comparison"):
                c_comp1, c_comp2 = st.columns(2)
                with c_comp1:
                    st.caption("Original Non-Contrast CT Scan")
                    st.image(result['original_image'], use_container_width=True)
                with c_comp2:
                    st.caption("AI Segmentation Overlay (Otsu Classical CV)")
                    st.image(result['annotated_segmentation'], use_container_width=True)

            st.write("")

            # AI Analysis Results Header
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; margin-top: 10px;">
                <div style="font-size: 1.35rem; font-weight: 800; color: #20283A;">
                    AI Analysis Results <span style="color: #B9362F;">●</span>
                </div>
                <div style="color: #10B981; font-weight: 700; font-size: 0.88rem; display: flex; align-items: center; gap: 6px;">
                    ● Analysis Complete
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not summary['has_stones']:
                st.markdown("""
                <div class="rs-summary-card">
                    <div style="color: #B9362F; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 4px;">
                        AI ANALYSIS SUMMARY
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #20283A;">
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

                # Summary Card
                st.markdown(f"""
                <div class="rs-summary-card">
                    <div style="color: #B9362F; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 4px;">
                        AI ANALYSIS SUMMARY
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #20283A;">
                        <span style="color: #B9362F; font-weight: 800;">{stone_count} stone(s) detected</span> • 
                        <span style="color: #B9362F; font-weight: 800;">{largest_mm:.2f} mm</span> largest stone diameter
                    </div>
                    <div style="font-size: 0.86rem; color: #4B5563; margin-top: 6px;">
                        {clinical_note}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Three Metric Cards
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

                # Detected Stone Regions Cards
                st.markdown("""
                <div style="font-size: 1.05rem; font-weight: 800; color: #20283A; margin-bottom: 10px;">
                    Detected Stone Regions <span style="color: #B9362F;">({count})</span>
                </div>
                """.format(count=stone_count), unsafe_allow_html=True)

                for s in stones:
                    if s.get('status') == 'Success':
                        st.markdown(f"""
                        <div class="rs-stone-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-weight: 800; font-size: 0.95rem; color: #B9362F;">Stone #{s['stone_id']}</span>
                                <span style="background-color: #FCEDEC; color: #B9362F; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 12px;">
                                    {s['confidence']*100:.1f}% Confidence
                                </span>
                            </div>
                            <div style="font-size: 0.83rem; color: #4B5563; line-height: 1.55;">
                                • <strong>Estimated Diameter:</strong> <span style="color: #B9362F; font-weight: 700;">{s['estimated_diameter_mm']:.2f} mm</span> ({s['equiv_diameter_px']:.1f} px)<br>
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
                <div style="font-weight: 800; font-size: 1rem; color: #20283A;">🫘 Anatomical Kidney Map</div>
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
                    <div style="font-weight: 800; font-size: 1rem; color: #20283A; margin-bottom: 8px;">
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

    # -------------------------------------------------------------------------
    # SUB-TAB 2: HOW IT WORKS ANIMATION
    # -------------------------------------------------------------------------
    with ws_tab2:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #20283A;">Interactive Pipeline Simulation</h3>
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
                body {{ font-family: 'Inter', sans-serif; background-color: #FFFFFF; margin: 0; padding: 10px; color: #20283A; }}
                .card-container {{ background-color: #FFFFFF; border: 1px solid #F1D5D5; border-radius: 18px; padding: 24px; box-shadow: 0 4px 20px rgba(185, 54, 47, 0.05); }}
                .ct-canvas {{ background-color: #111827; border-radius: 14px; border-top: 3px solid #B9362F; position: relative; width: 100%; height: 420px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
                .ct-img {{ max-height: 400px; max-width: 400px; border-radius: 6px; }}
                .scan-line {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #D94841, transparent); box-shadow: 0 0 12px #D94841; animation: scanMove 3s infinite linear; opacity: 0.85; }}
                @keyframes scanMove {{ 0% {{ top: 5%; }} 50% {{ top: 90%; }} 100% {{ top: 5%; }} }}
                .svg-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
                .yolo-box {{ stroke: #D94841; stroke-width: 2.5; stroke-dasharray: 6 4; fill: rgba(217, 72, 65, 0.15); transition: all 0.5s; }}
                .otsu-contour {{ stroke: #B9362F; stroke-width: 3; fill: rgba(185, 54, 47, 0.28); stroke-dasharray: 400; stroke-dashoffset: 400; transition: stroke-dashoffset 1.5s ease-in-out; }}
                .draw-contour {{ stroke-dashoffset: 0 !important; }}
                .meas-vector {{ stroke: #B9362F; stroke-width: 2.5; stroke-dasharray: 4; }}
                .badge-floating {{ position: absolute; background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(4px); border: 1px solid #B9362F; color: #FFFFFF; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 700; }}
                .ctrl-bar {{ display: flex; gap: 10px; justify-content: center; margin-top: 20px; }}
                .step-btn {{ background-color: #FFFFFF; border: 1px solid #F1D5D5; color: #20283A; font-weight: 700; font-size: 0.85rem; padding: 9px 16px; border-radius: 8px; cursor: pointer; }}
                .step-btn:hover, .step-btn.active {{ background-color: #B9362F; border-color: #B9362F; color: #FFFFFF; }}
                .timeline-bar {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 18px; text-align: center; }}
                .t-stage {{ background-color: #FCEDEC; border: 1px solid #F1D5D5; border-radius: 8px; padding: 10px; font-size: 0.78rem; font-weight: 700; color: #6B7280; }}
                .t-stage.active-stage {{ background-color: #B9362F; border-color: #B9362F; color: #FFFFFF; }}
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
                    <div id="confBadge" class="badge-floating" style="top: 20px; right: 20px; opacity: 0; background: #B9362F;">CONFIDENCE: 86.8%</div>
                    <div id="readoutBadge" class="badge-floating" style="bottom: 20px; right: 20px; opacity: 0; background: #B9362F;">DIMENSIONS: 8.2mm × 5.4mm</div>
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

    # -------------------------------------------------------------------------
    # SUB-TAB 3: KIDNEY HEALTH
    # -------------------------------------------------------------------------
    with ws_tab3:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #20283A;">Nephrolithiasis Clinical Reference</h3>
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

    # -------------------------------------------------------------------------
    # SUB-TAB 4: LIMITATIONS
    # -------------------------------------------------------------------------
    with ws_tab4:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="font-weight: 800; color: #20283A;">Known Limitations & Technical Evaluation</h3>
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
