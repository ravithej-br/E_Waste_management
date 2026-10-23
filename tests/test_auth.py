"""
tests/test_auth.py
──────────────────
Unit tests for user registration, authentication, and scan history.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from frontend.auth import register_user, authenticate_user, record_scan, get_user_history


def test_demo_user_authentication():
    """Verify default demo user exists and authenticates with demo credentials."""
    ok, user = authenticate_user("demo", "demo123")
    assert ok is True
    assert user is not None
    assert user["username"] == "demo"
    assert user["full_name"] == "Demo Researcher"


def test_user_registration_and_login():
    """Verify new user registration and subsequent login."""
    test_uname = "tester_unit"
    test_email = "tester_unit@example.com"
    test_pass = "secret123"

    ok, msg = register_user(test_uname, test_email, "Unit Tester", test_pass)
    # Could be true or already registered if rerun
    if ok:
        assert "success" in msg.lower()

    # Verify login
    login_ok, user_data = authenticate_user(test_uname, test_pass)
    assert login_ok is True
    assert user_data["username"] == test_uname


def test_invalid_login():
    """Verify rejection of wrong passwords."""
    ok, user = authenticate_user("demo", "wrongpassword123")
    assert ok is False
    assert user is None


def test_scan_history_recording():
    """Verify recording and retrieval of scan history."""
    test_uname = "demo"
    record_scan(test_uname, "battery", 0.9452, "CRITICAL")
    history = get_user_history(test_uname, limit=5)
    assert len(history) > 0
    latest = history[0]
    assert latest["prediction"] == "battery"
    assert latest["hazard_level"] == "CRITICAL"
