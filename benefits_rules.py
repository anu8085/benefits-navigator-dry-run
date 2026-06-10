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


def screen_programs(profile: dict, programs: list[dict]) -> list[dict]:
    """Return programs the family may qualify for, each with `match_reasons`.

    Triggering is need/situation based (per program id, with tag fallback). Income
    is annotated, not used to silently exclude — we surface "worth confirming".
    """
    p = profile or {}
    pct = income_pct_fpl(p.get("monthly_income"), p.get("household_size"))
    kids = _child_facts(p.get("children_ages"))
    pregnant = bool(p.get("pregnant"))
    work_or_school = bool(p.get("work_or_school"))
    by_id = {prog.get("id"): prog for prog in programs}

    matched: list[dict] = []

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

    def trig(prog_id, condition, reason):
        if condition and prog_id in by_id and prog_id not in {m.get("id") for m in matched}:
            add(by_id[prog_id], [reason])

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
