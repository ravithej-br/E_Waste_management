"""
frontend/styles.py
──────────────────
Modern, sleek dark-mode design system for EcoScan AI.
High-contrast typography, glassmorphic cards, smooth micro-interactions,
and complete compatibility with Streamlit's dark theme.
"""

def get_modern_css() -> str:
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Page Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.0rem !important;
        max-width: 1200px !important;
    }

    /* Smooth Fade-in Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Modern Minimalist Header */
    .app-header {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }

    .app-header h1 {
        color: #ffffff !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        margin: 0 0 6px 0 !important;
        letter-spacing: -0.02em;
    }

    .app-header p {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        line-height: 1.4;
    }

    /* Sleek Dark Surface Cards */
    .dark-card {
        background: #151e2e !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35) !important;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .dark-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.4) !important;
        box-shadow: 0 8px 30px -4px rgba(16, 185, 129, 0.12) !important;
    }

    /* Recycler Card */
    .recycler-card-dark {
        background: #151e2e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: all 0.2s ease;
    }

    .recycler-card-dark:hover {
        border-color: #10b981;
        box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.15);
        transform: translateY(-2px);
    }

    /* High-Contrast Hazard Badges */
    .badge-critical {
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.16) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
        padding: 4px 14px !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    .badge-high {
        display: inline-flex;
        align-items: center;
        background: rgba(249, 115, 22, 0.16) !important;
        color: #fb923c !important;
        border: 1px solid rgba(249, 115, 22, 0.35) !important;
        padding: 4px 14px !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    .badge-moderate {
        display: inline-flex;
        align-items: center;
        background: rgba(234, 179, 8, 0.16) !important;
        color: #facc15 !important;
        border: 1px solid rgba(234, 179, 8, 0.35) !important;
        padding: 4px 14px !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    .badge-low {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.16) !important;
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        padding: 4px 14px !important;
        border-radius: 9999px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }

    /* Candidate Class Row */
    .candidate-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.03);
        margin-bottom: 6px;
    }

    .candidate-row-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #e2e8f0;
    }

    .candidate-row-bar-bg {
        flex-grow: 1;
        margin: 0 16px;
        height: 8px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 9999px;
        overflow: hidden;
    }

    .candidate-row-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        border-radius: 9999px;
    }

    .candidate-row-pct {
        font-weight: 700;
        font-size: 0.85rem;
        color: #10b981;
        min-width: 45px;
        text-align: right;
    }

    /* Privacy Banner */
    .privacy-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.82rem;
        color: #34d399;
        background: rgba(16, 185, 129, 0.1);
        padding: 6px 14px;
        border-radius: 9999px;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* Modern Primary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.65rem 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    }

    div.stButton > button[kind="secondary"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        border-color: #10b981 !important;
        color: #ffffff !important;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Metric Box */
    .stat-pill {
        background: #151e2e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stat-pill-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #10b981;
    }
    .stat-pill-lbl {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 2px;
    }
    </style>
    """
