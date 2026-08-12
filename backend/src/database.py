"""
SQLite database for Tara's student memory.
Stores student profiles for the Learning & Literacy track.
Includes Day 6 Outbound Call preferences and Opt-Out handling.
"""

import json
import os
import random
import re
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "tara_memory.db"
)


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database, creating the table if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id          TEXT PRIMARY KEY,
            name             TEXT NOT NULL,
            language_pref    TEXT DEFAULT 'hinglish',
            current_level    TEXT DEFAULT 'beginner',
            topics_covered   TEXT DEFAULT '["basic words", "phonics"]',
            common_mistakes  TEXT DEFAULT '[]',
            last_interaction TEXT,
            opted_out        INTEGER DEFAULT 0
        )
    """)
    # Day 7: Human help escalations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            ref_id       TEXT PRIMARY KEY,
            user_id      TEXT NOT NULL,
            student_name TEXT NOT NULL,
            reason       TEXT NOT NULL,
            urgency      TEXT DEFAULT 'medium',
            summary      TEXT NOT NULL,
            user_consent INTEGER DEFAULT 1,
            status       TEXT DEFAULT 'open',
            created_at   TEXT NOT NULL
        )
    """)
    # Migration: check if opted_out column exists
    cursor = conn.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    if "opted_out" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN opted_out INTEGER DEFAULT 0")

    conn.commit()
    return conn


def lookup_or_create_student(
    user_id: str, display_name: str | None = None
) -> tuple[dict, bool]:
    """Look up a student by user_id. If not found, automatically creates and saves a new student record.
    Returns (student_dict, is_returning_boolean).
    """
    clean_id = user_id.strip().lower()
    name = display_name or user_id.strip().capitalize()
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE user_id = ?", (clean_id,)
        ).fetchone()

        if row is not None:
            # Returning student! Update last_interaction
            conn.execute(
                "UPDATE students SET last_interaction = ? WHERE user_id = ?",
                (now, clean_id),
            )
            conn.commit()
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "language_preference": row["language_pref"],
                "current_level": row["current_level"],
                "topics_covered": json.loads(row["topics_covered"]),
                "common_mistakes": json.loads(row["common_mistakes"]),
                "last_interaction": now,
                "opted_out": bool(row["opted_out"]),
            }, True

        # New student! Auto-create and save record in SQLite database
        default_topics = ["basic words", "phonics practice"]
        default_mistakes = []
        conn.execute(
            """
            INSERT INTO students (user_id, name, language_pref, current_level,
                                  topics_covered, common_mistakes, last_interaction, opted_out)
            VALUES (?, ?, 'hinglish', 'beginner', ?, ?, ?, 0)
            """,
            (
                clean_id,
                name,
                json.dumps(default_topics),
                json.dumps(default_mistakes),
                now,
            ),
        )
        conn.commit()

        return {
            "user_id": clean_id,
            "name": name,
            "language_preference": "hinglish",
            "current_level": "beginner",
            "topics_covered": default_topics,
            "common_mistakes": default_mistakes,
            "last_interaction": now,
            "opted_out": False,
        }, False
    finally:
        conn.close()


