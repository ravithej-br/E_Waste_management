"""
frontend/views/login.py
───────────────────────
Modern Dark SaaS Login & Registration portal for EcoScan AI.
Features crisp typography, clean cards, and 1-click demo access.
"""

import streamlit as st
from frontend.auth import authenticate_user, register_user


def render_login_page():
    """Renders the authentication portal with Login, Sign Up, and 1-Click Demo."""
    col_hero, col_auth = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div style="padding: 12px 0;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); padding: 4px 12px; border-radius: 9999px; color: #34d399; font-weight: 600; font-size: 0.75rem; margin-bottom: 16px; letter-spacing: 0.04em;">
                    🌿 CSE MINI-PROJECT • BENGALURU, KARNATAKA
                </div>
                <h1 style="font-size: 2.2rem; font-weight: 800; color: #ffffff; line-height: 1.2; letter-spacing: -0.03em; margin-bottom: 14px;">
                    Intelligent E-Waste Segregation & Compliance
                </h1>
                <p style="font-size: 0.95rem; color: #94a3b8; line-height: 1.6; margin-bottom: 24px;">
                    Edge AI classification powered by quantized EfficientNet-B0, automated statutory hazard assessment under India E-Waste Rules 2022, and verified KSPCB recycler routing.
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px;">
                    <div class="stat-pill">
                        <div class="stat-pill-val">90.07%</div>
                        <div class="stat-pill-lbl">Accuracy</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-val">5.03 ms</div>
                        <div class="stat-pill-lbl">Latency</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-val">8 Hubs</div>
                        <div class="stat-pill-lbl">KSPCB Verified</div>
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.06); border-left: 3px solid #10b981; padding: 12px 14px; border-radius: 6px; font-size: 0.8rem; color: #cbd5e1;">
                    🔒 <b>Privacy Commitment:</b> Images are evaluated strictly in volatile RAM. No photo is ever stored to disk.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_auth:
        st.markdown(
            """
            <div class="dark-card" style="margin-bottom: 14px;">
                <h3 style="margin: 0 0 4px 0; color: #ffffff; font-weight: 700; font-size: 1.15rem; letter-spacing: -0.02em;">Terminal Access</h3>
                <p style="color: #94a3b8; font-size: 0.82rem; margin: 0;">Sign in to access scanner, audit history, and recycler directory.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input("Username or Email", placeholder="e.g. demo or researcher@ewaste.org")
                login_pw = st.text_input("Password", type="password", placeholder="Enter your password")
                submit_login = st.form_submit_button("Sign In to Platform", type="primary", use_container_width=True)

                if submit_login:
                    if not login_id or not login_pw:
                        st.error("Please enter both username/email and password.")
                    else:
                        success, user_data = authenticate_user(login_id, login_pw)
                        if success:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user_data
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")

            st.markdown(
                """
                <div style="text-align: center; margin: 14px 0 10px 0; color: #64748b; font-size: 0.75rem; letter-spacing: 0.05em;">
                    ── OR INSTANT EVALUATION ──
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("⚡ One-Click Demo Access", use_container_width=True, type="secondary"):
                success, user_data = authenticate_user("demo", "demo123")
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user_data
                    st.rerun()

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. Ravitheja B R")
                reg_username = st.text_input("Choose Username", placeholder="e.g. ravitheja")
                reg_email = st.text_input("Email Address", placeholder="e.g. user@gmail.com")
                reg_pw = st.text_input("Password (min 6 characters)", type="password")
                reg_pw2 = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Create My Account", type="primary", use_container_width=True)

                if submit_reg:
                    if reg_pw != reg_pw2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = register_user(reg_username, reg_email, reg_name, reg_pw)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
