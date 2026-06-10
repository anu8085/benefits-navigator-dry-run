"""Deterministic, explainable benefit screening engine.

Pure Python. No external services, no AI. This is the trustworthy core that
decides which programs a family *may* qualify for, with human-readable reasons.

Defensive about the on-disk schema in sample_data/programs.json:
  shape: {"programs": [ {id, name, category, description, eligibility_notes,
          how_to_apply, url, income_limit_pct_fpL, accepts_undocumented, tags} ]}
Notes:
  - The income field is misspelled `income_limit_pct_fpL` in the data; we read it
    tolerantly (also accept correct spellings).
  - Programs use `tags` + `id`, not `rule_key`. We map by `id` with tag fallback.
  - A limit of 999 means "no income limit".
  - We never guarantee eligibility — reasons say "may qualify" / "worth checking".
"""
from __future__ import annotations

import json
from pathlib import Path

PROGRAMS_JSON = Path(__file__).parent / "sample_data" / "programs.json"

# Approx. 2024 monthly Federal Poverty Level by household size (48 states + DC).
_FPL_MONTHLY = {1: 1255, 2: 1704, 3: 2152, 4: 2600, 5: 3049, 6: 3497, 7: 3945, 8: 4394}
_FPL_INCREMENT = 448  # add per person above 8
_NO_LIMIT = 999


