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
from frontend.utils.history import (
    get_user_stats,
    get_user_history_filtered,
    count_user_history_filtered,
    delete_scan,
    clear_user_history,
    export_user_history_csv,
)


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


def test_history_filtering_and_stats():
    """Verify advanced history querying, filtering, metrics, and CSV export."""
    user = "tester_history"
    record_scan(user, "battery", 0.95, "CRITICAL")
    record_scan(user, "keyboard", 0.88, "LOW")
    record_scan(user, "cfl_bulb", 0.92, "HIGH")

    stats = get_user_stats(user)
    assert stats["total_scans"] >= 3
    assert stats["hazardous_items"] >= 2
    assert stats["recyclable_items"] >= 1

    # Test filtering by category
    filtered = get_user_history_filtered(user, category="battery")
    assert len(filtered) >= 1
    assert all(r["prediction"] == "battery" for r in filtered)

    # Test CSV export
    csv_str = export_user_history_csv(user)
    assert "Scan ID" in csv_str
    assert "battery" in csv_str

    # Test single deletion
    item_to_delete = filtered[0]["id"]
    deleted = delete_scan(item_to_delete, user)
    assert deleted is True

    # Test clear history
    cleared = clear_user_history(user)
    assert cleared is True
    assert count_user_history_filtered(user) == 0
