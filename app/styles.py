"""
styles.py - Global CSS Design System for RenalScan (Dark Medical AI Theme)
Official Brand Identity:
  Primary Brand Color: #B9362F
  Bright Red: #D94841
  Light Red Accent: #FF6B63
  Dark Red: #8F2924
  Main Background: #0D1117
  Secondary Section: #111820
  Card Background: #151C24
  Elevated Card: #1B232D
  Text Primary: #F8FAFC
  Text Secondary: #AAB4C0
  Border: rgba(255, 255, 255, 0.10)
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

    /* Global Dark Canvas */
    .stApp {
        background-color: #0D1117 !important;
        color: #F8FAFC !important;
    }

    .block-container {
        padding-top: 0.25rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Primary Red Button System */
    .stButton > button {
        background-color: #B9362F !important;
        color: #FFFFFF !important;
        border: 1px solid #D94841 !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
        padding: 10px 24px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 16px rgba(185, 54, 47, 0.35) !important;
        cursor: pointer !important;
    }
    .stButton > button:hover {
        background-color: #D94841 !important;
        border-color: #FF6B63 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 26px rgba(217, 72, 65, 0.5) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.99) !important;
    }

    /* Secondary Transparent / Dark Outline Button Style */
    .rs-btn-outline {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: rgba(255, 255, 255, 0.04);
        color: #F8FAFC !important;
        border: 1.5px solid #B9362F;
        border-radius: 9px;
        padding: 10px 22px;
        font-weight: 700;
        font-size: 0.92rem;
        text-decoration: none;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        text-align: center;
        cursor: pointer;
    }
    .rs-btn-outline:hover {
        background-color: rgba(185, 54, 47, 0.18);
        color: #FF6B63 !important;
        border-color: #D94841;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(185, 54, 47, 0.25);
    }

    /* Primary Red Link Button */
    .rs-btn-primary-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #B9362F;
        color: #FFFFFF !important;
        border: 1.5px solid #D94841;
        border-radius: 9px;
        padding: 10px 24px;
        font-weight: 700;
        font-size: 0.93rem;
        text-decoration: none;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 16px rgba(185, 54, 47, 0.35);
        cursor: pointer;
    }
    .rs-btn-primary-link:hover {
        background-color: #D94841;
        border-color: #FF6B63;
        color: #FFFFFF !important;
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 24px rgba(217, 72, 65, 0.45);
    }

    /* Sticky Dark Navbar */
    .lp-navbar {
        background: rgba(13, 17, 23, 0.88);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.10);
        padding: 12px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
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
        box-shadow: 0 0 16px rgba(185, 54, 47, 0.45);
        transition: transform 0.2s ease;
    }
    .lp-logo-badge:hover {
        transform: scale(1.05);
    }
    .lp-brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.025em;
        line-height: 1.1;
    }
    .lp-brand-accent {
        color: #FF6B63;
    }
    .lp-brand-sub {
        font-size: 0.76rem;
        color: #AAB4C0;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .lp-nav-links {
        display: flex;
        align-items: center;
        gap: 28px;
    }
    .lp-nav-item {
        color: #AAB4C0;
        font-size: 0.92rem;
        font-weight: 600;
        text-decoration: none;
        transition: color 0.2s ease;
        position: relative;
        white-space: nowrap;
    }
    .lp-nav-item:hover {
        color: #FF6B63;
    }
    .lp-nav-item::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 0%;
        height: 2px;
        background-color: #D94841;
        transition: width 0.2s ease;
    }
    .lp-nav-item:hover::after {
        width: 100%;
    }

    /* Small Animated Hero Badge */
    .lp-badge-animated {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: rgba(185, 54, 47, 0.14);
        color: #FF6B63;
        border: 1px solid rgba(185, 54, 47, 0.35);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 20px;
        padding: 6px 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(185, 54, 47, 0.15);
    }
    .lp-badge-dot {
        width: 8px;
        height: 8px;
        background-color: #D94841;
        box-shadow: 0 0 8px #D94841;
        border-radius: 50%;
        display: inline-block;
        animation: pulseRedDot 1.8s infinite ease-in-out;
    }

    .lp-hero-heading {
        font-size: 3.2rem;
        font-weight: 900;
        color: #F8FAFC;
        line-height: 1.15;
        letter-spacing: -0.03em;
        margin-bottom: 18px;
    }
    .lp-hero-heading .red-accent {
        color: #FF6B63;
        background: linear-gradient(135deg, #FF6B63 0%, #D94841 50%, #B9362F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .lp-hero-desc {
        font-size: 1.12rem;
        color: #AAB4C0;
        line-height: 1.65;
        margin-bottom: 28px;
        max-width: 580px;
    }

    /* Hero Checkmark Trust Points */
    .lp-hero-trust-row {
        display: flex;
        gap: 22px;
        margin-top: 24px;
        font-size: 0.85rem;
        color: #CBD5E1;
        font-weight: 600;
    }
    .lp-hero-trust-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .lp-hero-trust-check {
        color: #FF6B63;
        font-weight: 900;
        font-size: 0.95rem;
    }

    /* Hero Floating CT Visualization Container with Ambient Red Glow */
    .lp-ct-float-container {
        position: relative;
        background: radial-gradient(circle at 50% 50%, rgba(185, 54, 47, 0.12) 0%, #0B0E14 75%);
        border: 1.5px solid rgba(255, 255, 255, 0.10);
        border-top: 3.5px solid #B9362F;
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px rgba(185, 54, 47, 0.15);
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

    /* Floating Dark Glass Hero Cards */
    .lp-float-card {
        position: absolute;
        background: rgba(21, 28, 36, 0.92);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 10px 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        z-index: 10;
        pointer-events: none;
        color: #F8FAFC;
    }
    .lp-float-card-1 {
        bottom: 22px;
        left: 20px;
        border-left: 4px solid #FF6B63;
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

    /* Scroll Indicator */
    .lp-scroll-ind-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 18px;
        cursor: pointer;
    }
    .lp-scroll-ind-text {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #AAB4C0;
        margin-bottom: 4px;
    }
    .lp-scroll-ind-arrow {
        font-size: 1.15rem;
        color: #FF6B63;
        animation: bounceDown 1.8s infinite ease-in-out;
    }
    @keyframes bounceDown {
        0%, 100% { transform: translateY(0); opacity: 0.6; }
        50% { transform: translateY(6px); opacity: 1; }
    }

    /* Capability Strip (Dark #151C24) */
    .lp-trust-strip {
        background-color: #151C24;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 16px;
        padding: 18px 28px;
        margin-bottom: 50px;
        display: flex;
        align-items: center;
        justify-content: space-around;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .lp-trust-strip:hover {
        transform: translateY(-3px);
        border-color: rgba(217, 72, 65, 0.5);
        box-shadow: 0 10px 28px rgba(185, 54, 47, 0.22);
    }
    .lp-trust-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.84rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .lp-trust-icon {
        color: #FF6B63;
        font-size: 1.25rem;
    }
    .lp-trust-sep {
        color: rgba(255, 255, 255, 0.12);
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
        color: #F8FAFC;
        letter-spacing: -0.025em;
        margin-bottom: 10px;
    }
    .lp-section-title span {
        color: #FF6B63;
    }
    .lp-section-desc {
        font-size: 1.05rem;
        color: #AAB4C0;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Why RenalScan Feature Cards (Elevated Surface #1B232D) */
    .lp-feature-card {
        background: #1B232D;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-left: 4.5px solid #B9362F;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        display: flex;
        gap: 20px;
        align-items: flex-start;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    }
    .lp-feature-card:hover {
        border-left-color: #FF6B63;
        border-color: rgba(255, 255, 255, 0.22);
        transform: translateX(6px);
        box-shadow: 0 8px 24px rgba(185, 54, 47, 0.2);
    }
    .lp-feature-num {
        font-size: 2rem;
        font-weight: 900;
        color: #FF6B63;
        line-height: 1;
        min-width: 44px;
        text-shadow: 0 0 12px rgba(255, 107, 99, 0.35);
    }
    .lp-feature-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .lp-feature-desc {
        font-size: 0.9rem;
        color: #AAB4C0;
        line-height: 1.55;
    }

    /* Big CT Scan Showcase (Deepest Charcoal #080B10) */
    .lp-dark-showcase {
        background-color: #080B10;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-top: 4px solid #B9362F;
        border-radius: 24px;
        padding: 48px 40px;
        margin-bottom: 50px;
        color: #F8FAFC;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(185, 54, 47, 0.12);
        position: relative;
        overflow: hidden;
    }
    .lp-dark-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #F8FAFC;
        letter-spacing: -0.025em;
        margin-bottom: 8px;
    }
    .lp-dark-sub {
        font-size: 1.05rem;
        color: #AAB4C0;
        max-width: 640px;
        margin-bottom: 30px;
    }

    /* 6 Capabilities / Features Grid */
    .lp-cap-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 50px;
    }
    .lp-cap-card {
        background-color: #151C24;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .lp-cap-card:hover {
        transform: translateY(-4px);
        border-color: #B9362F;
        box-shadow: 0 10px 30px rgba(185, 54, 47, 0.22);
    }
    .lp-cap-icon {
        width: 44px;
        height: 44px;
        background-color: rgba(185, 54, 47, 0.18);
        color: #FF6B63;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        margin-bottom: 16px;
        transition: transform 0.2s ease;
    }
    .lp-cap-card:hover .lp-cap-icon {
        transform: scale(1.1);
    }
    .lp-cap-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 8px;
    }
    .lp-cap-desc {
        font-size: 0.88rem;
        color: #AAB4C0;
        line-height: 1.55;
    }

    /* Real White A4 Report on Dark Background for High-Contrast Realism */
    .lp-a4-report {
        background: #FFFFFF !important;
        color: #1F2937 !important;
        border-radius: 12px;
        padding: 36px 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .lp-a4-report:hover {
        transform: translateY(-4px);
        box-shadow: 0 28px 65px rgba(0, 0, 0, 0.75);
    }

    /* Kidney Health 4 Cards Grid (#151C24 Dark Surface) */
    .lp-health-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 50px;
    }
    .lp-health-card {
        background-color: #151C24;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .lp-health-card:hover {
        transform: translateY(-4px);
        border-color: #B9362F;
        box-shadow: 0 10px 28px rgba(185, 54, 47, 0.22);
    }
    .lp-health-icon {
        width: 44px;
        height: 44px;
        background-color: rgba(185, 54, 47, 0.18);
        color: #FF6B63;
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
        color: #F8FAFC;
        margin-bottom: 8px;
    }
    .lp-health-desc {
        font-size: 0.88rem;
        color: #AAB4C0;
        line-height: 1.55;
    }

    /* Responsible AI Shield Section */
    .lp-shield-section {
        background-color: #151C24;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-left: 5px solid #B9362F;
        border-radius: 18px;
        padding: 30px 36px;
        margin-bottom: 50px;
        display: flex;
        align-items: center;
        gap: 24px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }
    .lp-shield-icon-box {
        width: 64px;
        height: 64px;
        min-width: 64px;
        background-color: #1B232D;
        border: 2px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 4px 18px rgba(185, 54, 47, 0.25);
        animation: pulseShield 3s infinite ease-in-out;
    }
    @keyframes pulseShield {
        0%, 100% { box-shadow: 0 0 10px rgba(185, 54, 47, 0.2); transform: scale(1); }
        50% { box-shadow: 0 0 25px rgba(217, 72, 65, 0.45); transform: scale(1.04); }
    }

    /* Final Red Gradient CTA */
    .lp-final-cta-wrapper {
        background: linear-gradient(135deg, #151C24 0%, #3B1210 40%, #8F2924 75%, #B9362F 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 56px 44px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 16px 48px rgba(185, 54, 47, 0.3);
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
        margin: 0 auto;
        line-height: 1.6;
    }
    .rs-cta-white-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #FFFFFF;
        color: #B9362F !important;
        border: 2px solid #FFFFFF;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 800;
        font-size: 1rem;
        text-decoration: none;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
        cursor: pointer;
    }
    .rs-cta-white-btn:hover {
        background-color: #FCEDEC;
        color: #8F2924 !important;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    /* Footer */
    .lp-footer {
        background-color: #080B10;
        color: #AAB4C0;
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
        color: #F8FAFC;
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
        color: #AAB4C0;
        margin-bottom: 9px;
    }
    .lp-footer-bottom {
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 20px;
        text-align: center;
        font-size: 0.8rem;
        color: #64748B;
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
        .lp-cap-grid { grid-template-columns: 1fr 1fr; }
        .lp-footer-grid { grid-template-columns: 1fr; gap: 24px; }
        .lp-hero-heading { font-size: 2.4rem; }
    }
    @media (max-width: 600px) {
        .lp-health-grid { grid-template-columns: 1fr; }
        .lp-cap-grid { grid-template-columns: 1fr; }
        .lp-trust-strip { flex-direction: column; gap: 14px; }
        .lp-trust-sep { display: none; }
        .lp-hero-heading { font-size: 2rem; }
        .lp-hero-trust-row { flex-direction: column; gap: 8px; }
    }
</style>
""", unsafe_allow_html=True)
