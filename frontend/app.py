"""
frontend/app.py
───────────────
Main Application Router and Layout Controller for EcoScan AI.
Features:
  - Streamlit st.navigation & st.Page architecture with strict page separation.
  - Clean sidebar containing ONLY: logo + app name, compact user chip, navigation, and pinned Sign Out.
  - Zero page-specific controls in the sidebar.
  - Shared identical footer on all views.
"""

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from frontend.styles import get_modern_css
from frontend.views.login import render_login_page
from frontend.views.scanner import render_scanner_page
from frontend.views.recyclers import render_recyclers_page
from frontend.views.regulations import render_regulations_page
from frontend.views.benchmarks import render_benchmarks_page
from frontend.views.profile import render_profile_page
from frontend.components.footer import render_footer

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EcoScan AI • E-Waste Classification Platform",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Dark Navy + Emerald Green theme
st.markdown(get_modern_css(), unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# ─────────────────────────────────────────────
# ROUTING CONTROLLER
# ─────────────────────────────────────────────
if not st.session_state["authenticated"]:
    render_login_page()
    render_footer()
else:
    user = st.session_state["user"] or {}
    full_name = user.get("full_name", "Researcher")
    username = user.get("username", "demo")

    # 1. Sidebar: Logo + App Name + Compact User Chip
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 4px 0 14px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <span style="font-size: 1.8rem; line-height: 1;">♻️</span>
                    <div>
                        <div style="font-weight: 800; font-size: 1.15rem; color: #ffffff; letter-spacing: -0.02em;">EcoScan AI</div>
                        <div style="font-size: 0.72rem; color: #10b981; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">INT8 Neural Platform</div>
                    </div>
                </div>
                <div style="background: #11131a; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #f1f5f9;">{full_name}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8;">@{username}</div>
                    </div>
                    <span style="height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block;" title="Active Session"></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Define Dedicated Pages
    p_scanner = st.Page(render_scanner_page, title="Scanner & Classifier", icon="📸", default=True)
    p_recyclers = st.Page(render_recyclers_page, title="Recyclers Directory", icon="📍")
    p_regulations = st.Page(render_regulations_page, title="Legal Guidelines", icon="⚖️")
    p_benchmarks = st.Page(render_benchmarks_page, title="Model Benchmarks", icon="📊")
    p_account = st.Page(render_profile_page, title="Account & History", icon="👤")

    # Expose page objects in session state for reliable cross-page switching
    st.session_state["page_scanner"] = p_scanner
    st.session_state["page_recyclers"] = p_recyclers
    st.session_state["page_regulations"] = p_regulations
    st.session_state["page_benchmarks"] = p_benchmarks
    st.session_state["page_account"] = p_account

    # 3. Multi-Page Navigation with st.navigation
    pg = st.navigation(
        {
            "Core Services": [p_scanner, p_recyclers],
            "Intelligence & Law": [p_regulations, p_benchmarks],
            "User": [p_account],
        }
    )

    # Render Active Page
    pg.run()

    # 4. Pinned Sidebar Sign Out Button
    with st.sidebar:
        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary", key="btn_sidebar_signout"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["current_scan_result"] = None
            st.session_state["active_image_bytes"] = None
            st.rerun()

    # 5. Shared Identical Universal Footer
    render_footer()
