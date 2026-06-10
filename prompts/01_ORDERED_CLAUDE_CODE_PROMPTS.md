# 01_ORDERED_CLAUDE_CODE_PROMPTS

Use these prompts one at a time after the hackathon officially starts and after you create the new repo.

## Prompt 1 — Validate setup before code
Read `README_FIRST.md`, `00_SIMPLE_EXECUTION_PLAYBOOK.docx` if available, and the latest attached/reference project files. Do not write code yet. Confirm the build plan, required files, local env variables, Databricks prerequisites, and rule-safety risks. Then give me the first 5 commands only.

## Prompt 2 — Create project skeleton
Create the Benefits Navigator project skeleton from scratch in this new repo. Include app.py, agent.py, benefits_rules.py, databricks_client.py, lakebase_client.py, local_state_client.py, requirements.txt, app.yaml.template, sample_data/programs.json, sql files, docs, and .gitignore. Keep the code simple and aligned to the latest reference behavior. Do not include secrets or local DB files. After changes, give validation commands.

## Prompt 3 — Implement local JSON + SQLite fallback first
Implement and validate the fully local path: Streamlit + sample_data/programs.json + Anthropic + SQLite fallback. Lakebase must be attempted first only if configured, but local testing with no Lakebase must save to `.local_state/benefits_navigator_state.db`. Add clear UI messages and docs. Validate with one scenario and SQLite count command.

## Prompt 4 — Add Unity Catalog / Databricks SQL trusted data path
Implement or verify the Databricks SQL connector. The app must load `benefits_navigator.trusted.benefit_programs` first and fall back to sample_data/programs.json if unavailable. Add an adapter from Unity Catalog column names to rules-engine keys. Validate locally using Databricks SQL Warehouse env vars while keeping state in SQLite.

## Prompt 5 — Add Lakebase primary state path
Implement or verify Lakebase writes for intake, matches, action plan, and feedback. Lakebase must be primary, SQLite fallback second. Do not log secrets or raw sensitive data. Provide the Lakebase create-table SQL and grants SQL. Validate locally if Lakebase credentials are available, otherwise validate in Databricks App after deployment.

## Prompt 6 — Create Databricks App deployment files
Create/verify `app.yaml.template`, requirements.txt, and deployment documentation. Do not hardcode old workspace IDs or tokens. Use placeholders for new Databricks environment values. Explain how to attach `anthropic-api-key`, `databricks-token`, and `lakebase-db` resources/secrets.

## Prompt 7 — Run three required tests
Guide me through exactly these tests:
A. Fully local with JSON + SQLite.
B. Local with Unity Catalog via SQL Warehouse + SQLite.
C. Databricks App with Unity Catalog + Lakebase.
For each test, give expected UI messages, commands, SQL row-count checks, and what to screenshot.

## Prompt 8 — Prepare demo and submission
Create final README, Devpost text, 3-minute script, judge testing instructions, screenshots checklist, and likely judge Q&A. Keep SQLite only under local development fallback. Emphasize Databricks App, Unity Catalog, Databricks SQL, Lakebase, Anthropic, rules, and social impact.
