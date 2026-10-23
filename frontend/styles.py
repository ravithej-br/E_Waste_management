"""
frontend/styles.py
──────────────────
Modern, cohesive design system, typography, color palettes, and micro-animations
for the E-Waste Classification and Recycling Guidance Platform.
"""

def get_modern_css() -> str:
    return """
    <style>
    /* Google Fonts & Modern Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1e293b;
    }

    /* Page container spacing */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1280px;
    }

    /* Subtle Animated Fade-In */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in-container {
        animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Modern Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 45%, #059669 100%);
        color: #ffffff;
        padding: 30px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.25), 0 8px 10px -6px rgba(5, 150, 105, 0.15);
        position: relative;
        overflow: hidden;
    }

    .hero-banner::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0 0 8px 0;
    }

    .hero-banner p {
        color: #d1fae5;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0;
        line-height: 1.5;
    }

    /* Glassmorphic & Modern Cards */
    .modern-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease;
    }

    .modern-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 30px -4px rgba(0, 0, 0, 0.07), 0 6px 12px -4px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }

    /* Recycler Highlight Card */
    .recycler-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px -1px rgba(0, 0, 0, 0.04);
        transition: all 0.25s ease;
        position: relative;
    }

    .recycler-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px -4px rgba(16, 185, 129, 0.12);
        border-color: #10b981;
    }

    /* Hazard Level Badges */
    .badge-critical {
        display: inline-block;
        background: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .badge-high {
        display: inline-block;
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .badge-moderate {
        display: inline-block;
        background: #fefce8;
        color: #a16207;
        border: 1px solid #fef08a;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .badge-low {
        display: inline-block;
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* Privacy Banner Callout */
    .privacy-callout {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 0.95rem;
        color: #065f46;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Auth Card */
    .auth-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 36px 40px;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.07);
        max-width: 480px;
        margin: 0 auto;
    }

    /* User Profile Pill */
    .user-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #e2e8f0;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #334155;
    }

    /* Custom Streamlit Buttons Overrides */
    div.stButton > button:first-child {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
    }

    /* Primary CTA buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35);
    }

    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* Stat Highlight Box */
    .stat-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #059669;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    </style>
    """
