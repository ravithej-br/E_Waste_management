"""
frontend/views/login.py
───────────────────────
Minimalist, distraction-free Dark SaaS Login & Registration portal.
Contains ONLY essential authentication and registration controls.
"""

import streamlit as st
from frontend.auth import authenticate_user, register_user


def render_login_page():
    """Renders a clean, centered authentication card with Sign In and Registration tabs."""
    # Center the authentication container
    col_left, col_center, col_right = st.columns([1, 1.4, 1], gap="medium")

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px; padding-top: 16px;">
                <span style="font-size: 2.8rem; line-height: 1;">♻️</span>
                <h1 style="color: #ffffff; font-size: 1.75rem; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -0.02em;">EcoScan AI</h1>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">Sign in to your account or register to get started</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="dark-card">', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                login_id = st.text_input("Username or Email", placeholder="e.g. demo or user@example.com")
                login_pw = st.text_input("Password", type="password", placeholder="Enter your password")
                submit_login = st.form_submit_button("Sign In", type="primary", use_container_width=True)

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
                <div style="text-align: center; margin: 12px 0 10px 0; color: #64748b; font-size: 0.75rem; letter-spacing: 0.05em;">
                    ── OR INSTANT ACCESS ──
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
                reg_name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
                reg_username = st.text_input("Choose Username", placeholder="e.g. janedoe")
                reg_email = st.text_input("Email Address", placeholder="e.g. user@example.com")
                reg_pw = st.text_input("Password (min 6 characters)", type="password")
                reg_pw2 = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if submit_reg:
                    if not reg_name or not reg_username or not reg_email or not reg_pw:
                        st.error("Please fill in all registration fields.")
                    elif reg_pw != reg_pw2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = register_user(reg_username, reg_email, reg_name, reg_pw)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

        st.markdown('</div>', unsafe_allow_html=True)
