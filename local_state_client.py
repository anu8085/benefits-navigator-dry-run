"""SQLite fallback app-state persistence — LOCAL DEVELOPMENT/DEMO ONLY.

This is NOT the primary store. Lakebase is primary (lakebase_client.py). SQLite
exists only so local demos still persist state when Lakebase is unavailable.

DB path: .local_state/benefits_navigator_state.db  (gitignored, never committed)
JSON-ish fields are stored as TEXT (json.dumps). Never store secrets here.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("benefits_navigator.sqlite")

DB_DIR = Path(__file__).parent / ".local_state"
DB_PATH = DB_DIR / "benefits_navigator_state.db"
TABLES = ("family_intake_events", "program_matches", "action_plans", "user_feedback")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db_path() -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(get_db_path())


def init_local_db() -> None:
    """Create the four state tables if missing."""
    if os.environ.get("DATABRICKS_APP_NAME") or os.environ.get("DATABRICKS_WORKSPACE_ID"):
        logger.warning("SQLite fallback in a deployed Databricks App is ephemeral; prefer Lakebase.")
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS family_intake_events (
                intake_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                raw_user_text TEXT,
                profile_json TEXT
            );
            CREATE TABLE IF NOT EXISTS program_matches (
                match_id TEXT PRIMARY KEY,
                intake_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                program_id TEXT,
                program_name TEXT,
                match_reasons_json TEXT
            );
            CREATE TABLE IF NOT EXISTS action_plans (
                plan_id TEXT PRIMARY KEY,
                intake_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                action_plan_text TEXT,
                generated_by_model TEXT
            );
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                intake_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                rating TEXT,
                feedback_text TEXT
            );
            """
        )


def write_family_intake_event(profile: dict, raw_user_text: str) -> str:
    init_local_db()
    intake_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO family_intake_events (intake_id, created_at, raw_user_text, profile_json) "
            "VALUES (?, ?, ?, ?)",
            (intake_id, _now(), raw_user_text, json.dumps(profile or {})),
        )
    return intake_id


def write_program_matches(intake_id: str, matches: list[dict]) -> None:
    init_local_db()
    with _connect() as conn:
        for m in matches or []:
            conn.execute(
                "INSERT INTO program_matches "
                "(match_id, intake_id, created_at, program_id, program_name, match_reasons_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    intake_id,
                    _now(),
                    m.get("id"),
                    m.get("name"),
                    json.dumps(m.get("match_reasons", [])),
                ),
            )


def write_action_plan(intake_id: str, action_plan_text: str, generated_by_model: str) -> str:
    init_local_db()
    plan_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO action_plans (plan_id, intake_id, created_at, action_plan_text, generated_by_model) "
            "VALUES (?, ?, ?, ?, ?)",
            (plan_id, intake_id, _now(), action_plan_text, generated_by_model),
        )
    return plan_id


def write_user_feedback(intake_id: str, rating, feedback_text: str) -> str:
    init_local_db()
    feedback_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO user_feedback (feedback_id, intake_id, created_at, rating, feedback_text) "
            "VALUES (?, ?, ?, ?, ?)",
            (feedback_id, intake_id, _now(), str(rating), feedback_text),
        )
    return feedback_id


# Convenience aliases (match reference behavior).
def write_intake_event(raw_user_text: str, profile: dict) -> str:
    return write_family_intake_event(profile, raw_user_text)


def write_feedback(intake_id: str, rating, feedback_text: str) -> str:
    return write_user_feedback(intake_id, rating, feedback_text)


def get_local_state_counts() -> dict[str, int]:
    if not DB_PATH.exists():
        return {t: 0 for t in TABLES}
    counts = {}
    with _connect() as conn:
        for t in TABLES:
            try:
                counts[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except sqlite3.OperationalError:
                counts[t] = 0
    return counts
