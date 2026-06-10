"""Read trusted benefits data from Unity Catalog via Databricks SQL Warehouse.

Env vars (standardized to match the playbook):
  - DATABRICKS_SERVER_HOSTNAME   (host without https://)
  - DATABRICKS_HTTP_PATH         (e.g. /sql/1.0/warehouses/<id>)
  - DATABRICKS_TOKEN             (PAT, local testing only)
  - BENEFITS_TABLE               (optional; default below)

The UC table uses different column names than sample_data/programs.json, so
`adapt_databricks_programs()` normalizes rows into the shape the rules engine
and UI expect (matching the JSON fallback shape exactly).

Security: never print or log the token.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("benefits_navigator.databricks")

DEFAULT_BENEFITS_TABLE = "benefits_navigator.trusted.benefit_programs"
REQUIRED_ENV = ("DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN")


def _missing_env() -> list[str]:
    return [k for k in REQUIRED_ENV if not os.environ.get(k)]


def adapt_databricks_programs(rows: list[dict]) -> list[dict]:
    """Map Unity Catalog rows -> the program dict used by benefits_rules and the UI.

    UC columns -> normalized keys:
      program_id -> id, program_name -> name, eligibility_summary -> eligibility_notes,
      apply_url(+apply_phone) -> how_to_apply / url, income_limit_pct_fpl -> (same).
    Extra UC-only columns (min/max_child_age, requires_work_or_school) are carried
    through harmlessly; the deterministic rules engine ignores unknown keys.
    """
    out: list[dict] = []
    for r in rows:
        apply_url = (r.get("apply_url") or "").strip()
        phone = (r.get("apply_phone") or "").strip()
        if apply_url and phone:
            how_to_apply = f"Apply at {apply_url} or call {phone}."
        elif apply_url:
            how_to_apply = f"Apply at {apply_url}."
        elif phone:
            how_to_apply = f"Call {phone}."
        else:
            how_to_apply = ""
        out.append(
            {
                "id": r.get("program_id"),
                "name": r.get("program_name"),
                "category": r.get("category"),
                "description": r.get("description"),
                "eligibility_notes": r.get("eligibility_summary"),
                "how_to_apply": how_to_apply,
                "url": apply_url,
                "income_limit_pct_fpl": r.get("income_limit_pct_fpl"),
                "accepts_undocumented": bool(r.get("accepts_undocumented")),
                "tags": [t for t in [r.get("category"), r.get("rule_key")] if t],
                # carried through (unused by rules, available if needed):
                "rule_key": r.get("rule_key"),
                "state": r.get("state"),
            }
        )
    return out


def get_benefit_programs_from_databricks() -> list[dict]:
    """Return active trusted programs (normalized) as a list of dicts.

    Raises on any failure (missing env, connection/query error, or zero rows) so
    the caller can fall back to sample_data/programs.json.
    """
    missing = _missing_env()
    if missing:
        raise RuntimeError(f"Databricks env not configured: missing {', '.join(missing)}")

    from databricks import sql  # lazy import: keeps module import light/offline-safe

    host = os.environ["DATABRICKS_SERVER_HOSTNAME"]
    http_path = os.environ["DATABRICKS_HTTP_PATH"]
    token = os.environ["DATABRICKS_TOKEN"]
    table = os.environ.get("BENEFITS_TABLE", DEFAULT_BENEFITS_TABLE)

    logger.info("Connecting to Databricks SQL warehouse host=%s", host)  # never log token
    conn = sql.connect(server_hostname=host, http_path=http_path, access_token=token)
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table} WHERE active_flag = true")
            columns = [c[0] for c in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()

    programs = adapt_databricks_programs(rows)
    if not programs:
        raise RuntimeError("Databricks returned 0 active programs")
    logger.info("Loaded %d trusted programs from Databricks.", len(programs))
    return programs
