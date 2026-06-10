"""Benefits Navigator for Families — Streamlit app.

Flow: Claude profile extraction -> clarifying questions -> trusted programs
(Unity Catalog first, JSON fallback) -> deterministic rules engine -> Claude
action plan -> state save (Lakebase primary, SQLite fallback). Synthetic data only.
"""
from __future__ import annotations

import logging
import os

import streamlit as st

try:  # local dev convenience: load .env if python-dotenv is installed (never committed)
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001 - .env is optional; deployed app uses real env/secrets
    pass

import agent
import benefits_rules
import databricks_client
import lakebase_client
import local_state_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benefits_navigator")

MSG_DATABRICKS = "Using trusted Databricks benefits data."
MSG_JSON = "Using local fallback benefits data for demo safety."
MSG_LAKEBASE = "Plan saved to Lakebase app-state tables."
MSG_SQLITE = ("Plan generated successfully. Lakebase is unavailable, so this session "
              "was saved locally in SQLite for demo fallback.")
MSG_NOSAVE = "Plan generated successfully, but app-state saving failed."


def load_benefit_programs() -> tuple[list[dict], str]:
    """Databricks Unity Catalog first, JSON fallback second."""
    try:
        programs = databricks_client.get_benefit_programs_from_databricks()
        return programs, "databricks"
    except Exception as exc:  # noqa: BLE001 - intentional broad fallback
        logger.info("Databricks unavailable (%s); using JSON fallback.", type(exc).__name__)
        return benefits_rules.load_programs(), "json_fallback"


def _save_state(profile, raw_text, matches, action_plan) -> tuple[str | None, str]:
    """Try Lakebase, then SQLite. Returns (intake_id, mode)."""
    model = agent.CLAUDE_MODEL
    for backend, mode in ((lakebase_client, "lakebase"), (local_state_client, "sqlite_fallback")):
        try:
            intake_id = backend.write_family_intake_event(profile, raw_text)
            backend.write_program_matches(intake_id, matches)
            backend.write_action_plan(intake_id, action_plan, model)
            return intake_id, mode
        except Exception as exc:  # noqa: BLE001
            logger.info("%s save failed (%s).", mode, type(exc).__name__)
    return None, "none"


def _save_feedback(intake_id, rating, text) -> str:
    for backend, mode in ((lakebase_client, "lakebase"), (local_state_client, "sqlite_fallback")):
        try:
            backend.write_user_feedback(intake_id, rating, text)
            return mode
        except Exception as exc:  # noqa: BLE001
            logger.info("%s feedback save failed (%s).", mode, type(exc).__name__)
    return "none"


def _init_state():
    defaults = {
        "step": "intake", "raw_user_text": "", "profile": {}, "questions": [],
        "matches": [], "action_plan": "", "intake_id": None,
        "state_storage_mode": "none", "data_source": "", "feedback_saved_where": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def main() -> None:
    st.set_page_config(page_title="Benefits Navigator for Families", page_icon="🧭")
    _init_state()
    st.title("🧭 Benefits Navigator for Families")
    st.write("Tell us your situation, and we'll find NJ benefit programs you *may* "
             "qualify for — with clear reasons. This is not a guarantee of eligibility.")

    # Step 1 — intake
    if st.session_state.step == "intake":
        raw = st.text_area("Describe your family's situation:",
                           value=st.session_state.raw_user_text, height=140)
        if st.button("Find Benefits", type="primary") and raw.strip():
            st.session_state.raw_user_text = raw
            with st.spinner("Reading your situation..."):
                st.session_state.profile = agent.extract_profile_from_text(raw)
                st.session_state.questions = agent.generate_clarifying_questions(
                    raw, st.session_state.profile)
            st.session_state.step = "clarify"
            st.rerun()

    # Step 2 — clarifying questions
    elif st.session_state.step == "clarify":
        st.subheader("A few quick questions")
        answers = [st.text_input(q, key=f"ans_{i}")
                   for i, q in enumerate(st.session_state.questions)]
        if st.button("Build My Plan", type="primary"):
            with st.spinner("Building your plan..."):
                st.session_state.profile = agent.merge_profile_with_answers(
                    st.session_state.profile, st.session_state.questions, answers)
                programs, source = load_benefit_programs()
                st.session_state.data_source = source
                st.session_state.matches = benefits_rules.screen_programs(
                    st.session_state.profile, programs)
                st.session_state.action_plan = agent.generate_action_plan(
                    st.session_state.profile, st.session_state.matches)
                intake_id, mode = _save_state(
                    st.session_state.profile, st.session_state.raw_user_text,
                    st.session_state.matches, st.session_state.action_plan)
                st.session_state.intake_id = intake_id
                st.session_state.state_storage_mode = mode
            st.session_state.step = "plan"
            st.rerun()

    # Step 3 — plan + matches + feedback
    elif st.session_state.step == "plan":
        if st.session_state.data_source == "databricks":
            st.success(MSG_DATABRICKS)
        else:
            st.info(MSG_JSON)

        st.subheader("Your action plan")
        st.write(st.session_state.action_plan or "_No plan generated._")

        st.subheader(f"Matched programs ({len(st.session_state.matches)})")
        for m in st.session_state.matches:
            with st.container(border=True):
                st.markdown(f"**{m.get('name')}**  ·  _{m.get('category')}_")
                st.caption(m.get("description", ""))
                for reason in m.get("match_reasons", []):
                    st.markdown(f"- {reason}")
                st.markdown(f"➡️ {m.get('how_to_apply', '')}  ·  {m.get('url', '')}")

        mode = st.session_state.state_storage_mode
        if mode == "lakebase":
            st.success(MSG_LAKEBASE)
        elif mode == "sqlite_fallback":
            st.warning(MSG_SQLITE)
        else:
            st.error(MSG_NOSAVE)

        st.subheader("Was this helpful?")
        rating = st.radio("Rating", ["👍 Yes", "👎 No"], horizontal=True, index=0)
        fb_text = st.text_input("Anything else? (optional)")
        if st.button("Submit feedback") and st.session_state.intake_id:
            where = _save_feedback(st.session_state.intake_id, rating, fb_text)
            st.session_state.feedback_saved_where = where
            st.toast(f"Feedback saved ({where}).")
        if st.session_state.feedback_saved_where:
            st.caption(f"Feedback stored via: {st.session_state.feedback_saved_where}")

        if st.button("Start Over"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Optional local debug
    if os.environ.get("SHOW_LOCAL_STATE_DEBUG", "").lower() == "true":
        with st.expander("Local SQLite state (debug)"):
            st.json(local_state_client.get_local_state_counts())


if __name__ == "__main__":
    main()
