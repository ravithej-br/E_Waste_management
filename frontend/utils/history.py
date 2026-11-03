"""
frontend/utils/history.py
─────────────────────────
Dedicated audit history service for EcoScan AI.
Enforces the Zero Disk Leak Privacy Promise:
  - Only stores scan result metadata (prediction, confidence, hazard level, timestamp).
  - Never stores raw image bytes or file uploads.
  - Supports filtering, pagination, CSV export, single deletion, and full history purge.
"""

import io
import csv
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "users.db"


def _get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def record_scan(username: str, prediction: str, confidence: float, hazard_level: str) -> bool:
    """Logs an authenticated scan metadata to the scan_history table."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scan_history (username, prediction, confidence, hazard_level)
                VALUES (?, ?, ?, ?)
                """,
                (username, prediction, round(float(confidence), 4), hazard_level),
            )
            conn.commit()
            return True
    except Exception:
        return False


def get_user_history(username: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Legacy helper returning newest scans for a user."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, prediction, confidence, hazard_level, scanned_at
                FROM scan_history
                WHERE username = ?
                ORDER BY scanned_at DESC, id DESC
                LIMIT ?
                """,
                (username, limit),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def get_user_stats(username: str) -> Dict[str, Any]:
    """
    Computes summary metrics for user's profile card and dashboard:
    - total scans
    - hazardous items (CRITICAL, HIGH)
    - recyclable items (LOW, MODERATE, or accepted classes)
    - most common category
    """
    stats = {
        "total_scans": 0,
        "hazardous_items": 0,
        "recyclable_items": 0,
        "top_category": "None",
    }
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM scan_history WHERE username = ?",
                (username,)
            )
            stats["total_scans"] = cursor.fetchone()[0] or 0

            cursor.execute(
                """
                SELECT COUNT(*) FROM scan_history
                WHERE username = ? AND (UPPER(hazard_level) LIKE '%CRITICAL%' OR UPPER(hazard_level) LIKE '%HIGH%')
                """,
                (username,)
            )
            stats["hazardous_items"] = cursor.fetchone()[0] or 0

            cursor.execute(
                """
                SELECT COUNT(*) FROM scan_history
                WHERE username = ? AND (UPPER(hazard_level) LIKE '%LOW%' OR UPPER(hazard_level) LIKE '%MODERATE%')
                """,
                (username,)
            )
            stats["recyclable_items"] = cursor.fetchone()[0] or 0

            cursor.execute(
                """
                SELECT prediction, COUNT(*) as cnt
                FROM scan_history
                WHERE username = ?
                GROUP BY prediction
                ORDER BY cnt DESC
                LIMIT 1
                """,
                (username,)
            )
            row = cursor.fetchone()
            if row:
                stats["top_category"] = row["prediction"].replace("_", " ").title()
    except Exception:
        pass

    return stats


def get_user_history_filtered(
    username: str,
    category: Optional[str] = None,
    hazard_level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Retrieves filtered, paginated audit records for a given user sorted newest first.
    """
    query = "SELECT id, prediction, confidence, hazard_level, scanned_at FROM scan_history WHERE username = ?"
    params: List[Any] = [username]

    if category and category != "All":
        query += " AND prediction = ?"
        params.append(category)

    if hazard_level and hazard_level != "All":
        query += " AND UPPER(hazard_level) LIKE ?"
        params.append(f"%{hazard_level.upper()}%")

    if date_from:
        query += " AND DATE(scanned_at) >= DATE(?)"
        params.append(str(date_from))

    if date_to:
        query += " AND DATE(scanned_at) <= DATE(?)"
        params.append(str(date_to))

    if search_query:
        query += " AND (prediction LIKE ? OR hazard_level LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    query += " ORDER BY scanned_at DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def count_user_history_filtered(
    username: str,
    category: Optional[str] = None,
    hazard_level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search_query: Optional[str] = None,
) -> int:
    """Returns the total number of records matching the filter criteria."""
    query = "SELECT COUNT(*) FROM scan_history WHERE username = ?"
    params: List[Any] = [username]

    if category and category != "All":
        query += " AND prediction = ?"
        params.append(category)

    if hazard_level and hazard_level != "All":
        query += " AND UPPER(hazard_level) LIKE ?"
        params.append(f"%{hazard_level.upper()}%")

    if date_from:
        query += " AND DATE(scanned_at) >= DATE(?)"
        params.append(str(date_from))

    if date_to:
        query += " AND DATE(scanned_at) <= DATE(?)"
        params.append(str(date_to))

    if search_query:
        query += " AND (prediction LIKE ? OR hazard_level LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()[0] or 0
    except Exception:
        return 0


def delete_scan(scan_id: int, username: str) -> bool:
    """Permanently deletes a single scan record belonging to the user."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM scan_history WHERE id = ? AND username = ?",
                (scan_id, username)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception:
        return False


def clear_user_history(username: str) -> bool:
    """Purges all audit history records for the specified user."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM scan_history WHERE username = ?",
                (username,)
            )
            conn.commit()
            return True
    except Exception:
        return False


def export_user_history_csv(username: str) -> str:
    """Exports all scan records for a user as a CSV formatted string."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, scanned_at, prediction, confidence, hazard_level
                FROM scan_history
                WHERE username = ?
                ORDER BY scanned_at DESC, id DESC
                """,
                (username,)
            )
            rows = cursor.fetchall()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Scan ID", "Timestamp (UTC)", "Material Class", "Calibrated Confidence", "Hazard Level"])
            for r in rows:
                writer.writerow([
                    r["id"],
                    r["scanned_at"],
                    r["prediction"],
                    f"{r['confidence'] * 100:.2f}%",
                    r["hazard_level"]
                ])
            return output.getvalue()
    except Exception as e:
        return f"Error exporting CSV: {str(e)}"
