"""
app.py - RenalScan Application Router & Main Entry Point
Architecture:
  - Root route '/' -> RenalScan Dedicated Landing Page (app/landing_page.py)
  - Workstation route '/workstation' -> Existing CT Analysis Workstation (app/workstation_page.py)
Brand Identity: Official Medical Red (#B9362F) & Canvas White (#FFFFFF)
"""

import sys
from pathlib import Path
import streamlit as st

# Configure project roots in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION - RENALSCAN RED + WHITE MEDICAL IDENTITY
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RenalScan — AI Kidney Stone Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# GLOBAL BRAND STYLESHEET
# -----------------------------------------------------------------------------
try:
    from app.styles import inject_global_css
    from app.landing_page import render_landing_page
    from app.workstation_page import render_workstation_page
except ImportError:
    from styles import inject_global_css
    from landing_page import render_landing_page
    from workstation_page import render_workstation_page

inject_global_css()

# -----------------------------------------------------------------------------
# APPLICATION MULTI-PAGE ROUTING SYSTEM
# -----------------------------------------------------------------------------
def landing_view():
    render_landing_page(page_workstation=page_workstation)

def workstation_view():
    render_workstation_page(page_landing=page_landing)

# Multi-page configuration with exact URL paths:
# '/' -> Landing Page (default)
# '/workstation' -> CT Analysis Workstation
page_landing = st.Page(
    landing_view,
    title="RenalScan — AI Kidney Stone Analysis",
    icon="🩺",
    url_path="",
    default=True
)

page_workstation = st.Page(
    workstation_view,
    title="RenalScan — Analysis Workstation",
    icon="🔬",
    url_path="workstation"
)

pg = st.navigation([page_landing, page_workstation], position="hidden")

# Seamless compatibility with query parameters (e.g. ?page=workstation or ?page=landing)
if "page" in st.query_params:
    requested_page = st.query_params.get("page")
    if requested_page == "workstation" and pg != page_workstation:
        st.query_params.clear()
        st.switch_page(page_workstation)
    elif requested_page == "landing" and pg != page_landing:
        st.query_params.clear()
        st.switch_page(page_landing)

# Execute the routed page
pg.run()
