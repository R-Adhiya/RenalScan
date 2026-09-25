"""
landing_page.py - Premium, Highly Animated RenalScan Landing Page
Enterprise Healthcare AI Startup Visual Standard
Brand: Medical Red (#B9362F) & Canvas White (#FFFFFF)
"""

import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_sample_images():
    """Loads benchmark sample scans as base64 strings."""
    sample_dir = PROJECT_ROOT / "app" / "sample_scans"
    if not sample_dir.exists() or len(list(sample_dir.glob("*.jpg"))) == 0:
        sample_dir = PROJECT_ROOT / "data" / "test" / "images"
    sample_files = sorted(list(sample_dir.glob("*.jpg"))) if sample_dir.exists() else []

    b64_list = []
    for f in sample_files[:3]:
        with open(f, "rb") as img_f:
            b64_list.append(base64.b64encode(img_f.read()).decode())

    # Fallbacks if list is short
    while len(b64_list) < 3:
        b64_list.append(b64_list[0] if len(b64_list) > 0 else "")
    return b64_list

def render_landing_page(page_workstation=None):
    """Renders the complete cinematic, highly animated landing page."""

    def go_to_workstation():
        if page_workstation is not None:
            st.switch_page(page_workstation)
        else:
            st.switch_page("workstation")

    samples_b64 = load_sample_images()
    s1_b64, s2_b64, s3_b64 = samples_b64[0], samples_b64[1], samples_b64[2]

    # =========================================================================
    # 1. TOP NAVBAR (STICKY, BLURRED BACKDROP, RED BRAND ACCENT)
    # =========================================================================
    nav_c1, nav_c2, nav_c3 = st.columns([1.5, 2.6, 1], gap="small")
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
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; gap: 28px; padding-top: 6px;">
            <a href="#how-it-works" class="lp-nav-item">How It Works</a>
            <a href="#why-renalscan" class="lp-nav-item">Why RenalScan</a>
            <a href="#showcase" class="lp-nav-item">Showcase</a>
            <a href="#kidney-health" class="lp-nav-item">Kidney Health</a>
            <a href="#about" class="lp-nav-item">About</a>
        </div>
        """, unsafe_allow_html=True)

    with nav_c3:
        if st.button("Launch Workstation", key="nav_launch_lp", use_container_width=True):
            go_to_workstation()

    st.write("")

    # =========================================================================
    # 2. CINEMATIC HERO (HIGHLY ANIMATED MEDICAL VISUALIZATION)
    # =========================================================================
    st.markdown("""<div class="lp-hero-wrapper">""", unsafe_allow_html=True)
    hero_col_left, hero_col_right = st.columns([1.15, 1.25], gap="large")

    with hero_col_left:
        st.markdown("""
        <div class="lp-badge-animated">
            <span class="lp-badge-dot"></span>
            AI-POWERED MEDICAL IMAGING
        </div>
        <h1 class="lp-hero-heading">
            See Beyond the Scan.<br>
            <span class="red-accent">Understand the Stone.</span>
        </h1>
        <p class="lp-hero-desc">
            RenalScan uses AI-assisted CT image analysis to detect, visualize, segment, and measure potential kidney stone regions with calibrated millimeter precision.
        </p>
        """, unsafe_allow_html=True)

        h_btn1, h_btn2, h_btn_space = st.columns([1, 1.1, 0.1])
        with h_btn1:
            if st.button("Start Analysis →", key="hero_start_btn", use_container_width=True):
                go_to_workstation()
        with h_btn2:
            st.markdown("""
            <a href="#how-it-works" class="rs-btn-outline" style="width: 100%; box-sizing: border-box;">
                Explore RenalScan
            </a>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 24px; font-size: 0.84rem; color: #6B7280; font-weight: 500;">
            <span style="color: #B9362F; font-size: 1.1rem;">🛡️</span>
            <span>Technical Research Platform • YOLOv8s &amp; Otsu Sub-pixel Sizing</span>
        </div>
        """, unsafe_allow_html=True)

    with hero_col_right:
        # Animated Hero Visual: Floating CT Card + Laser Scanning Line + Floating White Metric Cards
        hero_ct_html = f"""
        <div class="lp-ct-float-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 0 4px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #B9362F; display: inline-block;"></span>
                    <span style="color: #D1D5DB; font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Abdominal CT Slice (Axial)</span>
                </div>
                <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #10B981; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">
                    ● LIVE PIPELINE
                </span>
            </div>
            
            <div style="position: relative; width: 100%; border-radius: 14px; overflow: hidden; background: #000000; display: flex; align-items: center; justify-content: center;">
                <!-- Animated Red Scan Line -->
                <div class="lp-laser-scanner"></div>
                
                <!-- Base CT Image -->
                <img src="data:image/jpeg;base64,{s1_b64}" style="width: 100%; max-height: 330px; object-fit: contain; opacity: 0.94;" alt="Abdominal CT Scan" />
                
                <!-- Medical SVG Overlay with Calipers, Contours, and Pulse Rings -->
                <svg viewBox="0 0 500 360" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <!-- Stone 1 Detection Box & Caliper -->
                    <rect x="220" y="140" width="75" height="68" fill="rgba(185,54,47,0.18)" stroke="#B9362F" stroke-width="2.5" stroke-dasharray="6 3" rx="6" />
                    <line x1="210" y1="174" x2="305" y2="174" stroke="#D94841" stroke-width="2" stroke-dasharray="3 3" />
                    <line x1="257" y1="130" x2="257" y2="218" stroke="#D94841" stroke-width="2" stroke-dasharray="3 3" />
                    <circle cx="257" cy="174" r="5" fill="#B9362F" stroke="#FFFFFF" stroke-width="1.5" />
                    
                    <!-- Pulsing Detection Target Marker -->
                    <circle cx="257" cy="174" r="14" fill="none" stroke="#D94841" stroke-width="1.5" opacity="0.75">
                        <animate attributeName="r" values="8;24;8" dur="2.4s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.9;0;0.9" dur="2.4s" repeatCount="indefinite"/>
                    </circle>

                    <!-- Real-Time Readout Overlay Tag -->
                    <g transform="translate(295, 126)">
                        <rect x="0" y="0" width="138" height="26" rx="6" fill="rgba(17, 24, 39, 0.92)" stroke="#B9362F" stroke-width="1.5" />
                        <text x="8" y="17" fill="#FFFFFF" font-family="'Inter', sans-serif" font-size="11" font-weight="700">
                            STONE: 8.19mm | 92%
                        </text>
                    </g>
                </svg>

                <!-- Floating Glass Card 1: AI Detection -->
                <div class="lp-float-card lp-float-card-1">
                    <div style="font-size: 0.68rem; color: #6B7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">AI Detection</div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                        <span style="width: 7px; height: 7px; background: #B9362F; border-radius: 50%; display: inline-block;"></span>
                        <span style="font-size: 0.92rem; font-weight: 800; color: #B9362F;">Stone Detected</span>
                    </div>
                </div>

                <!-- Floating Glass Card 2: Status -->
                <div class="lp-float-card lp-float-card-2">
                    <div style="font-size: 0.68rem; color: #047857; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Analysis Status</div>
                    <div style="display: flex; align-items: center; gap: 5px; margin-top: 2px;">
                        <span style="color: #10B981; font-weight: 900; font-size: 0.95rem;">✓</span>
                        <span style="font-size: 0.92rem; font-weight: 800; color: #065F46;">Complete (3/3)</span>
                    </div>
                </div>

                <!-- Floating Glass Card 3: Measurement -->
                <div class="lp-float-card lp-float-card-3">
                    <div style="font-size: 0.68rem; color: #8F2924; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Measurement</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #B9362F; margin-top: 2px;">
                        8.19 <span style="font-size: 0.78rem;">mm</span>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(hero_ct_html, unsafe_allow_html=True)

    # Scroll to Explore Indicator
    st.markdown("""
    <div class="lp-scroll-ind-container">
        <a href="#trust-strip" style="text-decoration: none; display: flex; flex-direction: column; align-items: center;">
            <span class="lp-scroll-ind-text">Scroll to Explore</span>
            <span class="lp-scroll-ind-arrow">↓</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # =========================================================================
    # 3. TRUST STRIP (SEQUENTIAL VALUE BAR)
    # =========================================================================
    st.markdown("""
    <div id="trust-strip" class="lp-trust-strip">
        <div class="lp-trust-item"><span class="lp-trust-icon">🔬</span> AI-Assisted CT Analysis</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">🎯</span> Stone Detection</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">✂️</span> Image Segmentation</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">📐</span> Size Measurement</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">📄</span> Structured Reporting</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 4. "WHY RENALSCAN?" SECTION (SPLIT EDITORIAL WITH DYNAMIC PREVIEW)
    # =========================================================================
    st.markdown("""
    <div id="why-renalscan" class="lp-section-header">
        <h2 class="lp-section-title">From Pixels to <span>Possibilities</span></h2>
        <p class="lp-section-desc">
            Turning complex CT images into structured, AI-assisted insights for rapid clinical evaluation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    why_c1, why_c2 = st.columns([1.1, 1.3], gap="large")
    with why_c1:
        st.markdown(f"""
        <div style="background-color: #111827; border-radius: 18px; border: 1.5px solid #1F2937; border-top: 3.5px solid #B9362F; padding: 22px; box-shadow: 0 12px 36px rgba(0,0,0,0.22);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="color: #FFFFFF; font-size: 0.88rem; font-weight: 800;">DIAGNOSTIC ROI EXTRACTION</span>
                <span style="background: #FCEDEC; color: #B9362F; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                    Sub-pixel Otsu
                </span>
            </div>
            <div style="position: relative; border-radius: 10px; overflow: hidden; background: #000;">
                <img src="data:image/jpeg;base64,{s2_b64}" style="width: 100%; max-height: 290px; object-fit: contain;" alt="Diagnostic ROI" />
                <svg viewBox="0 0 400 280" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <circle cx="210" cy="145" r="32" fill="rgba(185,54,47,0.28)" stroke="#B9362F" stroke-width="2.5" />
                    <line x1="178" y1="145" x2="242" y2="145" stroke="#FFFFFF" stroke-width="1.8" />
                    <line x1="210" y1="113" x2="210" y2="177" stroke="#FFFFFF" stroke-width="1.8" />
                </svg>
            </div>
            <div style="margin-top: 14px; background: rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; font-size: 0.82rem; color: #D1D5DB; line-height: 1.5;">
                <strong style="color: #F87171;">Clinical Precision:</strong> Adaptive segmentation isolates calculus margins from high-density renal cortex and vertebral bone artifacts.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with why_c2:
        st.markdown("""
        <div class="lp-feature-card">
            <div class="lp-feature-num">01</div>
            <div>
                <div class="lp-feature-title">DETECT</div>
                <div class="lp-feature-desc">
                    AI identifies potential stone regions within the abdominal CT scan using YOLOv8 trained specifically on non-contrast imaging.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">02</div>
            <div>
                <div class="lp-feature-title">SEGMENT</div>
                <div class="lp-feature-desc">
                    Detected regions are visually isolated through classical sub-pixel Otsu thresholding, separating hyperdense calcifications from surrounding tissue.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">03</div>
            <div>
                <div class="lp-feature-title">MEASURE</div>
                <div class="lp-feature-desc">
                    Calibrated physical calipers compute major axis, minor axis, and equivalent circle diameter with standardized millimeter conversions.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">04</div>
            <div>
                <div class="lp-feature-title">UNDERSTAND</div>
                <div class="lp-feature-desc">
                    Results are categorized into established clinical passage triage bands (&lt;4mm, 4–6mm, 6–10mm, &gt;10mm) and structured in an interactive workspace.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # 5. INTERACTIVE HOW IT WORKS (HORIZONTAL ANIMATED PIPELINE)
    # =========================================================================
    st.markdown("""
    <div id="how-it-works" class="lp-section-header" style="margin-top: 40px;">
        <h2 class="lp-section-title">How RenalScan <span>Thinks</span></h2>
        <p class="lp-section-desc">
            An automated six-phase pipeline engineered to deliver reproducible, quantitative insights in under two seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pipeline_component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; background: transparent; color: #20283A; }}
            .pipe-wrap {{ background: #FCEDEC; border: 1.5px solid #F1D5D5; border-radius: 20px; padding: 28px 24px; box-shadow: 0 4px 18px rgba(185, 54, 47, 0.04); }}
            .pipe-steps {{ display: flex; align-items: center; justify-content: space-between; position: relative; margin-bottom: 24px; }}
            .pipe-line {{ position: absolute; top: 22px; left: 8%; right: 8%; height: 3px; background: #F1D5D5; z-index: 1; }}
            .pipe-line-progress {{ position: absolute; top: 22px; left: 8%; width: 60%; height: 3px; background: #B9362F; z-index: 2; transition: width 0.4s ease; }}
            .step-node {{ display: flex; flex-direction: column; align-items: center; position: relative; z-index: 3; cursor: pointer; transition: transform 0.2s ease; width: 15%; }}
            .step-node:hover {{ transform: translateY(-3px); }}
            .step-badge {{ width: 44px; height: 44px; border-radius: 50%; background: #FFFFFF; border: 2.5px solid #F1D5D5; color: #6B7280; font-weight: 800; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: all 0.3s ease; }}
            .step-node.active .step-badge {{ background: #B9362F; border-color: #B9362F; color: #FFFFFF; box-shadow: 0 4px 14px rgba(185, 54, 47, 0.35); }}
            .step-lbl {{ font-size: 0.82rem; font-weight: 800; color: #4B5563; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.04em; }}
            .step-node.active .step-lbl {{ color: #B9362F; }}
            
            .detail-card {{ background: #FFFFFF; border: 1.5px solid #F1D5D5; border-left: 5px solid #B9362F; border-radius: 14px; padding: 20px 24px; box-shadow: 0 4px 16px rgba(185, 54, 47, 0.05); display: flex; align-items: center; justify-content: space-between; }}
            .detail-left {{ max-width: 70%; }}
            .detail-title {{ font-size: 1.15rem; font-weight: 800; color: #20283A; margin-bottom: 6px; }}
            .detail-desc {{ font-size: 0.9rem; color: #4B5563; line-height: 1.55; }}
            .detail-chip {{ background: #FCEDEC; border: 1px solid #F1D5D5; color: #B9362F; font-weight: 800; font-size: 0.78rem; padding: 6px 14px; border-radius: 8px; letter-spacing: 0.05em; }}
        </style>
    </head>
    <body>
        <div class="pipe-wrap">
            <div class="pipe-steps">
                <div class="pipe-line"></div>
                <div class="pipe-line-progress" id="pipeProgress"></div>
                
                <div class="step-node active" onclick="setStep(1)">
                    <div class="step-badge" id="b1">01</div>
                    <div class="step-lbl">UPLOAD</div>
                </div>
                <div class="step-node" onclick="setStep(2)">
                    <div class="step-badge" id="b2">02</div>
                    <div class="step-lbl">PREPROCESS</div>
                </div>
                <div class="step-node" onclick="setStep(3)">
                    <div class="step-badge" id="b3">03</div>
                    <div class="step-lbl">DETECT</div>
                </div>
                <div class="step-node" onclick="setStep(4)">
                    <div class="step-badge" id="b4">04</div>
                    <div class="step-lbl">SEGMENT</div>
                </div>
                <div class="step-node" onclick="setStep(5)">
                    <div class="step-badge" id="b5">05</div>
                    <div class="step-lbl">MEASURE</div>
                </div>
                <div class="step-node" onclick="setStep(6)">
                    <div class="step-badge" id="b6">06</div>
                    <div class="step-lbl">ANALYZE</div>
                </div>
            </div>

            <div class="detail-card">
                <div class="detail-left">
                    <div class="detail-title" id="cardTitle">01 UPLOAD — Ingest CT Scan Slices</div>
                    <div class="detail-desc" id="cardDesc">
                        Ingests high-resolution abdominal CT images in standard JPG, PNG, or DICOM-derived slices up to 200MB.
                    </div>
                </div>
                <div class="detail-chip" id="cardChip">STAGE 1 / 6</div>
            </div>
        </div>

        <script>
            const steps = [
                {{ title: "01 UPLOAD — Ingest CT Scan Slices", desc: "Ingests high-resolution abdominal CT images in standard JPG, PNG, or DICOM-derived slices up to 200MB with automated integrity checks.", chip: "STAGE 1 / 6 • INPUT", pct: "0%" }},
                {{ title: "02 PREPROCESS — Dynamic Contrast & Normalization", desc: "Normalizes dimensions, channels, and window levels to optimize Hounsfield-unit attenuation visibility before deep inference.", chip: "STAGE 2 / 6 • PREP", pct: "20%" }},
                {{ title: "03 DETECT — YOLOv8 Deep Calculus Localization", desc: "Runs fine-tuned YOLOv8s detector to localize candidate stone coordinates and assign probabilistic confidence ratings.", chip: "STAGE 3 / 6 • INFERENCE", pct: "40%" }},
                {{ title: "04 SEGMENT — Sub-pixel Otsu Contour Isolation", desc: "Executes adaptive local Otsu thresholding on padded detection regions to delineate precise calculus surface perimeters.", chip: "STAGE 4 / 6 • COMPUTER VISION", pct: "60%" }},
                {{ title: "05 MEASURE — Physical Caliper Geometry", desc: "Applies calibrated millimeter scaling (assumed 0.70 mm/px) to calculate major axis, minor axis, area, and equivalent diameter.", chip: "STAGE 5 / 6 • QUANTIFICATION", pct: "80%" }},
                {{ title: "06 ANALYZE — Clinical Triage & Report Export", desc: "Maps stones into risk bands (<4mm, 4-6mm, 6-10mm, >10mm) and compiles downloadable clinical summaries and CSV data.", chip: "STAGE 6 / 6 • REPORTING", pct: "100%" }}
            ];
            let activeIdx = 0;
            function setStep(num) {{
                activeIdx = num - 1;
                for(let i=1; i<=6; i++) {{
                    document.getElementById('b' + i).parentElement.classList.toggle('active', i === num);
                }}
                document.getElementById('pipeProgress').style.width = steps[activeIdx].pct;
                document.getElementById('cardTitle').innerText = steps[activeIdx].title;
                document.getElementById('cardDesc').innerText = steps[activeIdx].desc;
                document.getElementById('cardChip').innerText = steps[activeIdx].chip;
            }}
            // Auto loop every 4.5 seconds
            setInterval(() => {{
                activeIdx = (activeIdx + 1) % 6;
                setStep(activeIdx + 1);
            }}, 4500);
        </script>
    </body>
    </html>
    """
    components.html(pipeline_component_html, height=220, scrolling=False)

    # =========================================================================
    # 6. BIG CT SCAN SHOWCASE (DEEP CHARCOAL #16181D MEDICAL AI DEMONSTRATION)
    # =========================================================================
    st.markdown("""
    <div id="showcase" class="lp-dark-showcase">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
            <div>
                <div style="color: #D94841; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px;">
                    MEDICAL COMPUTER VISION SHOWCASE
                </div>
                <div class="lp-dark-title">Watch AI Find What the Eye Might Miss.</div>
                <div class="lp-dark-sub">
                    Visualize potential stone regions directly on CT images with automated multi-layer bounding and millimeter calipers.
                </div>
            </div>
            <span style="background: rgba(185,54,47,0.25); border: 1.5px solid #B9362F; color: #FFFFFF; font-weight: 700; font-size: 0.82rem; padding: 6px 16px; border-radius: 20px;">
                ● Multi-Layer Overlay
            </span>
        </div>
    """, unsafe_allow_html=True)

    showcase_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; background: transparent; margin: 0; color: #FFFFFF; }}
            .viewer-card {{ background: #0F131C; border: 1.5px solid #2A2F3B; border-radius: 18px; padding: 20px; display: flex; gap: 24px; }}
            .ct-frame {{ position: relative; width: 55%; height: 380px; background: #000; border-radius: 12px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
            .ct-frame img {{ max-height: 360px; max-width: 100%; object-fit: contain; }}
            
            .scan-bar {{ position: absolute; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #E53935, #FFF, #E53935, transparent); box-shadow: 0 0 16px #E53935; animation: sweepLoop 3.8s infinite ease-in-out; }}
            @keyframes sweepLoop {{ 0% {{ top: 4%; opacity: 0; }} 15% {{ opacity: 1; }} 85% {{ opacity: 1; }} 100% {{ top: 94%; opacity: 0; }} }}
            
            .info-panel {{ width: 45%; display: flex; flex-direction: column; justify-content: space-between; }}
            .panel-header {{ border-bottom: 1.5px solid #1F2937; padding-bottom: 12px; }}
            .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }}
            .stat-box {{ background: #161B26; border: 1px solid #2A2F3B; border-left: 3px solid #B9362F; border-radius: 10px; padding: 12px; }}
            .stat-lbl {{ font-size: 0.7rem; color: #9CA3AF; font-weight: 700; text-transform: uppercase; }}
            .stat-val {{ font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-top: 2px; }}
            
            .tag-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
            .tag {{ font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; background: rgba(255,255,255,0.06); color: #D1D5DB; }}
            .tag.active {{ background: #B9362F; color: #FFFFFF; }}
        </style>
    </head>
    <body>
        <div class="viewer-card">
            <div class="ct-frame">
                <div class="scan-bar"></div>
                <img src="data:image/jpeg;base64,{s1_b64}" alt="CT Analysis Demonstration" />
                <svg viewBox="0 0 400 320" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <rect x="155" y="115" width="70" height="60" fill="rgba(185,54,47,0.22)" stroke="#B9362F" stroke-width="2" stroke-dasharray="5 3" rx="4"/>
                    <line x1="145" y1="145" x2="235" y2="145" stroke="#D94841" stroke-width="2" stroke-dasharray="3"/>
                    <line x1="190" y1="105" x2="190" y2="185" stroke="#D94841" stroke-width="2" stroke-dasharray="3"/>
                    <circle cx="190" cy="145" r="4" fill="#B9362F"/>
                </svg>
            </div>
            <div class="info-panel">
                <div>
                    <div class="panel-header">
                        <span style="color: #10B981; font-weight: 800; font-size: 0.78rem;">● ANALYSIS PIPELINE EXECUTED</span>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-top: 4px;">Verified Stone Localization</div>
                    </div>
                    <div class="stat-grid">
                        <div class="stat-box">
                            <div class="stat-lbl">DETECTED CALCULI</div>
                            <div class="stat-val" style="color: #FFFFFF;">3 Regions</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-lbl">PRIMARY DIAMETER</div>
                            <div class="stat-val" style="color: #D94841;">5.27 mm</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-lbl">PEAK CONFIDENCE</div>
                            <div class="stat-val" style="color: #10B981;">69.6%</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-lbl">CLINICAL BAND</div>
                            <div class="stat-val" style="font-size: 0.95rem; color: #F87171;">4-6mm (Medium)</div>
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #9CA3AF; line-height: 1.5;">
                        AI pipeline localized multiple calculi in the renal calyx. Caliper measurements estimate primary axis dimensions with moderate spontaneous passage likelihood (~50%).
                    </div>
                </div>
                <div class="tag-row">
                    <span class="tag active">YOLOv8s Detector</span>
                    <span class="tag active">Otsu Contour</span>
                    <span class="tag">0.70 mm/px Calibration</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    components.html(showcase_html, height=430, scrolling=False)
    st.markdown("""</div>""", unsafe_allow_html=True)

    # =========================================================================
    # 7. LIVE ANALYSIS UI (ANIMATED COUNT-UP NUMBERS)
    # =========================================================================
    st.markdown("""
    <div class="lp-section-header">
        <h2 class="lp-section-title">Automated <span>Quantitative Assessment</span></h2>
        <p class="lp-section-desc">
            Instantly extracts numerical metrics, size stratifications, and calibrated geometric boundaries.
        </p>
    </div>
    """, unsafe_allow_html=True)

    countup_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; background: transparent; margin: 0; padding: 4px; color: #20283A; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
            .metric-card {{ background: #FFFFFF; border: 1.5px solid #F1D5D5; border-top: 4px solid #B9362F; border-radius: 16px; padding: 22px 16px; text-align: center; box-shadow: 0 4px 16px rgba(185, 54, 47, 0.05); }}
            .metric-lbl {{ font-size: 0.78rem; font-weight: 800; color: #6B7280; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }}
            .metric-val {{ font-size: 2.3rem; font-weight: 900; color: #B9362F; line-height: 1; }}
            .metric-sub {{ font-size: 0.8rem; color: #4B5563; margin-top: 6px; font-weight: 600; }}
            
            .regions-box {{ background: #FFFFFF; border: 1.5px solid #F1D5D5; border-radius: 16px; padding: 22px 26px; box-shadow: 0 4px 16px rgba(185, 54, 47, 0.04); }}
            .regions-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
            .stone-row {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1.2fr; gap: 12px; padding: 12px 14px; background: #FFF7F7; border: 1px solid #F1D5D5; border-radius: 10px; margin-bottom: 8px; align-items: center; }}
            .stone-id {{ font-weight: 800; color: #B9362F; font-size: 0.92rem; }}
            .stone-data {{ font-size: 0.88rem; font-weight: 700; color: #20283A; }}
        </style>
    </head>
    <body>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-lbl">POTENTIAL STONES</div>
                <div class="metric-val" id="numStones">0</div>
                <div class="metric-sub">Calculi Localized</div>
            </div>
            <div class="metric-card">
                <div class="metric-lbl">LARGEST SIZE</div>
                <div class="metric-val"><span id="numSize">0.00</span> <span style="font-size: 1.2rem;">mm</span></div>
                <div class="metric-sub">Calibrated Diameter</div>
            </div>
            <div class="metric-card">
                <div class="metric-lbl">PEAK CONFIDENCE</div>
                <div class="metric-val"><span id="numConf">0</span>%</div>
                <div class="metric-sub">Probability Score</div>
            </div>
        </div>

        <div class="regions-box">
            <div class="regions-header">
                <div style="font-weight: 800; font-size: 1.05rem; color: #20283A;">Localized Stone Regions (Quantitative Log)</div>
                <span style="background: #FCEDEC; color: #B9362F; font-weight: 800; font-size: 0.75rem; padding: 4px 10px; border-radius: 8px;">3 DETECTIONS</span>
            </div>
            <div class="stone-row">
                <div class="stone-id">Calculus #01</div>
                <div class="stone-data">5.27 mm</div>
                <div class="stone-data" style="color: #10B981;">69.6% Conf</div>
                <div style="font-size: 0.82rem; color: #B9362F; font-weight: 700;">4–6mm (Medium)</div>
            </div>
            <div class="stone-row">
                <div class="stone-id">Calculus #02</div>
                <div class="stone-data">3.66 mm</div>
                <div class="stone-data" style="color: #10B981;">54.9% Conf</div>
                <div style="font-size: 0.82rem; color: #047857; font-weight: 700;">&lt;4mm (Small)</div>
            </div>
            <div class="stone-row">
                <div class="stone-id">Calculus #03</div>
                <div class="stone-data">2.16 mm</div>
                <div class="stone-data" style="color: #6B7280;">44.4% Conf</div>
                <div style="font-size: 0.82rem; color: #047857; font-weight: 700;">&lt;4mm (Small)</div>
            </div>
        </div>

        <script>
            function animateCount(elemId, target, decimals, duration) {{
                let start = 0;
                let startTime = null;
                function update(now) {{
                    if (!startTime) startTime = now;
                    let progress = Math.min((now - startTime) / duration, 1);
                    let val = start + progress * (target - start);
                    document.getElementById(elemId).innerText = val.toFixed(decimals);
                    if (progress < 1) requestAnimationFrame(update);
                }}
                requestAnimationFrame(update);
            }}
            // Trigger count up animations smoothly
            setTimeout(() => {{
                animateCount('numStones', 3, 0, 1200);
                animateCount('numSize', 5.27, 2, 1400);
                animateCount('numConf', 70, 0, 1600);
            }}, 200);
        </script>
    </body>
    </html>
    """
    components.html(countup_html, height=320, scrolling=False)

    # =========================================================================
    # 8. REPORT PREVIEW (FLOATING A4 REPORT WITH 3D TILT EFFECT)
    # =========================================================================
    st.markdown("""
    <div class="lp-section-header" style="margin-top: 40px;">
        <h2 class="lp-section-title">From Analysis to a <span>Professional Report</span></h2>
        <p class="lp-section-desc">
            Standardized clinical findings generated automatically in printable text and structured CSV formats.
        </p>
    </div>
    """, unsafe_allow_html=True)

    rep_col1, rep_col2 = st.columns([1.3, 1], gap="large")
    with rep_col1:
        st.markdown("""
        <div class="lp-a4-report">
            <div style="border-bottom: 2.5px solid #B9362F; padding-bottom: 14px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: flex-end;">
                <div>
                    <div style="font-size: 1.3rem; font-weight: 900; color: #20283A; letter-spacing: -0.02em;">
                        RENAL<span style="color: #B9362F;">SCAN</span>
                    </div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #6B7280; letter-spacing: 0.05em;">
                        AI-ASSISTED KIDNEY STONE ANALYSIS REPORT
                    </div>
                </div>
                <div style="background-color: #FCEDEC; color: #B9362F; font-size: 0.74rem; font-weight: 800; padding: 4px 10px; border-radius: 6px;">
                    CONFIDENTIAL / RESEARCH
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; background: #FFF7F7; border: 1px solid #F1D5D5; border-radius: 10px; padding: 14px;">
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 700;">SCAN ID</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: #20283A;">RS-2026-001</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 700;">TOTAL STONES</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: #B9362F;">3 Detected</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 700;">MAX DIAMETER</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: #B9362F;">5.27 mm</div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; color: #6B7280; font-weight: 700;">CONFIDENCE</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: #10B981;">70% Mean</div>
                </div>
            </div>

            <div style="font-size: 0.88rem; color: #4B5563; line-height: 1.6; margin-bottom: 16px;">
                <strong>Clinical Evaluation Summary:</strong> Axial non-contrast CT abdominal scan demonstrates three hyperdense calcifications within the renal parenchyma. Primary calculus measures 5.27 mm (4–6mm Medium Band), indicating moderate spontaneous passage likelihood (~50%). Secondary calculi measure 3.66 mm and 2.16 mm.
            </div>

            <div style="border-top: 1px dashed #F1D5D5; padding-top: 14px; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #9CA3AF;">
                <span>Verified by RenalScan AI Model v2.0</span>
                <span>Assumed Spacing: 0.70 mm/px</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with rep_col2:
        st.markdown("""
        <div style="padding-top: 14px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: #FCEDEC; color: #B9362F; font-size: 0.78rem; font-weight: 800; padding: 4px 12px; border-radius: 6px; margin-bottom: 12px;">
                📄 ONE-CLICK EXPORT
            </div>
            <div style="font-size: 1.4rem; font-weight: 900; color: #20283A; margin-bottom: 12px; line-height: 1.2;">
                Seamless Documentation for Clinical Workflows
            </div>
            <p style="font-size: 0.95rem; color: #4B5563; line-height: 1.6; margin-bottom: 22px;">
                Export comprehensive summaries including calculus counts, physical caliper dimensions, Otsu contour perimeters, and clinical passage predictions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explore Analysis →", key="rep_explore_btn", use_container_width=True):
            go_to_workstation()

    # =========================================================================
    # 9. KIDNEY HEALTH (4 LARGE CARDS)
    # =========================================================================
    st.markdown("""
    <div id="kidney-health" class="lp-section-header" style="margin-top: 50px;">
        <h2 class="lp-section-title">Know Your <span>Kidneys</span></h2>
        <p class="lp-section-desc">
            Essential nephrolithiasis knowledge, symptoms, risk factors, and evidence-based preventive guidance.
        </p>
    </div>
    <div class="lp-health-grid">
        <div class="lp-health-card">
            <div class="lp-health-icon">🫘</div>
            <div class="lp-health-title">KIDNEY STONES</div>
            <div class="lp-health-desc">
                Hard mineral and salt deposits (calcium oxalate, uric acid, struvite, cystine) that crystallize inside the renal pelvis and calyces.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-health-icon">⚡</div>
            <div class="lp-health-title">SYMPTOMS</div>
            <div class="lp-health-desc">
                Severe radiating flank and lower abdominal pain, visible hematuria (blood in urine), painful dysuria, urinary urgency, and nausea.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-health-icon">⚠️</div>
            <div class="lp-health-title">RISK FACTORS</div>
            <div class="lp-health-desc">
                Chronic dehydration, high sodium and animal protein intake, familial history, metabolic disorders, hyperparathyroidism, and obesity.
            </div>
        </div>
        <div class="lp-health-card">
            <div class="lp-health-icon">💧</div>
            <div class="lp-health-title">PREVENTION</div>
            <div class="lp-health-desc">
                Consistently drinking sufficient fluids to generate &gt;2.5L daily urine volume, reducing dietary sodium, and balancing calcium intake.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 10. RESPONSIBLE AI (SHIELD PULSE SECTION)
    # =========================================================================
    st.markdown("""
    <div id="about" class="lp-shield-section">
        <div class="lp-shield-icon-box">🛡️</div>
        <div>
            <div style="font-size: 1.25rem; font-weight: 900; color: #20283A; margin-bottom: 6px;">
                AI-Assisted. Human-Centered.
            </div>
            <div style="font-size: 0.92rem; color: #4B5563; line-height: 1.65;">
                RenalScan is designed as an assistive computer vision system for technical research and medical imaging education. AI-generated findings provide supportive quantification and must be reviewed by certified medical specialists. This application is not a standalone diagnostic device.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 11. FINAL CTA (DEEP RED / DARK RED CONTAINER)
    # =========================================================================
    st.markdown("""
    <div class="lp-final-cta-wrapper">
        <h2 class="lp-final-cta-title">Your Scan. A Smarter Way to Analyze It.</h2>
        <p class="lp-final-cta-sub">
            Experience the automated detection, segmentation, and sizing pipeline inside the RenalScan Analysis Workstation.
        </p>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns([1, 1.2, 1])
    with f_col2:
        if st.button("Start Analysis →", key="final_deep_start", use_container_width=True):
            go_to_workstation()

    st.markdown("""
        <div style="margin-top: 18px;">
            <a href="#how-it-works" style="color: #FEE2E2; font-size: 0.88rem; text-decoration: underline; font-weight: 700;">
                How It Works
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 12. FOOTER (DARK CHARCOAL WITH RED ACCENT)
    # =========================================================================
    st.markdown("""
    <div class="lp-footer">
        <div class="lp-footer-grid">
            <div>
                <div style="font-size: 1.35rem; font-weight: 900; color: #FFFFFF; margin-bottom: 4px;">
                    Renal<span style="color: #D94841;">Scan</span>
                </div>
                <div style="font-size: 0.84rem; color: #9CA3AF; margin-bottom: 12px; font-weight: 600;">
                    AI Kidney Stone Analysis
                </div>
                <div style="font-size: 0.85rem; color: #6B7280; line-height: 1.6; max-width: 320px;">
                    AI-assisted kidney stone analysis from abdominal CT scans. Built for medical imaging innovation, portfolio evaluation, and computer vision research.
                </div>
            </div>
            <div class="lp-footer-col">
                <h4>Navigation</h4>
                <ul>
                    <li><a href="#" style="color: #9CA3AF; text-decoration: none;">Home</a></li>
                    <li><a href="#how-it-works" style="color: #9CA3AF; text-decoration: none;">How It Works</a></li>
                    <li><a href="#why-renalscan" style="color: #9CA3AF; text-decoration: none;">Why RenalScan</a></li>
                    <li><a href="#showcase" style="color: #9CA3AF; text-decoration: none;">Showcase</a></li>
                </ul>
            </div>
            <div class="lp-footer-col">
                <h4>Resources</h4>
                <ul>
                    <li><a href="#kidney-health" style="color: #9CA3AF; text-decoration: none;">Kidney Health</a></li>
                    <li><a href="#about" style="color: #9CA3AF; text-decoration: none;">About Responsible AI</a></li>
                    <li><a href="/workstation" style="color: #9CA3AF; text-decoration: none;">Live Workstation</a></li>
                </ul>
            </div>
        </div>
        <div class="lp-footer-bottom">
            © 2026 RenalScan. AI-assisted analysis. Not a substitute for professional medical advice.
        </div>
    </div>
    """, unsafe_allow_html=True)
