"""
frontend/app.py
───────────────
Main Application Router and Master Layout for EcoScan AI.
Features modern aesthetics, smooth page transitions, user authentication,
and multi-page navigation across Scanner, Recyclers Map, Regulations, Benchmarks, and Profile.
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

# ─────────────────────────────────────────────
# PAGE INITIALIZATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EcoScan AI • Intelligent E-Waste Platform",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject modern CSS styling and animations
st.markdown(get_modern_css(), unsafe_allow_html=True)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# ─────────────────────────────────────────────
# ROUTING CONTROLLER
# ─────────────────────────────────────────────
if not st.session_state["authenticated"]:
    # Render modern authentication & registration portal
    render_login_page()

    # Footer on login
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 40px 0 10px 0;">
            CSE Mini-Project • Bengaluru, Karnataka • Compliant with India E-Waste (Management) Rules 2022
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Authenticated Multi-Page Experience
    user = st.session_state["user"] or {}
    full_name = user.get("full_name", "Researcher")
    username = user.get("username", "demo")

    # Sidebar branding & user status
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 1.8rem;">♻️</span>
                    <div>
                        <div style="font-weight: 800; font-size: 1.2rem; color: #ffffff; letter-spacing: -0.02em;">EcoScan AI</div>
                        <div style="font-size: 0.75rem; color: #34d399; font-weight: 600;">INT8 Neural Engine</div>
                    </div>
                </div>
                <div style="background: #151e2e; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px 12px; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #f1f5f9;">{full_name}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8;">@{username}</div>
                    </div>
                    <span style="height: 9px; width: 9px; background-color: #10b981; border-radius: 50%; display: inline-block;"></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Define dedicated pages
    p_scanner = st.Page(render_scanner_page, title="Scanner & Classifier", icon="📸", default=True)
    p_recyclers = st.Page(render_recyclers_page, title="Recyclers Directory", icon="📍")
    p_regulations = st.Page(render_regulations_page, title="Legal Guidelines", icon="⚖️")
    p_benchmarks = st.Page(render_benchmarks_page, title="Model Benchmarks", icon="📊")
    p_profile = st.Page(render_profile_page, title="Account & History", icon="👤")

    # Run modern navigation
    pg = st.navigation(
        {
            "Core Services": [p_scanner, p_recyclers],
            "Compliance & Intelligence": [p_regulations, p_benchmarks],
            "User": [p_profile],
        }
    )

    pg.run()

    # Sidebar Logout Button
    with st.sidebar:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    # Universal Clean Footer
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 35px 0 15px 0; border-top: 1px solid #f1f5f9; margin-top: 40px;">
            🔒 <b>Privacy Assured:</b> All scans are evaluated strictly in volatile RAM. No images are permanently persisted to disk or external servers.
            <br>
            ⚠️ <b>Disclaimer:</b> Educational CSE Mini-Project (Bengaluru, Karnataka). Compliant with India E-Waste (Management) Rules 2022.
        </div>
        """,
        unsafe_allow_html=True,
    )
