"""Anthropic Claude integration for agentic reasoning.

The Claude client is created lazily inside each function so this module imports
cleanly with no ANTHROPIC_API_KEY present (needed for offline tests).

Model: defaults to claude-opus-4-8 (override via CLAUDE_MODEL; for a cheaper
demo set CLAUDE_MODEL=claude-sonnet-4-6). Verified against the claude-api
reference: adaptive thinking only, no temperature/top_p, JSON via
output_config.format (NOT assistant prefills).
"""
from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger("benefits_navigator.agent")

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")

_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "household_size": {"type": ["integer", "null"]},
        "monthly_income": {"type": ["number", "null"]},
        "county": {"type": ["string", "null"]},
        "state": {"type": ["string", "null"]},
        "children_ages": {"type": "array", "items": {"type": "integer"}},
        "pregnant": {"type": "boolean"},
        "needs_food": {"type": "boolean"},
        "needs_healthcare": {"type": "boolean"},
        "needs_childcare": {"type": "boolean"},
        "needs_housing_or_utilities": {"type": "boolean"},
        "work_or_school": {"type": "boolean"},
        "immigration_concern": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": [
        "household_size", "monthly_income", "county", "state", "children_ages",
        "pregnant", "needs_food", "needs_healthcare", "needs_childcare",
        "needs_housing_or_utilities", "work_or_school", "immigration_concern", "summary",
    ],
    "additionalProperties": False,
}


def _client():
    from anthropic import Anthropic

    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _json_message(system: str, user_text: str, schema: dict, max_tokens: int = 2000) -> dict:
    """One Claude call returning JSON validated against `schema`."""
    resp = _client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_text}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    return json.loads(text)


def extract_profile_from_text(user_text: str) -> dict:
    """Extract a structured family profile from raw user text. Never invents facts."""
    system = (
        "You extract a structured family profile for a NJ benefits screener. "
        "Only use facts stated by the user. If something is unknown, use null, "
        "false, or an empty list — never guess. Return JSON matching the schema. "
        "`summary` is a one-sentence neutral recap."
    )
    return _json_message(system, user_text, _PROFILE_SCHEMA)


def generate_clarifying_questions(user_text: str, profile: dict) -> list[str]:
    """2-3 follow-up questions that fill the biggest screening gaps."""
    schema = {
        "type": "object",
        "properties": {"questions": {"type": "array", "items": {"type": "string"}}},
        "required": ["questions"],
        "additionalProperties": False,
    }
    system = (
        "Given a user's situation and the extracted profile, ask 2-3 short, kind "
        "follow-up questions that would most improve benefit screening (e.g. county, "
        "child ages, work/school, current benefits, approximate income). Return JSON."
    )
    payload = f"USER SITUATION:\n{user_text}\n\nEXTRACTED PROFILE:\n{json.dumps(profile)}"
    out = _json_message(system, payload, schema, max_tokens=800)
    return out.get("questions", [])[:3]


def merge_profile_with_answers(profile: dict, questions: list[str], answers: list[str]) -> dict:
    """Merge follow-up answers into the profile, preserving known values."""
    qa = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions or [], answers or []))
    system = (
        "Update the family profile using the follow-up answers. Preserve existing "
        "known values unless an answer clearly corrects them. Do not invent facts. "
        "Return JSON matching the schema."
    )
    payload = f"CURRENT PROFILE:\n{json.dumps(profile)}\n\nFOLLOW-UP Q&A:\n{qa}"
    try:
        return _json_message(system, payload, _PROFILE_SCHEMA)
    except Exception as exc:  # noqa: BLE001 - merging is best-effort; keep current profile
        logger.warning("Profile merge failed (%s); keeping current profile.", type(exc).__name__)
        return profile


def generate_action_plan(profile: dict, eligible_programs: list[dict]) -> str:
    """Plain-language action plan grounded ONLY in the matched programs."""
    programs_brief = [
        {
            "name": p.get("name"),
            "category": p.get("category"),
            "how_to_apply": p.get("how_to_apply"),
            "url": p.get("url"),
            "why": p.get("match_reasons", []),
        }
        for p in eligible_programs
    ]
    system = (
        "You are a warm, plain-language benefits navigator for families in New Jersey. "
        "Write a short action plan grounded ONLY in the provided matched programs — do "
        "not mention any program not listed, and do not promise eligibility. Use the "
        "phrase 'may qualify' or 'worth checking'. Give a prioritized first-steps list "
        "with how to apply (URL/phone). End with one sentence: this is not a guarantee "
        "of eligibility."
    )
    payload = (
        f"FAMILY PROFILE:\n{json.dumps(profile)}\n\n"
        f"MATCHED PROGRAMS:\n{json.dumps(programs_brief, indent=2)}"
    )
    resp = _client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=3000,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": payload}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()
