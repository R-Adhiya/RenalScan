"""
styles.py - Global CSS Design System for RenalScan (Medical Red + White)
Primary Brand Color: #B9362F
Primary Accent: #D94841
Dark Red: #8F2924
Light Red: #FCEDEC
Background Canvas: #FFFFFF
Text Primary: #20283A
Text Secondary: #6B7280
Border: #F1D5D5
"""

import streamlit as st

def inject_global_css():
    st.markdown("""
<style>
    /* Inter Font Typography */
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
        color: #20283A;
    }

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        max-width: 1380px;
        margin: 0 auto;
    }

    /* Primary Red Button System */
    .stButton > button {
        background-color: #B9362F !important;
        color: #FFFFFF !important;
        border: 1px solid #B9362F !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 9px 22px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(185, 54, 47, 0.18) !important;
    }
    .stButton > button:hover {
        background-color: #8F2924 !important;
        border-color: #8F2924 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(185, 54, 47, 0.28) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Secondary White Button Style */
    .rs-btn-outline {
        display: inline-block;
        background-color: #FFFFFF;
        color: #B9362F;
        border: 1.5px solid #B9362F;
        border-radius: 8px;
        padding: 9px 20px;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.2s ease;
        text-align: center;
        cursor: pointer;
    }
    .rs-btn-outline:hover {
        background-color: #FCEDEC;
        color: #8F2924;
        border-color: #8F2924;
        transform: translateY(-1px);
    }

    /* Navbar */
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
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.04);
    }
    .lp-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .lp-logo-badge {
        width: 38px;
        height: 38px;
        background: #B9362F;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 1.25rem;
        box-shadow: 0 2px 8px rgba(185, 54, 47, 0.3);
    }
    .lp-brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #20283A;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .lp-brand-accent {
        color: #B9362F;
    }
    .lp-brand-sub {
        font-size: 0.76rem;
        color: #6B7280;
        font-weight: 500;
    }
    .lp-nav-links {
        display: flex;
        align-items: center;
        gap: 26px;
    }
    .lp-nav-item {
        font-size: 0.92rem;
        font-weight: 600;
        color: #4B5563;
        text-decoration: none;
        transition: color 0.2s;
    }
    .lp-nav-item:hover {
        color: #B9362F;
    }

    /* Hero Section */
    .lp-hero-wrapper {
        background: radial-gradient(circle at 85% 30%, #FCEDEC 0%, #FFFFFF 65%);
        border: 1px solid #F1D5D5;
        border-radius: 20px;
        padding: 44px 48px;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(185, 54, 47, 0.04);
        position: relative;
    }
    .lp-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #FCEDEC;
        color: #B9362F;
        border: 1px solid #F1D5D5;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 20px;
        padding: 5px 14px;
        margin-bottom: 16px;
    }
    .lp-hero-heading {
        font-size: 2.85rem;
        font-weight: 800;
        color: #20283A;
        line-height: 1.18;
        letter-spacing: -0.025em;
        margin-bottom: 16px;
    }
    .lp-hero-heading span {
        color: #B9362F;
    }
    .lp-hero-desc {
        font-size: 1.08rem;
        color: #4B5563;
        line-height: 1.6;
        margin-bottom: 24px;
        max-width: 580px;
    }
    .lp-trust-line {
        font-size: 0.84rem;
        color: #6B7280;
        margin-top: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
    }

    /* Sophisticated CT Preview in Hero */
    .lp-ct-preview-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-top: 3px solid #B9362F;
        border-radius: 16px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.28);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .lp-floating-card-1 {
        position: absolute;
        bottom: 24px;
        left: 20px;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(8px);
        border: 1px solid #F1D5D5;
        border-left: 4px solid #B9362F;
        border-radius: 10px;
        padding: 10px 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
        animation: floatCard1 3.5s ease-in-out infinite;
        z-index: 10;
    }
    .lp-floating-card-2 {
        position: absolute;
        top: 24px;
        right: 20px;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(8px);
        border: 1px solid #F1D5D5;
        border-left: 4px solid #10B981;
        border-radius: 10px;
        padding: 8px 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
        animation: floatCard2 4s ease-in-out infinite;
        z-index: 10;
    }
    .lp-floating-card-3 {
        position: absolute;
        top: 80px;
        right: 20px;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(8px);
        border: 1px solid #F1D5D5;
        border-left: 4px solid #D94841;
        border-radius: 10px;
        padding: 8px 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
        animation: floatCard1 4.5s ease-in-out infinite;
        z-index: 10;
    }
    @keyframes floatCard1 {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-7px); }
    }
    @keyframes floatCard2 {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(6px); }
    }

    /* Trust / Value Bar */
    .lp-trust-strip {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 14px 24px;
        margin-bottom: 44px;
        display: flex;
        align-items: center;
        justify-content: space-around;
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.03);
    }
    .lp-trust-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.82rem;
        font-weight: 800;
        color: #20283A;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .lp-trust-icon {
        color: #B9362F;
        font-size: 1.15rem;
    }
    .lp-trust-sep {
        color: #F1D5D5;
        font-size: 1.1rem;
    }

    /* Section Headings */
    .lp-section-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .lp-section-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #20283A;
        letter-spacing: -0.025em;
        margin-bottom: 8px;
    }
    .lp-section-title span {
        color: #B9362F;
    }
    .lp-section-desc {
        font-size: 1rem;
        color: #6B7280;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.55;
    }

    /* Split Section: What is RenalScan */
    .lp-split-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 18px;
        padding: 36px 40px;
        margin-bottom: 48px;
        box-shadow: 0 4px 18px rgba(185, 54, 47, 0.04);
    }
    .lp-editorial-step {
        display: flex;
        gap: 20px;
        margin-bottom: 26px;
    }
    .lp-editorial-num {
        font-size: 2rem;
        font-weight: 800;
        color: #B9362F;
        line-height: 1;
        min-width: 44px;
    }
    .lp-editorial-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 4px;
    }
    .lp-editorial-desc {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.5;
    }

    /* 6-Step Horizontal Process */
    .lp-timeline-wrapper {
        background-color: #FCEDEC;
        border: 1px solid #F1D5D5;
        border-radius: 16px;
        padding: 32px 24px;
        margin-bottom: 48px;
    }
    .lp-timeline-steps {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
    }
    .lp-timeline-line {
        position: absolute;
        top: 22px;
        left: 6%;
        right: 6%;
        height: 2px;
        background-color: #F1D5D5;
        z-index: 1;
    }
    .lp-timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        width: 15%;
        position: relative;
        z-index: 2;
    }
    .lp-step-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background-color: #B9362F;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 3px 10px rgba(185, 54, 47, 0.25);
        margin-bottom: 10px;
    }
    .lp-step-title {
        font-size: 0.88rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 3px;
    }
    .lp-step-desc {
        font-size: 0.74rem;
        color: #6B7280;
        line-height: 1.35;
    }

    /* Capabilities 2x3 Grid */
    .lp-cap-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 48px;
    }
    .lp-cap-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .lp-cap-card:hover {
        transform: translateY(-3px);
        border-color: #B9362F;
        box-shadow: 0 6px 18px rgba(185, 54, 47, 0.09);
    }
    .lp-cap-icon {
        width: 38px;
        height: 38px;
        background-color: #FCEDEC;
        color: #B9362F;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 14px;
    }
    .lp-cap-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 6px;
    }
    .lp-cap-desc {
        font-size: 0.86rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* Workstation Preview Box */
    .lp-preview-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 18px;
        padding: 36px 40px;
        margin-bottom: 48px;
        box-shadow: 0 4px 20px rgba(185, 54, 47, 0.04);
    }

    /* Analysis Report Showcase Card */
    .lp-report-card {
        background: #FFFFFF;
        border: 1.5px solid #F1D5D5;
        border-radius: 16px;
        padding: 26px;
        box-shadow: 0 6px 24px rgba(185, 54, 47, 0.06);
    }
    .lp-report-header {
        border-bottom: 2px solid #B9362F;
        padding-bottom: 12px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    /* Kidney Health 4 Cards */
    .lp-health-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 48px;
    }
    .lp-health-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 2px 8px rgba(185, 54, 47, 0.03);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .lp-health-card:hover {
        transform: translateY(-2px);
        border-color: #B9362F;
    }

    /* Responsible AI Banner */
    .lp-safety-banner {
        background-color: #FCEDEC;
        border: 1px solid #F1D5D5;
        border-left: 4px solid #B9362F;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 48px;
        display: flex;
        align-items: flex-start;
        gap: 18px;
    }
    .lp-safety-icon {
        color: #B9362F;
        font-size: 1.7rem;
        line-height: 1;
        margin-top: 2px;
    }

    /* Final CTA - Deep Red Container */
    .lp-final-cta-wrapper {
        background: linear-gradient(135deg, #8F2924 0%, #B9362F 100%);
        border-radius: 20px;
        padding: 48px 40px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 48px;
        box-shadow: 0 8px 30px rgba(143, 41, 36, 0.3);
    }
    .lp-final-cta-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    .lp-final-cta-sub {
        font-size: 1.05rem;
        color: #FEE2E2;
        max-width: 600px;
        margin: 0 auto 28px auto;
        line-height: 1.6;
    }

    /* Footer */
    .lp-footer {
        background-color: #111827;
        color: #E5E7EB;
        border-top: 3px solid #B9362F;
        border-radius: 16px 16px 0 0;
        padding: 40px 36px 26px 36px;
    }
    .lp-footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 36px;
        margin-bottom: 28px;
    }
    .lp-footer-col h4 {
        font-size: 0.92rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 14px;
        letter-spacing: 0.04em;
    }
    .lp-footer-col ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .lp-footer-col li {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-bottom: 8px;
    }
    .lp-footer-bottom {
        border-top: 1px solid #1F2937;
        padding-top: 18px;
        text-align: center;
        font-size: 0.78rem;
        color: #6B7280;
    }

    /* Workstation Specific CSS */
    .rs-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.03);
    }
    .rs-card-title {
        font-size: 1rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .rs-card-title-icon {
        color: #B9362F;
    }
    .rs-summary-card {
        background-color: #FCEDEC;
        border: 1px solid #F1D5D5;
        border-left: 5px solid #B9362F;
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
        border-top: 3px solid #B9362F;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(185, 54, 47, 0.04);
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
        color: #B9362F;
    }
    .rs-stone-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(185, 54, 47, 0.03);
    }
    .rs-stone-card:hover {
        border-color: #B9362F;
    }
    .rs-ct-header {
        background-color: #111827;
        border-radius: 14px 14px 0 0;
        border: 1px solid #1F2937;
        border-top: 3px solid #B9362F;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .rs-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        background-color: #FCEDEC;
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
        color: #20283A;
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
        color: #20283A;
        font-weight: 600;
    }
    .rs-meas-val-cell {
        background-color: #FCEDEC;
        color: #B9362F !important;
        font-weight: 800 !important;
        border-radius: 6px;
    }
    .rs-kidney-box {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.03);
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
        border: 2px solid #D94841;
        border-radius: 45% 55% 50% 50% / 60% 40% 60% 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        font-weight: 800;
        color: #B9362F;
        font-size: 0.85rem;
    }
    .rs-stone-pulse-dot {
        width: 14px;
        height: 14px;
        background-color: #B9362F;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 8px #D94841;
        animation: pulseRedDot 1.5s infinite;
    }
    @keyframes pulseRedDot {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }
</style>
""", unsafe_allow_html=True)
