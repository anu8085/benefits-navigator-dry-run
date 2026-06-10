"""Primary Lakebase (Postgres) app-state persistence.

Lakebase is the OFFICIAL primary app-state store. SQLite is only a local
fallback (see local_state_client.py).

SKELETON (Prompt 2): writes implemented in Prompt 5. Each stub raises so app.py
falls back to SQLite during local testing.

Security: never log secrets or raw sensitive data.
"""
from __future__ import annotations

import os

# In a deployed Databricks App, prefer the Lakebase app-resource / OAuth flow.
# For local testing, manual Postgres env vars may be provided.
REQUIRED_ENV = ("LAKEBASE_HOST", "LAKEBASE_DB", "LAKEBASE_USER", "LAKEBASE_PASSWORD")


def _is_configured() -> bool:
    return all(os.environ.get(k) for k in REQUIRED_ENV)


def _not_ready():
    raise RuntimeError("Lakebase not configured/available (implemented in Prompt 5)")


def write_family_intake_event(profile: dict, raw_user_text: str) -> str:
    """Insert intake event; return intake_id (UUID). TODO(Prompt 5)."""
    _not_ready()


def write_program_matches(intake_id: str, matches: list[dict]) -> None:
    """Insert one row per matched program. TODO(Prompt 5)."""
    _not_ready()


def write_action_plan(intake_id: str, action_plan_text: str, generated_by_model: str) -> str:
    """Insert action plan; return plan_id (UUID). TODO(Prompt 5)."""
    _not_ready()


def write_user_feedback(intake_id: str, rating, feedback_text: str) -> str:
    """Insert feedback; return feedback_id (UUID). TODO(Prompt 5)."""
    _not_ready()
