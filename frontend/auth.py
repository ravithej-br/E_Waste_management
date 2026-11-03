"""
frontend/auth.py
────────────────
Lightweight SQLite authentication service for E-Waste Classification System.
Handles user registration, login verification, password hashing, and scan history.
"""

import sys
import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "users.db"


def _get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes users and scan history database tables."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                hazard_level TEXT NOT NULL,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

    # Create default demo user if not exists
    create_demo_user_if_needed()


def _hash_password(password: str, salt: str) -> str:
    """PBKDF2 HMAC SHA-256 password hashing."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000,
    ).hex()


def register_user(username: str, email: str, full_name: str, password: str) -> Tuple[bool, str]:
    """Registers a new user in the database."""
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip()

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if not full_name:
        return False, "Please enter your full name."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, email, full_name, password_hash, salt)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, full_name, password_hash, salt),
            )
            conn.commit()
        return True, "Account registered successfully! You can now log in."
    except sqlite3.IntegrityError as e:
        if "users.username" in str(e):
            return False, "Username is already taken. Please choose another."
        elif "users.email" in str(e):
            return False, "An account with this email already exists."
        return False, "Username or email already registered."
    except Exception as e:
        return False, f"Registration error: {str(e)}"


def authenticate_user(identifier: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """Authenticates by username or email and returns user profile dict."""
    identifier = identifier.strip().lower()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, email, full_name, password_hash, salt, created_at
            FROM users
            WHERE username = ? OR email = ?
            """,
            (identifier, identifier),
        )
        row = cursor.fetchone()

        if not row:
            return False, None

        stored_hash = row["password_hash"]
        salt = row["salt"]

        calc_hash = _hash_password(password, salt)
        if secrets.compare_digest(stored_hash, calc_hash):
            user_data = {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "full_name": row["full_name"],
                "created_at": str(row["created_at"]),
            }
            return True, user_data

    return False, None


def create_demo_user_if_needed():
    """Ensures a default demo user is readily available for instant evaluation."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'demo'")
        if not cursor.fetchone():
            salt = secrets.token_hex(16)
            p_hash = _hash_password("demo123", salt)
            cursor.execute(
                """
                INSERT INTO users (username, email, full_name, password_hash, salt)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("demo", "demo@ewaste.org", "Demo Researcher", p_hash, salt),
            )
            conn.commit()


from frontend.utils.history import record_scan, get_user_history


# Auto-initialize database on import
init_db()
