"""
frontend/styles.py
──────────────────
Style loader for EcoScan AI. Injects frontend/styles.css into Streamlit.
"""

from pathlib import Path

CSS_PATH = Path(__file__).resolve().parent / "styles.css"


def get_modern_css() -> str:
    """Returns the CSS string wrapped in <style> tags."""
    if CSS_PATH.exists():
        css_content = CSS_PATH.read_text(encoding="utf-8")
        return f"<style>\n{css_content}\n</style>"
    return ""