def load_programs() -> list[dict]:
    """Load fallback trusted programs from sample_data/programs.json (the inner list)."""
    with open(PROGRAMS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("programs", [])


def get_fpl_monthly(household_size) -> float | None:
    if not household_size or household_size < 1:
        return None
    if household_size <= 8:
        return float(_FPL_MONTHLY[int(household_size)])
    return float(_FPL_MONTHLY[8] + (int(household_size) - 8) * _FPL_INCREMENT)


def income_pct_fpl(monthly_income, household_size) -> float | None:
    fpl = get_fpl_monthly(household_size)
    if fpl is None or monthly_income is None:
        return None
    return round((float(monthly_income) / fpl) * 100, 1)


def _income_limit(prog: dict) -> int:
    """Read the (misspelled) income limit field tolerantly."""
    for key in ("income_limit_pct_fpl", "income_limit_pct_fpL", "income_limit_pct_FPL"):
        if key in prog and prog[key] is not None:
            try:
                return int(prog[key])
            except (TypeError, ValueError):
                pass
    return _NO_LIMIT


def _income_note(pct: float | None, limit: int) -> str:
    if pct is None:
        return "Income not provided yet — worth checking your eligibility."
    if limit >= _NO_LIMIT:
        return "No income limit for this program."
    if pct <= limit:
        return f"Estimated income ~{pct:.0f}% of the poverty level is within the ~{limit}% guideline."
    return f"Estimated income ~{pct:.0f}% may be above the ~{limit}% guideline — still worth confirming."


def _child_facts(children_ages) -> dict:
    ages = [a for a in (children_ages or []) if isinstance(a, (int, float))]
    return {
        "has_child": bool(ages),
        "under_5": any(a < 5 for a in ages),
        "is_3_or_4": any(a in (3, 4) for a in ages),
        "under_13": any(a < 13 for a in ages),
        "under_19": any(a < 19 for a in ages),
    }


# Canonical rule keys and the keywords that identify each program. This lets
# matching survive different program_id/program_name across sources (JSON vs UC)
# and tables that lack `tags`/`rule_key`. Order matters: more specific first
# (e.g. CHIP before FamilyCare, since CHIP's name also contains "FamilyCare").
_RULE_KEYWORDS = [
    ("snap", ("snap", "supplemental nutrition", "food stamp")),
    ("wic", ("wic", "women, infants", "women infants")),
    ("chip", ("chip", "children's health", "childrens health")),
    ("nj_familycare", ("familycare", "family care", "medicaid")),
    ("ccdf", ("child care", "childcare", "ccdf")),
    ("preschool", ("preschool", "pre-k", "education aid")),
    ("tanf", ("tanf", "workfirst", "work first", "temporary assistance")),
    ("ga", ("general assistance",)),
    ("liheap", ("liheap", "energy assistance", "utility", "heating")),
    ("211nj", ("2-1-1", "211")),
    ("ece_home_visit", ("home visit", "nurse-family", "nurse family", "home visiting")),
    ("dv_services", ("domestic violence",)),
]
_KNOWN_KEYS = {k for k, _ in _RULE_KEYWORDS}


def rule_key_for(prog: dict) -> str | None:
    """Return a canonical rule key for a program, robust to source naming.

    Order: explicit `rule_key` -> `id` (if already canonical) -> keyword match on
    id/name/tags. UC rows may use different program_id values or omit tags/rule_key;
    this normalizes them to the same keys the JSON fallback uses.
    """
    for candidate in (prog.get("rule_key"), prog.get("id")):
        c = str(candidate).strip().lower() if candidate else ""
        if c in _KNOWN_KEYS:
            return c
    # Match on id + name first (descriptive, unambiguous). Tags are only a last
    # resort, because synthesized tags can include generic category words (e.g.
    # "childcare") that would otherwise misroute a program (preschool -> ccdf).
    primary = f"{prog.get('id') or ''} {prog.get('name') or ''}".lower()
    for key, kws in _RULE_KEYWORDS:
        if any(kw in primary for kw in kws):
            return key
    tag_text = " ".join(str(t).lower() for t in (prog.get("tags") or []))
    for key, kws in _RULE_KEYWORDS:
        if any(kw in tag_text for kw in kws):
            return key
    pid = str(prog.get("id")).strip().lower() if prog.get("id") else None
    return pid or None


def screen_programs(profile: dict, programs: list[dict]) -> list[dict]:
    """Return programs the family may qualify for, each with `match_reasons`.

    Triggering is need/situation based, keyed on a canonical rule key (see
    `rule_key_for`) so JSON and Unity Catalog produce identical matches. Income
    is annotated, not used to silently exclude — we surface "worth confirming".
    """
    p = profile or {}
    pct = income_pct_fpl(p.get("monthly_income"), p.get("household_size"))
    kids = _child_facts(p.get("children_ages"))
    pregnant = bool(p.get("pregnant"))
    work_or_school = bool(p.get("work_or_school"))

    by_key: dict[str, dict] = {}
    for prog in programs:
        key = rule_key_for(prog)
        if key and key not in by_key:
            by_key[key] = prog

    matched: list[dict] = []
    used: set[str] = set()

    def add(prog: dict, reasons: list[str]):
        if prog is None:
            return
        limit = _income_limit(prog)
        full_reasons = list(reasons) + [_income_note(pct, limit)]
        if p.get("immigration_concern") and not prog.get("accepts_undocumented", False):
            full_reasons.append(
                "Note: this program may ask about immigration status — NJ 2-1-1 can suggest safer options."
            )
        item = dict(prog)
        item["match_reasons"] = full_reasons
        matched.append(item)

    def trig(key, condition, reason):
        if condition and key in by_key and key not in used:
            used.add(key)
            add(by_key[key], [reason])

    trig("snap", p.get("needs_food"), "You mentioned needing help with food.")
    trig("wic", pregnant or kids["under_5"],
         "WIC supports pregnant parents and young children under 5.")
    trig("nj_familycare", p.get("needs_healthcare") or pregnant or kids["has_child"],
         "Health coverage for families, children, and pregnant parents.")
    trig("chip", kids["under_19"] and p.get("needs_healthcare"),
         "Low-cost health coverage specifically for children.")
    trig("ccdf", p.get("needs_childcare") and kids["under_13"] and work_or_school,
         "Childcare help for working/studying parents with children under 13.")
    trig("preschool", kids["is_3_or_4"],
         "Free preschool option for 3- and 4-year-olds.")
    trig("tanf", kids["has_child"] and (pct is None or pct <= 60),
         "Cash assistance and work support for low-income families with children.")
    trig("ga", (not kids["has_child"]) and (pct is not None and pct <= 40),
         "Cash assistance for low-income adults without children.")
    trig("liheap", p.get("needs_housing_or_utilities"),
         "You mentioned needing help with bills/utilities.")
    trig("ece_home_visit", pregnant,
         "Free nurse home-visiting support during pregnancy and early infancy.")
    # Universal safety net — always offer the referral hotline.
    trig("211nj", True, "NJ 2-1-1 is a free 24/7 helpline that can connect you to more local help.")

    return matched


def group_by_category(programs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for prog in programs:
        out.setdefault(prog.get("category", "Other"), []).append(prog)
    return out