def save_student(
    user_id: str,
    name: str,
    language_preference: str = "hinglish",
    current_level: str = "beginner",
    topics_covered: list[str] | None = None,
    common_mistakes: list[str] | None = None,
) -> dict:
    """Update a student record."""
    clean_id = user_id.strip().lower()
    now = datetime.now(timezone.utc).isoformat()
    topics = json.dumps(topics_covered or ["basic words"])
    mistakes = json.dumps(common_mistakes or [])

    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO students (user_id, name, language_pref, current_level,
                                  topics_covered, common_mistakes, last_interaction, opted_out)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                name             = excluded.name,
                language_pref    = excluded.language_pref,
                current_level    = excluded.current_level,
                topics_covered   = excluded.topics_covered,
                common_mistakes  = excluded.common_mistakes,
                last_interaction = excluded.last_interaction
            """,
            (clean_id, name, language_preference, current_level, topics, mistakes, now),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "user_id": clean_id,
        "name": name,
        "language_preference": language_preference,
        "current_level": current_level,
        "topics_covered": topics_covered or [],
        "common_mistakes": common_mistakes or [],
        "last_interaction": now,
        "opted_out": False,
    }


def opt_out_student(user_id: str) -> bool:
    """Opt-out a student from daily outbound practice calls."""
    clean_id = user_id.strip().lower()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "UPDATE students SET opted_out = 1 WHERE user_id = ?", (clean_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def is_opted_out(user_id: str) -> bool:
    """Check if a student has opted out of outbound calls."""
    clean_id = user_id.strip().lower()
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT opted_out FROM students WHERE user_id = ?", (clean_id,)
        ).fetchone()
        if row:
            return bool(row["opted_out"])
        return False
    finally:
        conn.close()


def delete_student(user_id: str) -> bool:
    """Delete a student record (forget-me)."""
    clean_id = user_id.strip().lower()
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM students WHERE user_id = ?", (clean_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ── Day 7: Human Help & Escalation Functions ─────────────────────────


def sanitize_summary(summary: str) -> str:
    """Redact sensitive PII (passwords, OTPs, PINs, phone numbers, card numbers) from summary."""
    clean = summary
    # Passwords / OTP / PIN patterns
    clean = re.sub(
        r"\b(password|pwd|otp|pin|cvv)\s*[:=]\s*\S+",
        r"\1: [REDACTED]",
        clean,
        flags=re.IGNORECASE,
    )
    # 4-6 digit numeric OTPs
    clean = re.sub(r"\b\d{4,6}\b", "[REDACTED_NUMERIC]", clean)
    # 16-digit card numbers
    clean = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[REDACTED_CARD]", clean)
    return clean


def create_escalation_request(
    user_id: str,
    student_name: str,
    reason: str,
    urgency: str = "medium",
    summary: str = "",
    user_consent: bool = True,
) -> dict:
    """Create or update a human help request ticket in SQLite.
    Prevents duplicate open tickets for the same user and reason.
    """
    clean_id = user_id.strip().lower()
    clean_urgency = urgency.lower() if urgency.lower() in ["low", "medium", "high", "emergency"] else "medium"
    sanitized = sanitize_summary(summary)
    now = datetime.now(timezone.utc).isoformat()

    conn = _get_connection()
    try:
        # Prevent duplicate open requests for the same student & reason
        existing = conn.execute(
            """
            SELECT * FROM escalations
            WHERE user_id = ? AND reason = ? AND status = 'open'
            """,
            (clean_id, reason),
        ).fetchone()

        if existing:
            # Update existing open ticket
            ref_id = existing["ref_id"]
            updated_summary = f"{existing['summary']} | Follow-up update: {sanitized}"
            conn.execute(
                """
                UPDATE escalations
                SET summary = ?, urgency = ?, created_at = ?, user_consent = ?
                WHERE ref_id = ?
                """,
                (updated_summary, clean_urgency, now, 1 if user_consent else 0, ref_id),
            )
            conn.commit()
            return {
                "ref_id": ref_id,
                "user_id": clean_id,
                "student_name": student_name,
                "reason": reason,
                "urgency": clean_urgency,
                "summary": updated_summary,
                "status": "open",
                "user_consent": user_consent,
                "is_duplicate_updated": True,
                "created_at": now,
            }

        # Create new escalation ticket
        ref_id = f"ESC-{random.randint(1000, 9999)}"
        conn.execute(
            """
            INSERT INTO escalations (ref_id, user_id, student_name, reason, urgency, summary, user_consent, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                ref_id,
                clean_id,
                student_name,
                reason,
                clean_urgency,
                sanitized,
                1 if user_consent else 0,
                now,
            ),
        )
        conn.commit()

        return {
            "ref_id": ref_id,
            "user_id": clean_id,
            "student_name": student_name,
            "reason": reason,
            "urgency": clean_urgency,
            "summary": sanitized,
            "status": "open",
            "user_consent": user_consent,
            "is_duplicate_updated": False,
            "created_at": now,
        }
    finally:
        conn.close()


def get_open_escalations() -> list[dict]:
    """Retrieve all open human escalation requests for teacher/admin dashboard."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM escalations WHERE status = 'open' ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "ref_id": r["ref_id"],
                "user_id": r["user_id"],
                "student_name": r["student_name"],
                "reason": r["reason"],
                "urgency": r["urgency"],
                "summary": r["summary"],
                "user_consent": bool(r["user_consent"]),
                "status": r["status"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        conn.close()


def get_escalation_by_id(ref_id: str) -> dict | None:
    """Retrieve an escalation request by its reference ID."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM escalations WHERE ref_id = ?", (ref_id.strip().upper(),)
        ).fetchone()
        if row:
            return {
                "ref_id": row["ref_id"],
                "user_id": row["user_id"],
                "student_name": row["student_name"],
                "reason": row["reason"],
                "urgency": row["urgency"],
                "summary": row["summary"],
                "user_consent": bool(row["user_consent"]),
                "status": row["status"],
                "created_at": row["created_at"],
            }
        return None
    finally:
        conn.close()

