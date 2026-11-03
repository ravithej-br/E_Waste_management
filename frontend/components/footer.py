"""
frontend/components/footer.py
─────────────────────────────
Reusable, clean, identical footer component for all pages.
Highlights privacy guarantee (volatile RAM evaluation) and statutory compliance.
"""

import streamlit as st


def render_footer():
    """Renders the standard small footer on every page."""
    st.markdown(
        """
        <div class="app-footer">
            🔒 <b>Privacy Assured:</b> All scans are evaluated strictly in volatile RAM. No images are permanently persisted to disk or cloud servers.
            <br>
            ⚖️ <b>Statutory Compliance:</b> EcoScan AI aligns with India E-Waste (Management) Rules 2022 & Battery Waste Rules 2022.
        </div>
        """,
        unsafe_allow_html=True,
    )
