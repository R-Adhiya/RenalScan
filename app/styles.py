"""
styles.py - Global CSS Design System for RenalScan (Medical Red + White)
Official Brand Identity:
  Primary Brand Color: #B9362F
  Primary Accent: #D94841
  Dark Red: #8F2924
  Light Red: #FCEDEC
  Background Canvas: #FFFFFF
  Secondary Surface: #FFF7F7
  Text Primary: #20283A
  Text Secondary: #6B7280
  Border: #F1D5D5
"""

import streamlit as st

def inject_global_css():
    st.markdown("""
<style>
    /* Inter Font Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        scroll-behavior: smooth;
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
        padding-bottom: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Primary Red Button System */
    .stButton > button {
        background-color: #B9362F !important;
        color: #FFFFFF !important;
        border: 1.5px solid #B9362F !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
        padding: 10px 24px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 12px rgba(185, 54, 47, 0.22) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background-color: #8F2924 !important;
        border-color: #8F2924 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 22px rgba(185, 54, 47, 0.32) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.99) !important;
    }

    /* Secondary White Button Style */
    .rs-btn-outline {
        display: inline-block;
        background-color: #FFFFFF;
        color: #B9362F;
        border: 1.5px solid #B9362F;
        border-radius: 9px;
        padding: 9px 22px;
        font-weight: 700;
        font-size: 0.92rem;
        text-decoration: none;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        text-align: center;
        cursor: pointer;
    }
    .rs-btn-outline:hover {
        background-color: #FCEDEC;
        color: #8F2924;
        border-color: #8F2924;
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(185, 54, 47, 0.14);
    }

    /* Primary HTML Link Button (for zero-latency routing) */
    .rs-btn-primary-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #B9362F;
        color: #FFFFFF !important;
        border: 1.5px solid #B9362F;
        border-radius: 9px;
        padding: 10px 24px;
        font-weight: 700;
        font-size: 0.93rem;
        text-decoration: none;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 14px rgba(185, 54, 47, 0.24);
        cursor: pointer;
    }
    .rs-btn-primary-link:hover {
        background-color: #8F2924;
        border-color: #8F2924;
        color: #FFFFFF !important;
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 22px rgba(185, 54, 47, 0.34);
    }

    /* Sticky Navbar */
    .lp-navbar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1.5px solid #F1D5D5;
        padding: 12px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 14px rgba(185, 54, 47, 0.05);
        transition: all 0.3s ease;
    }
    .lp-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
    }
    .lp-logo-badge {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #B9362F 0%, #D94841 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 1.3rem;
        box-shadow: 0 3px 10px rgba(185, 54, 47, 0.32);
        transition: transform 0.2s ease;
    }
    .lp-logo-badge:hover {
        transform: scale(1.05);
    }
    .lp-brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #20283A;
        letter-spacing: -0.025em;
        line-height: 1.1;
    }
    .lp-brand-accent {
        color: #B9362F;
    }
    .lp-brand-sub {
        font-size: 0.76rem;
        color: #6B7280;
        font-weight: 600;
        letter-spacing: 0.02em;
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
        transition: color 0.2s ease;
        position: relative;
    }
    .lp-nav-item:hover {
        color: #B9362F;
    }
    .lp-nav-item::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 0%;
        height: 2px;
        background-color: #B9362F;
        transition: width 0.2s ease;
    }
    .lp-nav-item:hover::after {
        width: 100%;
    }

    /* Cinematic Hero Wrapper with Faint Medical Grid */
    .lp-hero-wrapper {
        background-color: #FFFFFF;
        background-image: 
            radial-gradient(circle at 82% 24%, rgba(252, 237, 236, 0.95) 0%, rgba(255, 255, 255, 0) 58%),
            linear-gradient(to right, rgba(241, 213, 213, 0.22) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(241, 213, 213, 0.22) 1px, transparent 1px);
        background-size: 100% 100%, 36px 36px, 36px 36px;
        border: 1.5px solid #F1D5D5;
        border-radius: 24px;
        padding: 52px 50px 48px 50px;
        margin-bottom: 32px;
        box-shadow: 0 8px 32px rgba(185, 54, 47, 0.05);
        position: relative;
        overflow: hidden;
    }

    /* Small Animated Hero Badge */
    .lp-badge-animated {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #FCEDEC;
        color: #8F2924;
        border: 1px solid #F1D5D5;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 20px;
        padding: 6px 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(185, 54, 47, 0.08);
    }
    .lp-badge-dot {
        width: 8px;
        height: 8px;
        background-color: #B9362F;
        border-radius: 50%;
        display: inline-block;
        animation: pulseRedDot 1.8s infinite ease-in-out;
    }

    .lp-hero-heading {
        font-size: 3.2rem;
        font-weight: 900;
        color: #20283A;
        line-height: 1.15;
        letter-spacing: -0.03em;
        margin-bottom: 18px;
    }
    .lp-hero-heading .red-accent {
        color: #B9362F;
        background: linear-gradient(135deg, #B9362F 0%, #D94841 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .lp-hero-desc {
        font-size: 1.12rem;
        color: #4B5563;
        line-height: 1.65;
        margin-bottom: 28px;
        max-width: 580px;
    }

    /* Hero Floating CT Visualization Container */
    .lp-ct-float-container {
        position: relative;
        background: #0F131C;
        border: 1.5px solid #1F2937;
        border-top: 3.5px solid #B9362F;
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 16px 44px rgba(0, 0, 0, 0.32);
        animation: floatHeroCard 6s ease-in-out infinite;
        overflow: hidden;
    }
    @keyframes floatHeroCard {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-8px) rotate(0.4deg); }
    }

    /* Animated Red Scan Line */
    .lp-laser-scanner {
        position: absolute;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #E53935 30%, #FFFFFF 50%, #E53935 70%, transparent 100%);
        box-shadow: 0 0 14px #E53935, 0 0 28px rgba(229, 57, 53, 0.6);
        animation: heroScanLoop 3.6s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
        z-index: 8;
        pointer-events: none;
    }
    @keyframes heroScanLoop {
        0% { top: 6%; opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { top: 92%; opacity: 0; }
    }

    /* Floating White Hero Cards */
    .lp-float-card {
        position: absolute;
        background: rgba(255, 255, 255, 0.97);
        backdrop-filter: blur(10px);
        border: 1px solid #F1D5D5;
        border-radius: 12px;
        padding: 10px 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.16);
        z-index: 10;
        pointer-events: none;
    }
    .lp-float-card-1 {
        bottom: 22px;
        left: 20px;
        border-left: 4px solid #B9362F;
        animation: floatCard1 4s ease-in-out infinite;
    }
    .lp-float-card-2 {
        top: 24px;
        right: 20px;
        border-left: 4px solid #10B981;
        animation: floatCard2 4.6s ease-in-out infinite;
    }
    .lp-float-card-3 {
        top: 90px;
        right: 20px;
        border-left: 4px solid #D94841;
        animation: floatCard1 5.2s ease-in-out infinite;
    }
    @keyframes floatCard1 {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    @keyframes floatCard2 {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(6px); }
    }

    /* Detection Pulse Marker */
    .lp-stone-marker-box {
        position: absolute;
        border: 2px dashed #D94841;
        background: rgba(185, 54, 47, 0.22);
        border-radius: 6px;
        animation: boxGlow 2.5s ease-in-out infinite;
    }
    @keyframes boxGlow {
        0%, 100% { box-shadow: 0 0 6px rgba(217, 72, 65, 0.3); border-color: #D94841; }
        50% { box-shadow: 0 0 16px rgba(217, 72, 65, 0.7); border-color: #B9362F; }
    }

    /* Scroll Indicator */
    .lp-scroll-ind-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 14px;
        cursor: pointer;
    }
    .lp-scroll-ind-text {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #9CA3AF;
        margin-bottom: 4px;
    }
    .lp-scroll-ind-arrow {
        font-size: 1.1rem;
        color: #B9362F;
        animation: bounceDown 1.8s infinite ease-in-out;
    }
    @keyframes bounceDown {
        0%, 100% { transform: translateY(0); opacity: 0.6; }
        50% { transform: translateY(6px); opacity: 1; }
    }

    /* Trust Strip */
    .lp-trust-strip {
        background-color: #FFFFFF;
        border: 1.5px solid #F1D5D5;
        border-radius: 16px;
        padding: 16px 28px;
        margin-bottom: 50px;
        display: flex;
        align-items: center;
        justify-content: space-around;
        box-shadow: 0 3px 14px rgba(185, 54, 47, 0.04);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .lp-trust-strip:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(185, 54, 47, 0.08);
    }
    .lp-trust-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.84rem;
        font-weight: 800;
        color: #20283A;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .lp-trust-icon {
        color: #B9362F;
        font-size: 1.25rem;
    }
    .lp-trust-sep {
        color: #F1D5D5;
        font-size: 1.2rem;
    }

    /* Section Headers */
    .lp-section-header {
        text-align: center;
        margin-bottom: 34px;
    }
    .lp-section-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #20283A;
        letter-spacing: -0.025em;
        margin-bottom: 10px;
    }
    .lp-section-title span {
        color: #B9362F;
    }
    .lp-section-desc {
        font-size: 1.05rem;
        color: #6B7280;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Numbered Split Feature Cards */
    .lp-feature-card {
        background: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-left: 4px solid #F1D5D5;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        display: flex;
        gap: 20px;
        align-items: flex-start;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .lp-feature-card:hover {
        border-left-color: #B9362F;
        border-color: #B9362F;
        transform: translateX(6px);
        box-shadow: 0 6px 18px rgba(185, 54, 47, 0.08);
    }
    .lp-feature-num {
        font-size: 1.9rem;
        font-weight: 900;
        color: #B9362F;
        line-height: 1;
        min-width: 44px;
    }
    .lp-feature-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 4px;
    }
    .lp-feature-desc {
        font-size: 0.9rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* Interactive Pipeline (Horizontal on Desktop, Responsive) */
    .lp-pipeline-container {
        background-color: #FCEDEC;
        border: 1.5px solid #F1D5D5;
        border-radius: 20px;
        padding: 34px 28px;
        margin-bottom: 52px;
        box-shadow: 0 4px 20px rgba(185, 54, 47, 0.04);
    }
    .lp-pipeline-steps {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
    }
    .lp-pipeline-bar {
        position: absolute;
        top: 24px;
        left: 6%;
        right: 6%;
        height: 3px;
        background: #F1D5D5;
        z-index: 1;
    }
    .lp-pipe-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        width: 15%;
        position: relative;
        z-index: 2;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    .lp-pipe-step:hover {
        transform: translateY(-4px);
    }
    .lp-pipe-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background-color: #FFFFFF;
        border: 2.5px solid #B9362F;
        color: #B9362F;
        font-weight: 800;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(185, 54, 47, 0.16);
        margin-bottom: 12px;
        transition: all 0.25s ease;
    }
    .lp-pipe-step:hover .lp-pipe-circle {
        background-color: #B9362F;
        color: #FFFFFF;
        box-shadow: 0 6px 18px rgba(185, 54, 47, 0.35);
    }
    .lp-pipe-label {
        font-size: 0.9rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 4px;
    }
    .lp-pipe-sub {
        font-size: 0.75rem;
        color: #6B7280;
        line-height: 1.35;
    }

    /* Big CT Scan Showcase (Deep Charcoal #16181D) */
    .lp-dark-showcase {
        background-color: #16181D;
        border: 1px solid #2A2F3B;
        border-top: 4px solid #B9362F;
        border-radius: 24px;
        padding: 48px 40px;
        margin-bottom: 50px;
        color: #FFFFFF;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.45);
        position: relative;
        overflow: hidden;
    }
    .lp-dark-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: -0.025em;
        margin-bottom: 8px;
    }
    .lp-dark-sub {
        font-size: 1.05rem;
        color: #9CA3AF;
        max-width: 640px;
        margin-bottom: 32px;
    }

    /* Live Analysis UI Mockup Cards */
    .lp-live-metric-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-top: 3.5px solid #B9362F;
        border-radius: 14px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 3px 12px rgba(185, 54, 47, 0.05);
        transition: transform 0.2s ease;
    }
    .lp-live-metric-card:hover {
        transform: translateY(-2px);
    }

    /* Floating A4 Report Showcase */
    .lp-a4-report {
        background: #FFFFFF;
        border: 1.5px solid #F1D5D5;
        border-radius: 18px;
        padding: 32px 36px;
        box-shadow: 0 14px 40px rgba(185, 54, 47, 0.08), 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .lp-a4-report:hover {
        transform: translateY(-4px) perspective(1000px) rotateX(1deg);
        box-shadow: 0 20px 50px rgba(185, 54, 47, 0.12);
    }

    /* Kidney Health 4 Cards Grid */
    .lp-health-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 50px;
    }
    .lp-health-card {
        background-color: #FFFFFF;
        border: 1px solid #F1D5D5;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 3px 12px rgba(185, 54, 47, 0.03);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .lp-health-card:hover {
        transform: translateY(-4px);
        border-color: #B9362F;
        box-shadow: 0 8px 24px rgba(185, 54, 47, 0.1);
    }
    .lp-health-icon {
        width: 44px;
        height: 44px;
        background-color: #FCEDEC;
        color: #B9362F;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        margin-bottom: 16px;
    }
    .lp-health-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #20283A;
        margin-bottom: 8px;
    }
    .lp-health-desc {
        font-size: 0.88rem;
        color: #4B5563;
        line-height: 1.55;
    }

    /* Responsible AI Shield Section */
    .lp-shield-section {
        background-color: #FCEDEC;
        border: 1.5px solid #F1D5D5;
        border-left: 5px solid #B9362F;
        border-radius: 18px;
        padding: 30px 36px;
        margin-bottom: 50px;
        display: flex;
        align-items: center;
        gap: 24px;
        box-shadow: 0 4px 16px rgba(185, 54, 47, 0.04);
    }
    .lp-shield-icon-box {
        width: 64px;
        height: 64px;
        min-width: 64px;
        background-color: #FFFFFF;
        border: 2px solid #F1D5D5;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 4px 14px rgba(185, 54, 47, 0.12);
        animation: pulseShield 3s infinite ease-in-out;
    }
    @keyframes pulseShield {
        0%, 100% { box-shadow: 0 0 10px rgba(185, 54, 47, 0.15); transform: scale(1); }
        50% { box-shadow: 0 0 22px rgba(185, 54, 47, 0.35); transform: scale(1.04); }
    }

    /* Final Red CTA */
    .lp-final-cta-wrapper {
        background: linear-gradient(135deg, #8F2924 0%, #B9362F 60%, #D94841 100%);
        border-radius: 24px;
        padding: 56px 44px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 50px;
        box-shadow: 0 14px 40px rgba(143, 41, 36, 0.35);
        position: relative;
        overflow: hidden;
    }
    .lp-final-cta-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 14px;
        letter-spacing: -0.025em;
    }
    .lp-final-cta-sub {
        font-size: 1.15rem;
        color: #FEE2E2;
        max-width: 640px;
        margin: 0 auto 32px auto;
        line-height: 1.6;
    }

    /* Footer */
    .lp-footer {
        background-color: #111827;
        color: #E5E7EB;
        border-top: 3.5px solid #B9362F;
        border-radius: 20px 20px 0 0;
        padding: 44px 40px 28px 40px;
    }
    .lp-footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 40px;
        margin-bottom: 30px;
    }
    .lp-footer-col h4 {
        font-size: 0.95rem;
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
        font-size: 0.88rem;
        color: #9CA3AF;
        margin-bottom: 9px;
    }
    .lp-footer-bottom {
        border-top: 1px solid #1F2937;
        padding-top: 20px;
        text-align: center;
        font-size: 0.8rem;
        color: #6B7280;
    }

    /* Keyframes */
    @keyframes pulseRedDot {
        0%, 100% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
    }

    /* Accessibility: Respect Reduced Motion */
    @media (prefers-reduced-motion: reduce) {
        *, ::before, ::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }

    /* Responsive Queries */
    @media (max-width: 900px) {
        .lp-health-grid { grid-template-columns: 1fr 1fr; }
        .lp-footer-grid { grid-template-columns: 1fr; gap: 24px; }
        .lp-hero-heading { font-size: 2.4rem; }
    }
    @media (max-width: 600px) {
        .lp-health-grid { grid-template-columns: 1fr; }
        .lp-trust-strip { flex-direction: column; gap: 14px; }
        .lp-trust-sep { display: none; }
        .lp-hero-wrapper { padding: 30px 20px; }
        .lp-hero-heading { font-size: 2rem; }
    }
</style>
""", unsafe_allow_html=True)
