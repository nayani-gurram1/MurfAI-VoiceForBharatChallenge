"""
SQLite database for Tara's student memory.
Stores student profiles for the Learning & Literacy track.
"""

import json
import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tara_memory.db")


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database, creating the table if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id         TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            language_pref   TEXT DEFAULT 'hinglish',
            current_level   TEXT DEFAULT 'beginner',
            topics_covered  TEXT DEFAULT '["basic words", "phonics"]',
            common_mistakes TEXT DEFAULT '[]',
            last_interaction TEXT
        )
    """)
    conn.commit()
    return conn


def lookup_or_create_student(user_id: str, display_name: str | None = None) -> tuple[dict, bool]:
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
            }, True

        # New student! Auto-create and save record in SQLite database
        default_topics = ["basic words", "phonics practice"]
        default_mistakes = []
        conn.execute(
            """
            INSERT INTO students (user_id, name, language_pref, current_level,
                                  topics_covered, common_mistakes, last_interaction)
            VALUES (?, ?, 'hinglish', 'beginner', ?, ?, ?)
            """,
            (clean_id, name, json.dumps(default_topics), json.dumps(default_mistakes), now),
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
                                  topics_covered, common_mistakes, last_interaction)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name            = excluded.name,
                language_pref   = excluded.language_pref,
                current_level   = excluded.current_level,
                topics_covered  = excluded.topics_covered,
                common_mistakes = excluded.common_mistakes,
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
    }


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
