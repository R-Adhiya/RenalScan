"""
landing_page.py - Complete, Premium, Highly Animated RenalScan Landing Website
Follows Enterprise Healthcare AI Startup Visual Standards:
  1. Sticky Navbar
  2. Full Animated Hero (Left 50-55% Messaging, Right 45-50% Preserved Animated CT Visual)
  3. Hero Background Animation (Faint grid & red radial glow)
  4. Scroll Indicator
  5. Trust / Capability Strip (6 items)
  6. Why RenalScan (01 DETECT, 02 SEGMENT, 03 MEASURE, 04 ANALYZE + Animated CT)
  7. How It Works (01 to 06 Animated Timeline)
  8. Big Interactive CT Demo (Dark #16181D, 8-step animation sequence)
  9. Features (6 Premium Cards)
  10. Workstation Preview (Realistic Workstation UI Preview + Launch CTA)
  11. Report Preview (Floating A4 Report Card)
  12. Kidney Health (4 Interactive Cards with Hover Reveals)
  13. Responsible AI (Pulsing Medical Shield)
  14. Final CTA (Deep Red Gradient + White Button)
  15. Minimal Footer
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

    while len(b64_list) < 3:
        b64_list.append(b64_list[0] if len(b64_list) > 0 else "")
    return b64_list

def render_landing_page(page_workstation=None):
    """Renders the complete 15-section product landing website."""

    def go_to_workstation():
        st.session_state["current_page"] = "workstation"
        if page_workstation is not None:
            st.switch_page(page_workstation)
        else:
            st.switch_page("workstation")

    samples_b64 = load_sample_images()
    s1_b64, s2_b64, s3_b64 = samples_b64[0], samples_b64[1], samples_b64[2]

    # =========================================================================
    # 1. NAVBAR (STICKY, BLURRED BACKDROP, RED BRAND ACCENT)
    # =========================================================================
    nav_c1, nav_c2, nav_c3 = st.columns([1.3, 3.7, 1.2], gap="small")
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
            <a href="#why-renalscan" class="lp-nav-item">Why RenalScan</a>
            <a href="#demo" class="lp-nav-item">CT Demo</a>
            <a href="#features" class="lp-nav-item">Capabilities</a>
            <a href="#kidney-health" class="lp-nav-item">Kidney Health</a>
            <a href="#about" class="lp-nav-item">About</a>
        </div>
        """, unsafe_allow_html=True)

    with nav_c3:
        if st.button("Launch Workstation", key="nav_launch_lp", use_container_width=True):
            go_to_workstation()

    st.write("")

    # =========================================================================
    # 2. FULL ANIMATED HERO (LEFT 50-55% MESSAGING, RIGHT 45-50% CT VISUAL)
    # =========================================================================
    hero_col_left, hero_col_right = st.columns([1.18, 1.22], gap="large")

    with hero_col_left:
        st.markdown("""
        <div class="lp-badge-animated">
            <span class="lp-badge-dot"></span>
            AI-POWERED MEDICAL IMAGING
        </div>
        <h1 class="lp-hero-heading">
            Smarter <span class="red-accent">Kidney Stone</span><br>
            Analysis with <span class="red-accent">AI.</span>
        </h1>
        <p class="lp-hero-desc">
            RenalScan transforms CT images into AI-assisted kidney stone insights — helping visualize potential stone regions, estimate measurements, and organize analysis results.
        </p>
        """, unsafe_allow_html=True)

        h_btn1, h_btn2, h_btn_space = st.columns([1, 1.15, 0.1])
        with h_btn1:
            if st.button("Start Analysis →", key="hero_start_btn", use_container_width=True):
                go_to_workstation()
        with h_btn2:
            st.markdown("""
            <a href="#how-it-works" class="rs-btn-outline" style="width: 100%; box-sizing: border-box;">
                Explore How It Works
            </a>
            """, unsafe_allow_html=True)

        # Three Trust Checkmarks
        st.markdown("""
        <div class="lp-hero-trust-row">
            <div class="lp-hero-trust-item">
                <span class="lp-hero-trust-check">✓</span> AI-Assisted Analysis
            </div>
            <div class="lp-hero-trust-item">
                <span class="lp-hero-trust-check">✓</span> CT Visualization
            </div>
            <div class="lp-hero-trust-item">
                <span class="lp-hero-trust-check">✓</span> Stone Measurement
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hero_col_right:
        # PRESERVED ANIMATED HERO CT VISUALIZATION
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
                        <rect x="0" y="0" width="144" height="26" rx="6" fill="rgba(17, 24, 39, 0.92)" stroke="#B9362F" stroke-width="1.5" />
                        <text x="8" y="17" fill="#FFFFFF" font-family="'Inter', sans-serif" font-size="11" font-weight="700">
                            STONE: 8.19mm | 92%
                        </text>
                    </g>
                </svg>

                <!-- Floating Glass Card 1: AI Detection -->
                <div class="lp-float-card lp-float-card-1">
                    <div style="font-size: 0.68rem; color: #AAB4C0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">AI Detection</div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                        <span style="width: 7px; height: 7px; background: #FF6B63; border-radius: 50%; display: inline-block;"></span>
                        <span style="font-size: 0.92rem; font-weight: 800; color: #FF6B63;">Stone detected</span>
                    </div>
                </div>

                <!-- Floating Glass Card 2: Status -->
                <div class="lp-float-card lp-float-card-2">
                    <div style="font-size: 0.68rem; color: #34D399; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Analysis Status</div>
                    <div style="display: flex; align-items: center; gap: 5px; margin-top: 2px;">
                        <span style="color: #10B981; font-weight: 900; font-size: 0.95rem;">✓</span>
                        <span style="font-size: 0.92rem; font-weight: 800; color: #34D399;">Complete (3/3)</span>
                    </div>
                </div>

                <!-- Floating Glass Card 3: Measurement -->
                <div class="lp-float-card lp-float-card-3">
                    <div style="font-size: 0.68rem; color: #AAB4C0; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Measurement</div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #FF6B63; margin-top: 2px;">
                        8.19 <span style="font-size: 0.78rem; color: #AAB4C0;">mm</span>
                    </div>
                </div>
            </div>
        </div>
        """
        st.html(hero_ct_html)

    # 4. HERO SCROLL INDICATOR
    st.markdown("""
    <div class="lp-scroll-ind-container">
        <a href="#trust-strip" style="text-decoration: none; display: flex; flex-direction: column; align-items: center;">
            <span class="lp-scroll-ind-text">SCROLL TO EXPLORE</span>
            <span class="lp-scroll-ind-arrow">↓</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 5. TRUST / CAPABILITY STRIP (FULL WIDTH)
    # =========================================================================
    st.markdown("""
    <div id="trust-strip" class="lp-trust-strip">
        <div class="lp-trust-item"><span class="lp-trust-icon">🔬</span> AI-Assisted Analysis</div>
        <div class="lp-trust-sep">|</div>
        <div class="lp-trust-item"><span class="lp-trust-icon">⚡</span> CT Image Processing</div>
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
    # 6. WHY RENALSCAN (SPLIT WITH 01-04 AND VERTICAL ANIMATED CT VISUAL)
    # =========================================================================
    st.markdown("""
    <div id="why-renalscan" class="lp-section-header">
        <h2 class="lp-section-title">From CT Pixels to <span>Meaningful Insights</span></h2>
        <p class="lp-section-desc">
            RenalScan brings AI-assisted image analysis into one focused workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

    why_c1, why_c2 = st.columns([1.1, 1.3], gap="large")
    with why_c1:
        st.markdown("""
        <div class="lp-feature-card">
            <div class="lp-feature-num">01</div>
            <div>
                <div class="lp-feature-title">DETECT</div>
                <div class="lp-feature-desc">
                    Identify potential stone regions from CT images using a deep convolutional YOLOv8 architecture trained on non-contrast abdominal scans.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">02</div>
            <div>
                <div class="lp-feature-title">SEGMENT</div>
                <div class="lp-feature-desc">
                    Highlight detected regions for clearer visualization through classical sub-pixel Otsu thresholding, separating calculus margins from tissue.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">03</div>
            <div>
                <div class="lp-feature-title">MEASURE</div>
                <div class="lp-feature-desc">
                    Estimate dimensions of detected regions using physical millimeter calipers to compute major axis, minor axis, and equivalent diameter.
                </div>
            </div>
        </div>

        <div class="lp-feature-card">
            <div class="lp-feature-num">04</div>
            <div>
                <div class="lp-feature-title">ANALYZE</div>
                <div class="lp-feature-desc">
                    Review structured AI-assisted findings mapped into clinical passage probability triage bands (<4mm, 4–6mm, 6–10mm, >10mm).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with why_c2:
        st.html(f"""
        <div style="background-color: #151C24; border-radius: 18px; border: 1.5px solid rgba(255,255,255,0.10); border-top: 3.5px solid #B9362F; padding: 22px; box-shadow: 0 12px 36px rgba(0,0,0,0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="color: #F8FAFC; font-size: 0.88rem; font-weight: 800;">VERTICAL CT VISUALIZATION</span>
                <span style="background: rgba(185,54,47,0.18); border: 1px solid rgba(255,107,99,0.3); color: #FF6B63; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                    Multi-Stage Pipeline
                </span>
            </div>
            <div style="position: relative; border-radius: 10px; overflow: hidden; background: #000;">
                <img src="data:image/jpeg;base64,{s2_b64}" style="width: 100%; max-height: 310px; object-fit: contain;" alt="Diagnostic ROI" />
                <svg viewBox="0 0 400 280" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <circle cx="210" cy="145" r="32" fill="rgba(185,54,47,0.28)" stroke="#B9362F" stroke-width="2.5" />
                    <line x1="178" y1="145" x2="242" y2="145" stroke="#FFFFFF" stroke-width="1.8" />
                    <line x1="210" y1="113" x2="210" y2="177" stroke="#FFFFFF" stroke-width="1.8" />
                </svg>
            </div>
            <div style="margin-top: 14px; background: rgba(255,255,255,0.04); border-radius: 8px; padding: 12px; font-size: 0.82rem; color: #AAB4C0; line-height: 1.5; border: 1px solid rgba(255,255,255,0.06);">
                <strong style="color: #FF6B63;">Automated Insight:</strong> Sequential detection, contour segmentation, and caliper measurement occur simultaneously within the active slice.
            </div>
        </div>
        """)

    # =========================================================================
    # 7. HOW IT WORKS (01 TO 06 ANIMATED TIMELINE)
    # =========================================================================
    st.markdown("""
    <div id="how-it-works" class="lp-section-header" style="margin-top: 48px;">
        <h2 class="lp-section-title">How RenalScan <span>Works</span></h2>
        <p class="lp-section-desc">
            A disciplined six-phase workflow engineered to deliver reproducible, quantitative insights in under two seconds.
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
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; background: transparent; color: #F8FAFC; }}
            .pipe-wrap {{ background: #111820; border: 1.5px solid rgba(255, 255, 255, 0.10); border-radius: 20px; padding: 28px 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45); }}
            .pipe-steps {{ display: flex; align-items: center; justify-content: space-between; position: relative; margin-bottom: 24px; }}
            .pipe-line {{ position: absolute; top: 22px; left: 8%; right: 8%; height: 3px; background: rgba(255, 255, 255, 0.12); z-index: 1; }}
            .pipe-line-progress {{ position: absolute; top: 22px; left: 8%; width: 0%; height: 3px; background: linear-gradient(90deg, #B9362F, #FF6B63); z-index: 2; transition: width 0.4s ease; box-shadow: 0 0 10px rgba(255, 107, 99, 0.6); }}
            .step-node {{ display: flex; flex-direction: column; align-items: center; position: relative; z-index: 3; cursor: pointer; transition: transform 0.2s ease; width: 15%; }}
            .step-node:hover {{ transform: translateY(-3px); }}
            .step-badge {{ width: 44px; height: 44px; border-radius: 50%; background: #151C24; border: 2.5px solid rgba(255, 255, 255, 0.14); color: #AAB4C0; font-weight: 800; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: all 0.3s ease; }}
            .step-node.active .step-badge {{ background: #B9362F; border-color: #FF6B63; color: #FFFFFF; box-shadow: 0 0 16px rgba(255, 107, 99, 0.5); }}
            .step-lbl {{ font-size: 0.82rem; font-weight: 800; color: #AAB4C0; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.04em; }}
            .step-node.active .step-lbl {{ color: #FF6B63; }}
            
            .detail-card {{ background: #151C24; border: 1.5px solid rgba(255, 255, 255, 0.10); border-left: 5px solid #FF6B63; border-radius: 14px; padding: 20px 24px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35); display: flex; align-items: center; justify-content: space-between; }}
            .detail-left {{ max-width: 70%; }}
            .detail-title {{ font-size: 1.15rem; font-weight: 800; color: #F8FAFC; margin-bottom: 6px; }}
            .detail-desc {{ font-size: 0.9rem; color: #AAB4C0; line-height: 1.55; }}
            .detail-chip {{ background: rgba(185, 54, 47, 0.18); border: 1px solid rgba(255, 107, 99, 0.35); color: #FF6B63; font-weight: 800; font-size: 0.78rem; padding: 6px 14px; border-radius: 8px; letter-spacing: 0.05em; }}
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
                        Ingests high-resolution abdominal CT images in standard JPG, PNG, or DICOM-derived slices up to 200MB with automated integrity checks.
                    </div>
                </div>
                <div class="detail-chip" id="cardChip">STAGE 1 / 6 • INPUT</div>
            </div>
        </div>

        <script>
            const steps = [
                {{ title: "01 UPLOAD — Ingest CT Scan Slices", desc: "Ingests high-resolution abdominal CT images in standard JPG, PNG, or DICOM-derived slices up to 200MB with automated format and channel validation.", chip: "STAGE 1 / 6 • INPUT", pct: "0%" }},
                {{ title: "02 PREPROCESS — Window Leveling & Normalization", desc: "Normalizes dimensions, channels, and window levels to optimize Hounsfield-unit attenuation visibility before deep inference.", chip: "STAGE 2 / 6 • PREP", pct: "20%" }},
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
    # 8. BIG INTERACTIVE CT DEMO (DARK CHARCOAL #080B10)
    # =========================================================================
    st.markdown("""
    <div id="demo" class="lp-section-header" style="margin-top: 48px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
            <div>
                <div style="color: #FF6B63; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px;">
                    REAL AI ANALYSIS DEMONSTRATION
                </div>
                <div class="lp-dark-title" style="color: #F8FAFC;">Watch AI Analyze a CT Scan.</div>
                <div class="lp-dark-sub" style="color: #AAB4C0;">
                    Step through the automated sequence from scan line sweep to detection box, pulsing marker, calipers, and AI analysis panel.
                </div>
            </div>
            <span style="background: rgba(185,54,47,0.18); border: 1.5px solid rgba(255,107,99,0.35); color: #FF6B63; font-weight: 700; font-size: 0.82rem; padding: 6px 16px; border-radius: 20px;">
                ● Live 8-Step Simulation
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    demo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            body {{ font-family: 'Inter', sans-serif; background: transparent; margin: 0; color: #FFFFFF; }}
            .demo-wrap {{ background: #080B10; border: 1.5px solid rgba(255, 255, 255, 0.10); border-radius: 18px; padding: 22px; display: flex; gap: 26px; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5); }}
            .ct-box {{ position: relative; width: 55%; height: 390px; background: #000; border-radius: 12px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
            .ct-box img {{ max-height: 370px; max-width: 100%; object-fit: contain; }}
            .scan-laser {{ position: absolute; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #E53935, #FFF, #E53935, transparent); box-shadow: 0 0 16px #E53935; transition: top 0.2s ease; opacity: 0; }}
            
            .side-box {{ width: 45%; display: flex; flex-direction: column; justify-content: space-between; }}
            .panel-card {{ background: #151C24; border: 1.5px solid rgba(255, 255, 255, 0.10); border-left: 4.5px solid #FF6B63; border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); opacity: 0; transform: translateX(20px); transition: all 0.5s ease; }}
            .panel-card.slide-in {{ opacity: 1; transform: translateX(0); }}
            
            .ctrl-btns {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }}
            .demo-btn {{ background: #151C24; border: 1px solid rgba(255, 255, 255, 0.12); color: #AAB4C0; font-weight: 700; font-size: 0.8rem; padding: 8px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s; }}
            .demo-btn:hover, .demo-btn.active {{ background: #B9362F; border-color: #FF6B63; color: #FFFFFF; box-shadow: 0 0 12px rgba(185, 54, 47, 0.4); }}
        </style>
    </head>
    <body>
        <div class="demo-wrap">
            <div class="ct-box">
                <div class="scan-laser" id="laser"></div>
                <img src="data:image/jpeg;base64,{s1_b64}" id="demoImg" alt="CT Slice Demo" />
                <svg viewBox="0 0 400 320" style="position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none;">
                    <rect id="dBox" x="160" y="115" width="70" height="60" fill="rgba(185,54,47,0.22)" stroke="#B9362F" stroke-width="2.5" stroke-dasharray="6 3" rx="4" opacity="0"/>
                    <circle id="dMarker" cx="195" cy="145" r="5" fill="#B9362F" stroke="#FFF" stroke-width="1.5" opacity="0"/>
                    <circle id="dPulse" cx="195" cy="145" r="14" fill="none" stroke="#D94841" stroke-width="1.5" opacity="0"/>
                    <line id="dMaj" x1="150" y1="145" x2="240" y2="145" stroke="#D94841" stroke-width="2" stroke-dasharray="3" opacity="0"/>
                    <line id="dMin" x1="195" y1="105" x2="195" y2="185" stroke="#D94841" stroke-width="2" stroke-dasharray="3" opacity="0"/>
                    
                    <g id="dTag" transform="translate(235, 105)" opacity="0">
                        <rect x="0" y="0" width="150" height="26" rx="6" fill="rgba(17, 24, 39, 0.95)" stroke="#B9362F" stroke-width="1.5" />
                        <text x="8" y="17" fill="#FFFFFF" font-family="'Inter', sans-serif" font-size="11" font-weight="800">
                            STONE DETECTED: 8.19 mm
                        </text>
                    </g>
                </svg>
            </div>

            <div class="side-box">
                <div>
                    <div style="font-size: 0.78rem; font-weight: 800; color: #10B981; letter-spacing: 0.08em; text-transform: uppercase;">
                        STAGE: <span id="stageName">STEP 1 — CT IMAGE INGESTION</span>
                    </div>
                    <div style="font-size: 1.35rem; font-weight: 900; color: #FFFFFF; margin: 4px 0 16px 0;">
                        Automated AI Inference Sequence
                    </div>

                    <div class="panel-card" id="resPanel">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.10); padding-bottom: 8px; margin-bottom: 12px;">
                            <span style="font-size: 0.85rem; font-weight: 800; color: #FFFFFF;">AI ANALYSIS</span>
                            <span style="background: rgba(16, 185, 129, 0.2); color: #10B981; font-weight: 800; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;">Verified</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                            <div>
                                <div style="font-size: 0.7rem; color: #AAB4C0; font-weight: 700;">POTENTIAL STONE</div>
                                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;">Detected (1)</div>
                            </div>
                            <div>
                                <div style="font-size: 0.7rem; color: #AAB4C0; font-weight: 700;">CALCULATED SIZE</div>
                                <div style="font-size: 1.15rem; font-weight: 800; color: #FF6B63;">8.19 mm</div>
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 0.7rem; color: #AAB4C0; font-weight: 700;">MODEL CONFIDENCE</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #10B981;">92% Optimal</div>
                        </div>
                    </div>
                </div>

                <div>
                    <div class="ctrl-btns">
                        <button class="demo-btn active" onclick="execStep(1)">1. CT Image</button>
                        <button class="demo-btn" onclick="execStep(2)">2. Scan Laser</button>
                        <button class="demo-btn" onclick="execStep(4)">4. Detection Box</button>
                        <button class="demo-btn" onclick="execStep(6)">6. Calipers</button>
                        <button class="demo-btn" onclick="execStep(8)">8. AI Result</button>
                        <button class="demo-btn" onclick="runAuto()">🔄 Replay Sequence</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let timer = null;
            function execStep(step) {{
                const laser = document.getElementById('laser');
                const box = document.getElementById('dBox');
                const marker = document.getElementById('dMarker');
                const pulse = document.getElementById('dPulse');
                const maj = document.getElementById('dMaj');
                const min = document.getElementById('dMin');
                const tag = document.getElementById('dTag');
                const panel = document.getElementById('resPanel');
                const stName = document.getElementById('stageName');

                if (step === 1) {{
                    stName.innerText = "STEP 1 — CT IMAGE INGESTED";
                    laser.style.opacity = '0'; box.setAttribute('opacity', '0');
                    marker.setAttribute('opacity', '0'); pulse.setAttribute('opacity', '0');
                    maj.setAttribute('opacity', '0'); min.setAttribute('opacity', '0');
                    tag.setAttribute('opacity', '0'); panel.classList.remove('slide-in');
                }} else if (step === 2) {{
                    stName.innerText = "STEP 2 — LASER SCAN LINE SWEEPS";
                    laser.style.opacity = '1'; laser.style.top = '45%';
                }} else if (step === 4) {{
                    stName.innerText = "STEP 4 — DETECTION BOX & MARKER";
                    laser.style.opacity = '0';
                    box.setAttribute('opacity', '1'); marker.setAttribute('opacity', '1');
                    pulse.setAttribute('opacity', '1');
                }} else if (step === 6) {{
                    stName.innerText = "STEP 6 — CALIPER MEASUREMENT DRAWN";
                    box.setAttribute('opacity', '1'); marker.setAttribute('opacity', '1');
                    pulse.setAttribute('opacity', '1');
                    maj.setAttribute('opacity', '1'); min.setAttribute('opacity', '1');
                    tag.setAttribute('opacity', '1');
                }} else if (step >= 8) {{
                    stName.innerText = "STEP 8 — AI RESULT PANEL SLIDES IN";
                    box.setAttribute('opacity', '1'); marker.setAttribute('opacity', '1');
                    pulse.setAttribute('opacity', '1');
                    maj.setAttribute('opacity', '1'); min.setAttribute('opacity', '1');
                    tag.setAttribute('opacity', '1');
                    panel.classList.add('slide-in');
                }}
            }}
            function runAuto() {{
                clearInterval(timer);
                execStep(1);
                timer = setTimeout(() => {{
                    execStep(2);
                    timer = setTimeout(() => {{
                        execStep(4);
                        timer = setTimeout(() => {{
                            execStep(6);
                            timer = setTimeout(() => {{
                                execStep(8);
                            }}, 1200);
                        }}, 1200);
                    }}, 1200);
                }}, 800);
            }}
            runAuto();
        </script>
    </body>
    </html>
    """
    components.html(demo_html, height=440, scrolling=False)

    # =========================================================================
    # 9. FEATURES (6 PREMIUM CARDS)
    # =========================================================================
    st.markdown("""
    <div id="features" class="lp-section-header" style="margin-top: 48px;">
        <h2 class="lp-section-title">Built Around the <span>Complete Analysis Workflow</span></h2>
        <p class="lp-section-desc">
            Every capability designed specifically for rapid, reliable nephrolithiasis CT assessment.
        </p>
    </div>
    <div class="lp-cap-grid">
        <div class="lp-cap-card">
            <div class="lp-cap-icon">🎯</div>
            <div class="lp-cap-title">AI STONE DETECTION</div>
            <div class="lp-cap-desc">
                High-sensitivity YOLOv8s model localizes candidate calculi across complex soft tissue and bone attenuations.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">✂️</div>
            <div class="lp-cap-title">IMAGE SEGMENTATION</div>
            <div class="lp-cap-desc">
                Sub-pixel Otsu segmentation isolates true stone perimeters, preventing overestimation from beam hardening.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📐</div>
            <div class="lp-cap-title">STONE MEASUREMENT</div>
            <div class="lp-cap-desc">
                Calibrated physical calipers compute major axis, minor axis, and equivalent spherical diameter in millimeters.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📈</div>
            <div class="lp-cap-title">CONFIDENCE ANALYSIS</div>
            <div class="lp-cap-desc">
                Probabilistic confidence calibration indicates certainty, alerting clinicians to borderline or faint calcifications.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">🖼️</div>
            <div class="lp-cap-title">CT VISUALIZATION</div>
            <div class="lp-cap-desc">
                Multi-layer toggle overlays between raw CT, detection bounding boxes, binary masks, and caliper axes.
            </div>
        </div>
        <div class="lp-cap-card">
            <div class="lp-cap-icon">📄</div>
            <div class="lp-cap-title">STRUCTURED REPORTING</div>
            <div class="lp-cap-desc">
                Instant clinical summary text reports and tabular CSV export for documentation, audits, and research.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 10. WORKSTATION PREVIEW (REALISTIC UI PREVIEW + LAUNCH CTA)
    # =========================================================================
    st.markdown("""
    <div class="lp-section-header" style="margin-top: 48px;">
        <h2 class="lp-section-title">Your Complete <span>Analysis Workspace</span></h2>
        <p class="lp-section-desc">
            Upload a CT scan, visualize AI detections, review measurements, and explore structured analysis results in one workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ws_p_col1, ws_p_col2 = st.columns([1.1, 1], gap="large")
    with ws_p_col1:
        st.html(f"""
        <div style="background-color: #151C24; border-radius: 14px; border: 1.5px solid rgba(255, 255, 255, 0.10); border-top: 3.5px solid #B9362F; padding: 18px; box-shadow: 0 8px 30px rgba(0,0,0,0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="color: #F8FAFC; font-size: 0.85rem; font-weight: 800;">WORKSPACE INTERACTION PREVIEW</span>
                <span style="font-size: 0.72rem; background: rgba(185, 54, 47, 0.18); border: 1px solid rgba(255, 107, 99, 0.3); color: #FF6B63; font-weight: 800; padding: 3px 8px; border-radius: 8px;">Slice 034 / 128</span>
            </div>
            <img src="data:image/jpeg;base64,{s1_b64}" style="width: 100%; max-height: 230px; object-fit: contain; border-radius: 8px; margin-bottom: 12px;" alt="Workstation CT Preview" />
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center;">
                <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #AAB4C0; font-size: 0.68rem; font-weight: 700;">STONES</div>
                    <div style="color: #F8FAFC; font-size: 1.15rem; font-weight: 800;">3</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #AAB4C0; font-size: 0.68rem; font-weight: 700;">LARGEST</div>
                    <div style="color: #FF6B63; font-size: 1.15rem; font-weight: 800;">5.27 mm</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.06); padding: 8px; border-radius: 6px;">
                    <div style="color: #AAB4C0; font-size: 0.68rem; font-weight: 700;">CONFIDENCE</div>
                    <div style="color: #34D399; font-size: 1.15rem; font-weight: 800;">70%</div>
                </div>
            </div>
        </div>
        """)

    with ws_p_col2:
        st.markdown("""
        <div style="padding-top: 8px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(185, 54, 47, 0.18); border: 1px solid rgba(255, 107, 99, 0.3); color: #FF6B63; font-size: 0.78rem; font-weight: 800; padding: 4px 12px; border-radius: 6px; margin-bottom: 12px;">
                ● LIVE INTERACTIVE WORKSPACE
            </div>
            <div style="font-size: 1.45rem; font-weight: 900; color: #F8FAFC; margin-bottom: 12px; line-height: 1.25;">
                Full-Featured Diagnostic Workstation
            </div>
            <p style="font-size: 0.95rem; color: #AAB4C0; line-height: 1.6; margin-bottom: 20px;">
                Experience the real RenalScan analysis environment. Adjust model thresholds, toggle visualization layers, inspect sub-pixel contour masks, and export clinical reports.
            </p>
            <ul style="list-style: none; padding: 0; margin-bottom: 26px;">
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #F8FAFC; font-size: 0.9rem;">
                    <span style="color: #FF6B63; font-weight: 900;">✓</span> Multi-layer visualization overlays (YOLO, Otsu, Calipers)
                </li>
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #F8FAFC; font-size: 0.9rem;">
                    <span style="color: #FF6B63; font-weight: 900;">✓</span> Spatial anatomical kidney left/right distribution mapping
                </li>
                <li style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-weight: 600; color: #F8FAFC; font-size: 0.9rem;">
                    <span style="color: #FF6B63; font-weight: 900;">✓</span> One-click clinical report (.txt) &amp; measurement (.csv) downloads
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Launch Workstation →", key="ws_prev_launch_btn", use_container_width=True):
            go_to_workstation()

    # =========================================================================
    # 11. REPORT PREVIEW (ANIMATED A4 REPORT CARD)
    # =========================================================================
    st.markdown("""
    <div class="lp-section-header" style="margin-top: 48px;">
        <h2 class="lp-section-title">Turn Analysis Into a <span>Structured Report</span></h2>
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

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px; background: #FFF7F7; border: 1px solid #F1D5D5; border-radius: 10px; padding: 14px; text-align: center;">
                <div>
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">TOTAL STONES</div>
                    <div style="font-size: 1.25rem; font-weight: 900; color: #B9362F;">3 Detected</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">LARGEST SIZE</div>
                    <div style="font-size: 1.25rem; font-weight: 900; color: #B9362F;">5.27 mm</div>
                </div>
                <div>
                    <div style="font-size: 0.72rem; color: #6B7280; font-weight: 700;">CONFIDENCE</div>
                    <div style="font-size: 1.25rem; font-weight: 900; color: #10B981;">70% Mean</div>
                </div>
            </div>

            <div style="margin-bottom: 16px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #20283A; margin-bottom: 8px;">
                    DETECTED STONE FINDINGS
                </div>
                <div style="font-size: 0.84rem; color: #4B5563; line-height: 1.6;">
                    • <strong>Stone #1:</strong> 5.27 mm (Major: 5.4mm, Minor: 3.8mm) — 4–6mm Medium Band (Moderate passage likelihood)<br>
                    • <strong>Stone #2:</strong> 3.66 mm (Major: 4.1mm, Minor: 2.9mm) — &lt;4mm Small Band (High passage likelihood)<br>
                    • <strong>Stone #3:</strong> 2.16 mm (Major: 2.6mm, Minor: 1.8mm) — &lt;4mm Small Band (High passage likelihood)
                </div>
            </div>

            <div style="margin-bottom: 16px; background: #FCEDEC; border-radius: 8px; padding: 10px 14px;">
                <div style="font-size: 0.8rem; font-weight: 800; color: #8F2924; margin-bottom: 4px;">
                    AI ANALYSIS IMPRESSION
                </div>
                <div style="font-size: 0.82rem; color: #4B5563; line-height: 1.5;">
                    Axial non-contrast CT abdominal scan demonstrates three hyperdense calcifications within the renal parenchyma. Moderate passage likelihood for primary calculus with expectant medical therapy.
                </div>
            </div>

            <div style="border-top: 1px dashed #F1D5D5; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.76rem; color: #9CA3AF;">
                <span>Verified by RenalScan AI Model v2.0</span>
                <span>Assumed Spacing: 0.70 mm/px</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with rep_col2:
        st.markdown("""
        <div style="padding-top: 14px;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(185, 54, 47, 0.18); border: 1px solid rgba(255, 107, 99, 0.3); color: #FF6B63; font-size: 0.78rem; font-weight: 800; padding: 4px 12px; border-radius: 6px; margin-bottom: 12px;">
                📄 ONE-CLICK EXPORT
            </div>
            <div style="font-size: 1.45rem; font-weight: 900; color: #F8FAFC; margin-bottom: 12px; line-height: 1.25;">
                From Raw CT Slices to Diagnostic Reports
            </div>
            <p style="font-size: 0.95rem; color: #AAB4C0; line-height: 1.6; margin-bottom: 22px;">
                Review the complete analysis workflow in the interactive workstation and generate audit-ready clinical exports.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Analysis Workflow →", key="rep_explore_btn", use_container_width=True):
            go_to_workstation()

    # =========================================================================
    # 12. KIDNEY HEALTH (4 INTERACTIVE CARDS)
    # =========================================================================
    st.html("""
    <div id="kidney-health" class="lp-section-header" style="margin-top: 50px;">
        <h2 class="lp-section-title">Know Your <span>Kidneys</span></h2>
        <p class="lp-section-desc">
            Essential nephrolithiasis knowledge, symptoms, risk factors, and evidence-based preventive guidance.
        </p>
    </div>
    <div class="lp-health-grid">
        <div class="lp-health-card">
            <div>
                <div class="lp-health-icon">🫘</div>
                <div class="lp-health-title">KIDNEY STONES</div>
                <div class="lp-health-desc">
                    Hard mineral and salt deposits (calcium oxalate, uric acid, struvite, cystine) that crystallize inside the renal pelvis and calyces when urine becomes supersaturated.
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.8rem; font-weight: 700; color: #FF6B63;">
                Learn Formation Path →
            </div>
        </div>
        <div class="lp-health-card">
            <div>
                <div class="lp-health-icon">⚡</div>
                <div class="lp-health-title">SYMPTOMS</div>
                <div class="lp-health-desc">
                    Severe radiating flank and lower abdominal pain, visible hematuria (blood in urine), painful dysuria, urinary urgency, chills, and intermittent nausea.
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.8rem; font-weight: 700; color: #FF6B63;">
                Triage Indicators →
            </div>
        </div>
        <div class="lp-health-card">
            <div>
                <div class="lp-health-icon">⚠️</div>
                <div class="lp-health-title">RISK FACTORS</div>
                <div class="lp-health-desc">
                    Chronic dehydration, excessive dietary sodium and animal protein intake, familial history, metabolic disorders, hyperparathyroidism, and obesity.
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.8rem; font-weight: 700; color: #FF6B63;">
                Etiology Factors →
            </div>
        </div>
        <div class="lp-health-card">
            <div>
                <div class="lp-health-icon">💧</div>
                <div class="lp-health-title">PREVENTION</div>
                <div class="lp-health-desc">
                    Consistently drinking sufficient fluids to generate &gt;2.5L daily urine volume, reducing dietary sodium, and maintaining adequate dietary calcium intake.
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 0.8rem; font-weight: 700; color: #FF6B63;">
                Lifestyle Guidance →
            </div>
        </div>
    </div>
    """)

    # =========================================================================
    # 13. RESPONSIBLE AI (ANIMATED PULSING MEDICAL SHIELD)
    # =========================================================================
    st.html("""
    <div id="about" class="lp-shield-section" style="margin-top: 48px;">
        <div class="lp-shield-icon-box">🛡️</div>
        <div>
            <div style="font-size: 1.25rem; font-weight: 900; color: #F8FAFC; margin-bottom: 6px;">
                AI-Assisted. Human-Centered.
            </div>
            <div style="font-size: 0.92rem; color: #AAB4C0; line-height: 1.65;">
                RenalScan provides AI-assisted image analysis to support the interpretation of CT images. AI-generated findings should be reviewed by qualified healthcare professionals. This prototype is designed for computer vision research and technical demonstration.
            </div>
        </div>
    </div>
    """)

    # =========================================================================
    # 14. FINAL CTA (FULL WIDTH DEEP RED GRADIENT CONTAINER)
    # =========================================================================
    st.html("""
    <div class="lp-final-cta-wrapper">
        <h2 class="lp-final-cta-title">Ready to Explore RenalScan?</h2>
        <p class="lp-final-cta-sub">
            Experience AI-assisted kidney stone analysis from CT images. Fast, automated, reproducible.
        </p>
        <div style="display: flex; justify-content: center; gap: 16px; align-items: center; margin-top: 28px; flex-wrap: wrap;">
            <a href="workstation" target="_self" class="rs-cta-white-btn">
                Start Analysis →
            </a>
            <a href="#how-it-works" style="color: #FEE2E2; font-size: 0.95rem; text-decoration: underline; font-weight: 700; padding: 10px 18px;">
                Explore How It Works ↑
            </a>
        </div>
    </div>
    """)

    # =========================================================================
    # 15. FOOTER (MINIMAL, PREMIUM DARK CHARCOAL)
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
                    AI-assisted kidney stone analysis from abdominal CT images. Built for technical portfolio evaluation and medical computer vision research.
                </div>
            </div>
            <div class="lp-footer-col">
                <h4>Navigation</h4>
                <ul>
                    <li><a href="#" style="color: #9CA3AF; text-decoration: none;">Home</a></li>
                    <li><a href="#how-it-works" style="color: #9CA3AF; text-decoration: none;">How It Works</a></li>
                    <li><a href="#why-renalscan" style="color: #9CA3AF; text-decoration: none;">Why RenalScan</a></li>
                    <li><a href="#demo" style="color: #9CA3AF; text-decoration: none;">CT Demo</a></li>
                </ul>
            </div>
            <div class="lp-footer-col">
                <h4>Resources</h4>
                <ul>
                    <li><a href="#features" style="color: #9CA3AF; text-decoration: none;">Capabilities</a></li>
                    <li><a href="#kidney-health" style="color: #9CA3AF; text-decoration: none;">Kidney Health</a></li>
                    <li><a href="#about" style="color: #9CA3AF; text-decoration: none;">Responsible AI</a></li>
                    <li><a href="/workstation" style="color: #9CA3AF; text-decoration: none;">Workstation</a></li>
                </ul>
            </div>
        </div>
        <div class="lp-footer-bottom">
            © 2026 RenalScan. AI-assisted analysis. Not a substitute for professional medical advice.
        </div>
    </div>
    """, unsafe_allow_html=True)
