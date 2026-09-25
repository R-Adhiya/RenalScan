"""
landing_page.py - Dedicated Premium RenalScan Landing Page
Official Brand: Medical Red (#B9362F) & Canvas White (#FFFFFF)
"""

import base64
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_sample_b64():
    sample_dir = PROJECT_ROOT / "app" / "sample_scans"
    if not sample_dir.exists() or len(list(sample_dir.glob("*.jpg"))) == 0:
        sample_dir = PROJECT_ROOT / "data" / "test" / "images"
    sample_files = sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []
    if len(sample_files) > 0:
        with open(sample_files[0], "rb") as img_f:
            return base64.b64encode(img_f.read()).decode()
    return ""

def render_landing_page(page_workstation=None):
    """Renders the 12-section enterprise healthcare landing page."""
    
    def go_to_workstation():
        if page_workstation is not None:
            st.switch_page(page_workstation)
        else:
            st.switch_page("workstation")

    sample_b64 = get_sample_b64()

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
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; gap: 26px; padding-top: 6px;">
            <a href="#how-it-works" class="lp-nav-item">How It Works</a>
            <a href="#capabilities" class="lp-nav-item">Capabilities</a>
            <a href="#workstation-preview" class="lp-nav-item">Workstation</a>
            <a href="#kidney-health" class="lp-nav-item">Kidney Health</a>
            <a href="#about" class="lp-nav-item">About</a>
        </div>
        """, unsafe_allow_html=True)
    with nav_c3:
        if st.button("Launch Workstation", key="nav_launch_lp", use_container_width=True):
            go_to_workstation()

    st.write("")

    # -------------------------------------------------------------------------
    # 2. HERO SECTION
    # -------------------------------------------------------------------------
    st.markdown("""<div class="lp-hero-wrapper">""", unsafe_allow_html=True)
    hero_left, hero_right = st.columns([1.2, 1], gap="large")

    with hero_left:
        st.markdown("""
        <div class="lp-badge">AI-Powered CT Diagnostic Research</div>
        <h1 class="lp-hero-heading">
            Intelligent CT Analysis.<br>
            <span>Built for Better Insights.</span>
        </h1>
        <p class="lp-hero-desc">
            RenalScan combines computer vision and clinical image processing to assist in the detection, segmentation, and physical measurement of kidney stones from abdominal CT scans.
        </p>
        """, unsafe_allow_html=True)

        hero_btn1, hero_btn2, hero_btn3 = st.columns([1, 1, 0.2])
        with hero_btn1:
            if st.button("Start Analysis →", key="hero_start_btn", use_container_width=True):
                go_to_workstation()
        with hero_btn2:
            if st.button("Analyze CT Scan", key="hero_analyze_btn", use_container_width=True):
                go_to_workstation()

        st.markdown("""
        <div class="lp-trust-line">
            <span>🛡️</span> Technical Research Demonstration • YOLOv8s &amp; Otsu Segmentation
        </div>
        """, unsafe_allow_html=True)

    with hero_right:
        st.markdown(f"""
        <div class="lp-ct-preview-card">
            <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 0 4px;">
                <span style="color: #9CA3AF; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Abdominal CT Slice</span>
                <span style="color: #10B981; font-size: 0.72rem; font-weight: 700;">● Active Stream</span>
            </div>
            <div style="position: relative; width: 100%; border-radius: 12px; overflow: hidden; background: #000; display: flex; align-items: center; justify-content: center;">
                <img src="data:image/jpeg;base64,{sample_b64}" style="width: 100%; max-height: 280px; object-fit: contain; opacity: 0.92;" />
                <svg viewBox="0 0 400 280" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <rect x="180" y="110" width="65" height="55" fill="rgba(185,54,47,0.22)" stroke="#B9362F" stroke-width="2.5" stroke-dasharray="4 2" rx="4" />
                    <line x1="175" y1="137" x2="250" y2="137" stroke="#D94841" stroke-width="2" stroke-dasharray="3" />
                    <line x1="212" y1="105" x2="212" y2="170" stroke="#D94841" stroke-width="2" stroke-dasharray="3" />
                    <circle cx="212" cy="137" r="4" fill="#B9362F" />
                </svg>
                <div class="lp-floating-card-1">
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 700; text-transform: uppercase;">AI Detection</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #B9362F;">8.19 mm Calculus</div>
                </div>
                <div class="lp-floating-card-2">
                    <div style="font-size: 0.7rem; color: #047857; font-weight: 700; text-transform: uppercase;">Analysis Status</div>
                    <div style="font-size: 0.85rem; font-weight: 800; color: #065F46;">Complete (3/3)</div>
                </div>
                <div class="lp-floating-card-3">
                    <div style="font-size: 0.7rem; color: #8F2924; font-weight: 700; text-transform: uppercase;">AI Confidence</div>
                    <div style="font-size: 0.85rem; font-weight: 800; color: #B9362F;">92.4% Optimal</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. TRUST & VALUE BAR
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-trust-strip">
        <div class="lp-trust-item"><span class="lp-trust-icon">🔬</span> AI-Assisted Analysis</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">⚡</span> CT Image Processing</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">🎯</span> Stone Detection</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">📐</span> Segmentation</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">📊</span> Measurement</div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. WHAT IS RENALSCAN? (SPLIT EDITORIAL SECTION)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-section-header">
        <h2 class="lp-section-title">What is <span>RenalScan</span>?</h2>
        <p class="lp-section-desc">
            A state-of-the-art computer vision pipeline engineered to assist radiologists and urologists in evaluating renal calculi from abdominal computed tomography scans.
        </p>
    </div>
    <div class="lp-split-box">
    """, unsafe_allow_html=True)

    split_col1, split_col2 = st.columns([1, 1.2], gap="large")
    with split_col1:
        st.markdown(f"""
        <div style="background-color: #111827; border-radius: 14px; border: 1px solid #1F2937; border-top: 3px solid #B9362F; padding: 18px; text-align: center;">
            <div style="color: #9CA3AF; font-size: 0.78rem; font-weight: 700; margin-bottom: 12px; display: flex; justify-content: space-between;">
                <span>AI Segmentation Overlay</span>
                <span style="color: #D94841;">● Active ROI</span>
            </div>
            <img src="data:image/jpeg;base64,{sample_b64}" style="width: 100%; max-height: 290px; object-fit: contain; border-radius: 8px; filter: contrast(1.1);" />
            <div style="margin-top: 14px; background: rgba(255,255,255,0.06); border-radius: 8px; padding: 10px; text-align: left; font-size: 0.8rem; color: #D1D5DB;">
                <span style="color: #F87171; font-weight: 700;">Diagnostic Insight:</span> Automated Otsu thresholding separates high-density calcium deposits from soft renal parenchyma.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with split_col2:
        st.markdown("""
        <div class="lp-editorial-step">
            <div class="lp-editorial-num">01</div>
            <div>
                <div class="lp-editorial-title">Automated Detection</div>
                <div class="lp-editorial-desc">
                    Identifies candidate renal stone regions in axial CT slices using a deep convolutional YOLOv8 architecture fine-tuned on non-contrast abdominal scans.
                </div>
            </div>
        </div>
        <div class="lp-editorial-step">
            <div class="lp-editorial-num">02</div>
            <div>
                <div class="lp-editorial-title">Precise Segmentation</div>
                <div class="lp-editorial-desc">
                    Isolates exact calculus boundaries using adaptive Otsu thresholding and morphological filtering, preserving delicate geometric margins.
                </div>
            </div>
        </div>
        <div class="lp-editorial-step">
            <div class="lp-editorial-num">03</div>
            <div>
                <div class="lp-editorial-title">Geometric Measurement</div>
                <div class="lp-editorial-desc">
                    Extracts major axis, minor axis, surface area, and estimated physical diameter (mm) to support clinical decision-making and triage stratification.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. HOW IT WORKS (6-STEP WORKFLOW TIMELINE)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="how-it-works" class="lp-section-header">
        <h2 class="lp-section-title">How It <span>Works</span></h2>
        <p class="lp-section-desc">
            Six disciplined stages translate raw DICOM or CT scan slices into verified clinical insights in seconds.
        </p>
    </div>
    <div class="lp-timeline-wrapper">
        <div class="lp-timeline-steps">
            <div class="lp-timeline-line"></div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">01</div>
                <div class="lp-step-title">UPLOAD</div>
                <div class="lp-step-desc">Accepts abdominal CT scans in standard image or DICOM formats.</div>
            </div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">02</div>
                <div class="lp-step-title">PREPROCESS</div>
                <div class="lp-step-desc">Normalizes dimensions, contrasts, and windowing values.</div>
            </div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">03</div>
                <div class="lp-step-title">DETECT</div>
                <div class="lp-step-desc">YOLOv8 scans for hyperdense calculi and returns bounding boxes.</div>
            </div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">04</div>
                <div class="lp-step-title">SEGMENT</div>
                <div class="lp-step-desc">Otsu thresholding defines the precise stone perimeter.</div>
            </div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">05</div>
                <div class="lp-step-title">MEASURE</div>
                <div class="lp-step-desc">Calipers calculate major/minor axes and estimated diameter.</div>
            </div>
            <div class="lp-timeline-step">
                <div class="lp-step-circle">06</div>
                <div class="lp-step-title">ANALYZE</div>
                <div class="lp-step-desc">Generates triage category, risk metrics, and reports.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 6. WORKSTATION PREVIEW (INSIDE THE RENALSCAN ANALYSIS WORKSTATION)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="workstation-preview" class="lp-section-header">
        <h2 class="lp-section-title">Inside the <span>Analysis Workstation</span></h2>
        <p class="lp-section-desc">
            An intuitive diagnostic workspace built for high-throughput review and precision adjustment.
        </p>
    </div>
    <div class="lp-preview-box">
    """, unsafe_allow_html=True)

    ws_prev_left, ws_prev_right = st.columns([1.1, 1], gap="large")
    with ws_prev_left:
        st.markdown(f"""
        <div style="background-color: #111827; border-radius: 14px; border: 1px solid #1F2937; border-top: 3px solid #B9362F; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; color: #FFFFFF;">
                <div style="font-weight: 800; font-size: 0.92rem;">WORKSTATION PREVIEW</div>
                <span style="font-size: 0.75rem; background: #FCEDEC; color: #B9362F; font-weight: 700; padding: 3px 8px; border-radius: 10px;">Slice 034 / 128</span>
            </div>
            <img src="data:image/jpeg;base64,{sample_b64}" style="width: 100%; max-height: 240px; object-fit: contain; border-radius: 8px; margin-bottom: 14px;" />
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center;">
                <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #9CA3AF; font-size: 0.68rem; font-weight: 700;">STONES</div>
                    <div style="color: #FFFFFF; font-size: 1.1rem; font-weight: 800;">3</div>
                </div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #9CA3AF; font-size: 0.68rem; font-weight: 700;">LARGEST</div>
                    <div style="color: #D94841; font-size: 1.1rem; font-weight: 800;">8.2 mm</div>
                </div>
                <div style="background: rgba(255,255,255,0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #9CA3AF; font-size: 0.68rem; font-weight: 700;">CONFIDENCE</div>
                    <div style="color: #10B981; font-size: 1.1rem; font-weight: 800;">86.8%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ws_prev_right:
        st.markdown("""
        <div style="padding-top: 6px;">
            <div style="font-size: 1.35rem; font-weight: 800; color: #20283A; margin-bottom: 10px;">
                Full-Featured Diagnostic Workstation
            </div>
            <div style="font-size: 0.95rem; color: #4B5563; line-height: 1.6; margin-bottom: 20px;">
                The RenalScan Workstation provides complete control over image enhancement, detection confidence thresholds, and segmentation masks. Examine detected calculus geometry with calibrated millimeter measurements.
            </div>
            <ul style="list-style: none; padding: 0; margin-bottom: 24px;">
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #20283A; font-size: 0.9rem;">
                    <span style="color: #B9362F;">✓</span> Interactive multi-layer visualization overlays
                </li>
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #20283A; font-size: 0.9rem;">
                    <span style="color: #B9362F;">✓</span> Real-time brightness &amp; contrast adjustments
                </li>
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #20283A; font-size: 0.9rem;">
                    <span style="color: #B9362F;">✓</span> Anatomical left/right kidney spatial distribution mapping
                </li>
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #20283A; font-size: 0.9rem;">
                    <span style="color: #B9362F;">✓</span> One-click clinical report and CSV dataset export
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Launch Workstation →", key="ws_preview_launch", use_container_width=True):
            go_to_workstation()

    st.markdown("""</div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 7. CAPABILITIES GRID (2x3 GRID)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="capabilities" class="lp-section-header">
        <h2 class="lp-section-title">Core <span>Capabilities</span></h2>
        <p class="lp-section-desc">
            Engineered with medical image processing standards to ensure high reliability across clinical workflows.
        </p>
    </div>
    <div class="lp-cap-grid">
        <div class="lp-cap-card">
            <div class="lp-cap-icon">🎯</div>
            <div class="lp-cap-title">Stone Detection</div>
            <div class="lp-cap-desc">
                High-sensitivity YOLOv8 model localized candidate calculi across complex soft tissue and bone attenuations.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">✂️</div>
            <div class="lp-cap-title">Contour Segmentation</div>
            <div class="lp-cap-desc">
                Sub-pixel Otsu segmentation isolates true stone perimeters, preventing overestimation from beam hardening.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📐</div>
            <div class="lp-cap-title">Physical Sizing</div>
            <div class="lp-cap-desc">
                Calibrated millimeters conversion computes major axis, minor axis, and equivalent spherical diameter.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📈</div>
            <div class="lp-cap-title">Confidence Calibration</div>
            <div class="lp-cap-desc">
                Probabilistic confidence scoring indicates certainty, alerting clinicians to borderline or faint calcifications.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">🖼️</div>
            <div class="lp-cap-title">Multi-Layer Visuals</div>
            <div class="lp-cap-desc">
                Switch seamlessly between raw CT, detection bounding boxes, binary masks, and measurement vector overlays.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📄</div>
            <div class="lp-cap-title">Structured Export</div>
            <div class="lp-cap-desc">
                Generate instant clinical summary text reports and export tabular CSV measurement sheets for audits.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 8. ANALYSIS REPORT SHOWCASE
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-section-header">
        <h2 class="lp-section-title">Standardized <span>Analysis Reports</span></h2>
        <p class="lp-section-desc">
            Automated findings structured according to clinical urology triage criteria.
        </p>
    </div>
    <div style="max-width: 820px; margin: 0 auto 48px auto;">
        <div class="lp-report-card">
            <div class="lp-report-header">
                <div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #20283A;">RENALSCAN AI ANALYSIS REPORT</div>
                    <div style="font-size: 0.78rem; color: #6B7280;">AUTOMATED NEPHROLITHIASIS QUANTIFICATION</div>
                </div>
                <div style="background-color: #FCEDEC; color: #B9362F; font-size: 0.75rem; font-weight: 800; padding: 4px 10px; border-radius: 6px;">
                    CONFIDENTIAL / MEDICAL RESEARCH
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; background-color: #FFF7F7; border: 1px solid #F1D5D5; border-radius: 10px; padding: 12px 14px;">
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600;">SCAN ID</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #20283A;">RS-2026-0819</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600;">CALCULI DETECTED</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #B9362F;">1 Calculus</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600;">LARGEST DIAMETER</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #B9362F;">8.19 mm</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 600;">TRIAGE BAND</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #D94841;">6-10mm (Large)</div>
                </div>
            </div>
            <div style="font-size: 0.84rem; color: #4B5563; line-height: 1.6; margin-bottom: 14px;">
                <strong>Clinical Stratification:</strong> Single hyperattenuating calcification observed in renal parenchyma ROI. Low likelihood of spontaneous passage (~20%). Elective urological consultation (ESWL / URS) indicated.
            </div>
            <div style="border-top: 1px dashed #F1D5D5; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #9CA3AF;">
                <span>Verified by RenalScan AI Pipeline v2.0</span>
                <span>Assumed Spacing: 0.70 mm/px</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 9. KIDNEY HEALTH SECTION (4 LARGE CARDS)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="kidney-health" class="lp-section-header">
        <h2 class="lp-section-title">Understanding <span>Kidney Health</span></h2>
        <p class="lp-section-desc">
            Learn more about kidney stones, symptoms, risk factors, diagnosis, prevention, and treatment.
        </p>
    </div>
    <div class="lp-health-grid">
        <div class="lp-health-card">
            <div class="lp-cap-icon">🫘</div>
            <div class="lp-cap-title">KIDNEY STONES</div>
            <div class="lp-cap-desc">
                Mineral crystallizations (calcium oxalate, phosphate, or uric acid) that precipitate inside renal calyces.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-cap-icon">⚡</div>
            <div class="lp-cap-title">SYMPTOMS</div>
            <div class="lp-cap-desc">
                Common symptoms: acute radiating flank pain, visible hematuria (blood in urine), dysuria, and nausea.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-cap-icon">⚠️</div>
            <div class="lp-cap-title">RISK FACTORS</div>
            <div class="lp-cap-desc">
                Chronic dehydration, high dietary sodium, excessive animal protein, familial history, and metabolic factors.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-cap-icon">💧</div>
            <div class="lp-cap-title">PREVENTION</div>
            <div class="lp-cap-desc">
                Consuming sufficient fluids to achieve &gt;2.5L daily urine volume and maintaining dietary calcium balance.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 10. RESPONSIBLE AI (LIGHT RED SECTION)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div id="about" class="lp-safety-banner">
        <div class="lp-safety-icon">🛡️</div>
        <div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #20283A; margin-bottom: 4px;">
                AI-Assisted. Human-Centered.
            </div>
            <div style="font-size: 0.9rem; color: #4B5563; line-height: 1.6;">
                RenalScan is designed to assist with medical image analysis. AI-generated findings provide supportive information and should be reviewed by qualified healthcare professionals. This portfolio prototype is intended for technical evaluation and educational demonstration, not as a standalone medical diagnostic or surgical decision-making tool.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 11. FINAL CTA (DEEP RED / DARK RED CONTAINER)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-final-cta-wrapper">
        <h2 class="lp-final-cta-title">Ready to Explore RenalScan?</h2>
        <p class="lp-final-cta-sub">
            Upload a CT scan and experience AI-assisted kidney stone analysis.
        </p>
    """, unsafe_allow_html=True)

    cta_btn_col1, cta_btn_col2, cta_btn_col3 = st.columns([1, 1.2, 1])
    with cta_btn_col2:
        if st.button("Start Analysis →", key="final_deep_start", use_container_width=True):
            go_to_workstation()

    st.markdown("""
        <div style="margin-top: 14px;">
            <a href="#how-it-works" style="color: #FEE2E2; font-size: 0.85rem; text-decoration: underline; font-weight: 600;">
                How It Works
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 12. FOOTER (DARK CHARCOAL WITH RED TOP BORDER)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="lp-footer">
        <div class="lp-footer-grid">
            <div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">
                    Renal<span style="color: #D94841;">Scan</span>
                </div>
                <div style="font-size: 0.82rem; color: #9CA3AF; margin-bottom: 12px;">
                    AI Kidney Stone Analysis
                </div>
                <div style="font-size: 0.82rem; color: #6B7280; line-height: 1.6; max-width: 320px;">
                    AI-assisted kidney stone analysis from CT images. Built for technical portfolio demonstration and medical computer vision research.
                </div>
            </div>
            <div class="lp-footer-col">
                <h4>Product</h4>
                <ul>
                    <li>Workstation</li>
                    <li>How It Works</li>
                    <li>Capabilities</li>
                </ul>
            </div>
            <div class="lp-footer-col">
                <h4>Resources</h4>
                <ul>
                    <li>Kidney Health</li>
                    <li>About</li>
                    <li>Medical Disclaimer</li>
                </ul>
            </div>
        </div>
        <div class="lp-footer-bottom">
            © 2026 RenalScan. AI-assisted analysis. Not a substitute for professional medical advice.
        </div>
    </div>
    """, unsafe_allow_html=True)
