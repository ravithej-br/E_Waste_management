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
        <div class="hero-banner">
            <h1>👤 Account & Scan History</h1>
            <p>View your profile credentials and inspect your recent electronic waste audit logs.</p>
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
            <div class="modern-card">
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                    <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700;">
                        {full_name[:1].upper()}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #0f172a; font-size: 1.3rem;">{full_name}</h3>
                        <span style="color: #64748b; font-size: 0.9rem;">@{username} • {email}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.88rem; color: #475569; border-top: 1px solid #f1f5f9; padding-top: 14px;">
                    <div><b>Account Status:</b> <span style="color: #059669; font-weight: 600;">Active / Verified</span></div>
                    <div><b>Registered On:</b> {created_at[:10]}</div>
                    <div><b>Session Type:</b> In-Memory Authenticated</div>
                    <div><b>Jurisdiction:</b> Bengaluru (Karnataka)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_actions:
        st.markdown(
            """
            <div class="modern-card">
                <h4 style="margin: 0 0 8px 0; color: #0f172a;">Session Control</h4>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">
                    Sign out of your account session. In-memory temporary cache will be cleanly cleared.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Sign Out of Platform", type="secondary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

    st.markdown("### 📋 Your Recent E-Waste Scan History")

    history = get_user_history(username=username, limit=15)

    if not history:
        st.info("No scans recorded yet. Go to the 'Scan & Classify' page to analyze your first item!")
    else:
        df_hist = pd.DataFrame(history)
        df_hist["Confidence"] = (df_hist["confidence"] * 100).round(1).astype(str) + "%"
        df_hist["Item Category"] = df_hist["prediction"].apply(lambda s: s.replace("_", " ").title())
        df_hist["Date & Time"] = df_hist["scanned_at"].str.slice(0, 19)

        display_df = df_hist[["Date & Time", "Item Category", "Confidence", "hazard_level"]]
        display_df.columns = ["Scanned At", "Predicted Material", "Calibrated Confidence", "Hazard Rating"]

        st.dataframe(display_df, use_container_width=True, hide_index=True)
