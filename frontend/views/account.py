"""
frontend/views/account.py
─────────────────────────
Alias module for Account & History page.
"""

from frontend.views.profile import render_profile_page

def render_account_page():
    render_profile_page()
