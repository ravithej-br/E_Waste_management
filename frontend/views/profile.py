"""
frontend/views/profile.py
─────────────────────────
User Profile, Account Information, and Scan Audit Log History view.
"""

import streamlit as st
import pandas as pd
from frontend.auth import get_user_history


def render_profile_page():
    """Renders user account details and audit log of previous e-waste scans."""
    st.markdown(
        """
        <div class="app-header">
            <h1>👤 Account & Scan History</h1>
            <p>View your credentials and inspect previous electronic waste audit records.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user = st.session_state.get("user", {})
    username = user.get("username", "demo")
    full_name = user.get("full_name", "Researcher")
    email = user.get("email", "user@example.com")
    created_at = user.get("created_at", "2026-10-23")

    col_info, col_actions = st.columns([2, 1], gap="large")

    with col_info:
        st.markdown(
            f"""
            <div class="dark-card">
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                    <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 700;">
                        {full_name[:1].upper()}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #ffffff; font-size: 1.25rem;">{full_name}</h3>
                        <span style="color: #94a3b8; font-size: 0.88rem;">@{username} • {email}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem; color: #cbd5e1; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 12px;">
                    <div><b>Status:</b> <span style="color: #10b981; font-weight: 600;">Active / Verified</span></div>
                    <div><b>Registered:</b> {created_at[:10]}</div>
                    <div><b>Storage:</b> In-Memory Protected</div>
                    <div><b>City:</b> Bengaluru (Karnataka)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown(
            """
            <div class="dark-card">
                <h4 style="margin: 0 0 6px 0; color: #ffffff;">Session Control</h4>
                <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 14px;">
                    Sign out to end current session. In-memory temporary cache will be cleared.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Sign Out of Platform", type="secondary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["current_scan_result"] = None
            st.session_state["active_image_bytes"] = None
            st.rerun()

    st.markdown("### 📋 Your Recent E-Waste Scan History")

    history = get_user_history(username=username, limit=15)

    if not history:
        st.info("No scans recorded yet. Go to 'Scanner & Classifier' to analyze your first item!")
    else:
        df_hist = pd.DataFrame(history)
        df_hist["Confidence"] = (df_hist["confidence"] * 100).round(1).astype(str) + "%"
        df_hist["Item Category"] = df_hist["prediction"].apply(lambda s: s.replace("_", " ").title())
        df_hist["Date & Time"] = df_hist["scanned_at"].str.slice(0, 19)

        display_df = df_hist[["Date & Time", "Item Category", "Confidence", "hazard_level"]]
        display_df.columns = ["Scanned At", "Predicted Material", "Calibrated Confidence", "Hazard Rating"]

        st.dataframe(display_df, use_container_width=True, hide_index=True)
