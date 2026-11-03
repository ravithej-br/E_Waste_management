"""
frontend/components/cards.py
────────────────────────────
Reusable card widgets for headers, candidate probabilities, and metric pills.
"""

import streamlit as st
from frontend.components.badges import render_privacy_pill


def render_header_card(title: str, subtitle: str, pill_text: str = "Volatile RAM Only"):
    """Renders the standard page header card with title, subtitle, and privacy pill."""
    st.markdown(
        f"""
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
                {render_privacy_pill(pill_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_candidate_row(label: str, confidence: float, icon: str = "📦") -> str:
    """Renders a candidate class probability bar."""
    pct = round(confidence * 100, 1)
    return f"""
    <div class="candidate-row">
        <span class="candidate-row-name">{icon} {label}</span>
        <div class="candidate-row-bar-bg">
            <div class="candidate-row-bar-fill" style="width: {pct}%;"></div>
        </div>
        <span class="candidate-row-pct">{pct}%</span>
    </div>
    """


def render_stat_pill_html(value: str, label: str) -> str:
    """Renders a stat pill container."""
    return f"""
    <div class="stat-pill">
        <div class="stat-pill-val">{value}</div>
        <div class="stat-pill-lbl">{label}</div>
    </div>
    """
