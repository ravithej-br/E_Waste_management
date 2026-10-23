"""
frontend/views/login.py
───────────────────────
Modern Dark-Mode Login and Registration view for E-Waste Platform.
Provides form authentication, registration validation, and 1-click Demo mode.
"""

import streamlit as st
from frontend.auth import authenticate_user, register_user


def render_login_page():
    """Renders the authentication portal with Login, Sign Up, and Demo modes."""
    col_hero, col_auth = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div style="padding: 10px 0;">
                <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); padding: 5px 14px; border-radius: 9999px; color: #34d399; font-weight: 600; font-size: 0.82rem; margin-bottom: 16px;">
                    🌿 CSE Mini-Project • Bengaluru, Karnataka
                </div>
                <h1 style="font-size: 2.4rem; font-weight: 800; color: #ffffff; line-height: 1.2; letter-spacing: -0.03em; margin-bottom: 14px;">
                    Intelligent E-Waste Segregation & Compliance
                </h1>
                <p style="font-size: 1.05rem; color: #94a3b8; line-height: 1.6; margin-bottom: 24px;">
                    Real-time AI classification powered by quantized EfficientNet-B0, automated statutory hazard assessment under India E-Waste Rules 2022, and instant Bengaluru recycler matching.
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px;">
                    <div class="stat-pill">
                        <div class="stat-pill-val">90.07%</div>
                        <div class="stat-pill-lbl">Test Accuracy</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-val">5.0 ms</div>
                        <div class="stat-pill-lbl">CPU Latency</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-val">8 Centers</div>
                        <div class="stat-pill-lbl">KSPCB Mapped</div>
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10b981; padding: 12px 16px; border-radius: 6px; font-size: 0.85rem; color: #cbd5e1;">
                    🔒 <b>Privacy Commitment:</b> Images are processed strictly in volatile RAM. No photo is ever stored to disk or cloud databases.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_auth:
        st.markdown(
            """
            <div class="dark-card" style="margin-bottom: 16px;">
                <h3 style="margin-top: 0; margin-bottom: 4px; color: #ffffff; font-weight: 700;">Account Portal</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">Sign in to access scanner, history, and recycling directory.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input("Username or Email", placeholder="e.g. demo or user@example.com")
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
                            st.success(f"Welcome back, {user_data['full_name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password.")

            st.markdown(
                """
                <div style="text-align: center; margin: 15px 0 10px 0; color: #64748b; font-size: 0.82rem;">
                    ── OR INSTANT EVALUATION ──
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick Demo Login Button
            if st.button("⚡ One-Click Demo Mode (Tester Access)", use_container_width=True, type="secondary"):
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
