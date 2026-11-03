"""
frontend/components/badges.py
─────────────────────────────
Reusable HTML badges and status indicators for hazard levels,
privacy guarantees, and facility operating status.
"""

def render_hazard_badge(hazard_level: str) -> str:
    """
    Renders a consistent, high-contrast hazard badge.
    - Low: Green (#34d399)
    - Moderate / Medium: Amber (#fbbf24)
    - High / Critical: Red (#f87171)
    """
    lvl = (hazard_level or "MODERATE").upper()
    if "CRITICAL" in lvl:
        cls_name = "badge-critical"
        label = "CRITICAL HAZARD"
    elif "HIGH" in lvl:
        cls_name = "badge-high"
        label = "HIGH HAZARD"
    elif "LOW" in lvl:
        cls_name = "badge-low"
        label = "LOW HAZARD"
    else:
        cls_name = "badge-medium"
        label = "MODERATE HAZARD"

    return f'<span class="{cls_name}">{label}</span>'


def render_privacy_pill(text: str = "Volatile RAM Only • Zero Disk Storage") -> str:
    """Renders small, consistent privacy promise pill."""
    return f'<span class="privacy-pill">🔒 {text}</span>'


def render_status_badge(is_open: bool, label: str) -> str:
    """Renders facility open/closed badge."""
    if is_open:
        return (
            '<span style="background: rgba(16, 185, 129, 0.16); color: #34d399; '
            'border: 1px solid rgba(16, 185, 129, 0.35); padding: 2px 10px; '
            'border-radius: 9999px; font-weight: 700; font-size: 0.72rem;">🟢 OPEN TODAY</span>'
        )
    return (
        '<span style="background: rgba(239, 68, 68, 0.16); color: #f87171; '
        'border: 1px solid rgba(239, 68, 68, 0.35); padding: 2px 10px; '
        'border-radius: 9999px; font-weight: 700; font-size: 0.72rem;">🔴 CLOSED TODAY</span>'
    )
