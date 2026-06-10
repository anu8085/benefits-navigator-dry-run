# PROMPT 03 - IF CLAUDE IS NOT ALLOWED / MANUAL OR ALTERNATE AI RECREATION

Use this only after checking organizer guidance.

If Claude Code or AI coding assistants are allowed, paste this prompt into the allowed AI system together with `docs/FULL_PROJECT_RECREATION_BLUEPRINT.md`.

If AI coding assistants are not allowed, do not paste this into any AI system. Use the blueprint as a manual build checklist and type/build the files yourself during the official Project Period.

## Prompt

You are helping me recreate my hackathon project from scratch during the official Project Period.

Build the project exactly according to `docs/FULL_PROJECT_RECREATION_BLUEPRINT.md`.

Rules:

1. Build one file at a time.
2. Do not skip validation.
3. Do not add unnecessary frameworks.
4. Keep Lakebase as the official primary state store.
5. Keep SQLite as local fallback only.
6. Keep Unity Catalog / Databricks SQL as the primary trusted data path.
7. Keep `sample_data/programs.json` as trusted-data fallback only.
8. Keep Anthropic Claude as the official AI reasoning component.
9. Never create or commit secrets.
10. Never commit `.env`, `.local_state`, or SQLite DB files.
11. Use synthetic data only.
12. Do not claim guaranteed benefit eligibility.

Start with this order:

1. Create `.gitignore`, `requirements.txt`, folders, and `sample_data/programs.json`.
2. Create `benefits_rules.py` and test it against JSON.
3. Create `agent.py` with Anthropic functions.
4. Create `local_state_client.py` and test SQLite counts.
5. Create `databricks_client.py` with JSON fallback handled in app.
6. Create `lakebase_client.py` with write functions.
7. Create `app.py` with local JSON + SQLite working first.
8. Add SQL files.
9. Add `app.yaml` template.
10. Run local tests.
11. Prepare Databricks deployment.

After each file, show:

- file created/modified
- what it does
- command to validate
- expected result
- rollback instruction

Do not continue to the next step until validation passes.
