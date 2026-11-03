"""
frontend/views/profile.py
─────────────────────────
Dedicated Account & History page for EcoScan AI.
Contains:
  - Top profile card (Name, Username, Total Scans, Most Common Category)
  - Summary metrics row (st.metric)
  - Comprehensive audit history list with filters, pagination, dialog, CSV export, and deletion.
  - Zero raw image persistence (Privacy Guarantee).
"""

import streamlit as st
from frontend.utils.history import get_user_stats
from frontend.components.history_table import render_history_component


def render_profile_page():
    """Renders the comprehensive Account Profile and Scan History Audit page."""
    # Header Card
    st.markdown(
        """
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>👤 Account & Audit History</h1>
                    <p>Review your researcher credentials, inspection volume, and historical e-waste audit logs.</p>
                </div>
                <span class="privacy-pill">🔒 Zero Raw Image Persistence</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user = st.session_state.get("user") or {}
    username = user.get("username", "demo")
    full_name = user.get("full_name", "Researcher")
    email = user.get("email", "user@example.com")
    created_at = str(user.get("created_at", "2026-10-23"))[:10]

    # Calculate summary stats for the top profile card
    stats = get_user_stats(username)
    total_scans = stats["total_scans"]
    top_category = stats["top_category"]

    # 1. Top Profile Card
    st.markdown(
        f"""
        <div class="dark-card" style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff;
                                width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center;
                                justify-content: center; font-size: 1.5rem; font-weight: 800; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);">
                        {full_name[:1].upper()}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <h2 style="margin: 0; color: #ffffff; font-size: 1.35rem; font-weight: 800;">{full_name}</h2>
                            <span style="background: rgba(16, 185, 129, 0.16); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                VERIFIED
                            </span>
                        </div>
                        <span style="color: #94a3b8; font-size: 0.88rem;">@{username} • {email}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 24px; text-align: right;">
                    <div>
                        <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.04em;">Total Scans</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #10b981;">{total_scans}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.04em;">Primary Material</div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #f1f5f9;">{top_category}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.04em;">Member Since</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #cbd5e1; margin-top: 4px;">{created_at}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Helper callback to jump back to Scanner
    def _go_to_scanner():
        if "page_scanner" in st.session_state and hasattr(st, "switch_page"):
            st.switch_page(st.session_state["page_scanner"])

    # 2. Render Full History Table & Management Controls
    render_history_component(username=username, on_navigate_scanner=_go_to_scanner)
