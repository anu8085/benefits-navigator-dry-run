# FULL PROJECT RECREATION BLUEPRINT

Use this file when you need to recreate the Benefits Navigator project from scratch during the hackathon.

## Important rule-safety note

- If Claude Code or any AI coding assistant is allowed by the organizers, give this blueprint to that AI along with the master prompt and ask it to build the project one file at a time.
- If AI coding assistants are not allowed, use this as a manual human build specification. Do not use an AI coding assistant if organizers prohibit it.
- The final submitted repo should be created during the official Project Period.
- Do not copy secrets, `.env`, `.local_state`, SQLite DB files, or old Git history.
- Lakebase is the official primary app-state store. SQLite is local fallback only.

## Target architecture

Benefits Navigator is a Streamlit Databricks App that helps a family discover possible benefit programs.

Primary path:

1. Streamlit UI collects user situation.
2. Anthropic Claude extracts a structured family profile and asks clarifying questions.
3. Trusted benefit programs are read from Unity Catalog / Delta through Databricks SQL Warehouse.
4. Python rules engine screens programs and returns explainable matches.
5. Claude generates a plain-language action plan grounded only in matched programs.
6. Lakebase stores intake, matches, action plan, and feedback.
7. Demo analytics SQL summarizes usage and program demand.

Fallback paths:

- If Unity Catalog / SQL Warehouse is unavailable, load `sample_data/programs.json`.
- If Lakebase is unavailable during local testing, write app state to SQLite at `.local_state/benefits_navigator_state.db`.
- If both Lakebase and SQLite fail, still show the generated plan.

## Folder structure to recreate

```text
benefits-navigator/
├── app.py
├── agent.py
├── benefits_rules.py
├── databricks_client.py
├── lakebase_client.py
├── local_state_client.py
├── requirements.txt
├── app.yaml
├── .gitignore
├── README.md
├── sample_data/
│   └── programs.json
├── sql/
│   ├── 01_create_trusted_benefit_programs.sql
│   ├── 02_create_lakebase_tables.sql
│   ├── 03_lakebase_service_principal_grants.sql
│   └── 04_demo_analytics.sql
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   ├── TESTING.md
│   ├── DEMO.md
│   ├── LOCAL_SQLITE_FALLBACK.md
│   └── TROUBLESHOOTING.md
└── tests/
    └── README.md
```

## Required Python dependencies

`requirements.txt`:

```text
streamlit
anthropic
pandas
databricks-sql-connector
psycopg[binary]
databricks-sdk>=0.89.0
```

SQLite uses Python standard library `sqlite3`, so do not add an extra SQLite package.

## `.gitignore`

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
.local_state/
*.db
*.sqlite
*.sqlite3
.DS_Store
.idea/
```

## File-by-file functional specification

### 1. `sample_data/programs.json`

Purpose: local fallback trusted program dataset.

Content: array of 8 New Jersey benefit programs. Each record should include:

- `program_id`
- `program_name`
- `category`
- `description`
- `eligibility_summary`
- `apply_url`
- `apply_phone`
- `source_name`
- `source_url`
- `source_type`
- `state`
- `active_flag`
- `last_verified_date`
- `rule_key`
- `income_limit_pct_fpl`
- `accepts_undocumented`
- `min_child_age`
- `max_child_age`
- `requires_work_or_school`

Recommended programs:

1. NJ SNAP
2. WIC
3. NJ FamilyCare
4. NJ FamilyCare CHIP
5. NJ Child Care Assistance Program
6. NJ Preschool Education Aid
7. LIHEAP / Utility Assistance
8. NJ 2-1-1

### 2. `benefits_rules.py`

Purpose: deterministic, explainable screening engine.

Functions:

#### `load_programs()`

- Opens `sample_data/programs.json`.
- Returns list of program dictionaries.
- Used only when Databricks trusted table is unavailable.

#### `get_fpl_monthly(household_size)`

- Return approximate monthly Federal Poverty Level for household size.
- Use simple dictionary for household sizes 1-8.
- For larger household, add incremental amount.

#### `income_pct_fpl(monthly_income, household_size)`

- If missing income or household size, return `None`.
- Else calculate `(monthly_income / monthly_fpl) * 100`.

#### `screen_programs(profile, programs)`

Input profile fields:

- `household_size`
- `monthly_income`
- `county`
- `state`
- `children_ages`
- `pregnant`
- `needs_food`
- `needs_healthcare`
- `needs_childcare`
- `needs_housing_or_utilities`
- `work_or_school`
- `immigration_concern`

Logic:

- Calculate income percent FPL.
- Iterate through programs.
- For each program, evaluate rule based on `rule_key`.
- Add match reasons as human-readable strings.
- Add `match_score` or confidence if useful.
- Return matched program dictionaries with `match_reasons`.

Rule examples:

- `snap`: match if food need and income appears low enough or unknown.
- `wic`: match if pregnant or child under 5.
- `familycare`: match if healthcare need and income plausibly eligible.
- `chip`: match if children exist and healthcare need.
- `childcare`: match if childcare need and child age <= 13 and work/school.
- `preschool`: match if child age 3 or 4.
- `liheap`: match if utility/housing need and income appears low enough or unknown.
- `nj211`: match as broad navigation/emergency referral.

Do not guarantee eligibility. Say “may qualify” or “worth checking.”

#### `group_by_category(programs)`

- Return dictionary category -> list of programs.

### 3. `agent.py`

Purpose: Anthropic Claude integration for agentic reasoning.

Required environment variable:

- `ANTHROPIC_API_KEY`

Functions:

#### `extract_profile_from_text(user_text)`

- Calls Anthropic Claude.
- Extracts structured JSON profile from raw user text.
- Should handle missing fields as null/false/empty list.
- Must return a Python dictionary.
- Must not invent facts.
- Must include a free-text summary.

Recommended prompt behavior:

- Identify household size, income, children ages, county, state, pregnancy, needs.
- Return JSON only.
- If unknown, use null or empty values.

#### `generate_clarifying_questions(user_text, profile)`

- Calls Claude.
- Generates 2-3 important follow-up questions.
- Questions should fill gaps needed for benefit screening.
- Examples: county, child age, work/school, current benefits, income.
- Return list of strings.

#### `merge_profile_with_answers(profile, questions, answers)`

- Calls Claude or deterministic logic.
- Merges follow-up answers into existing profile.
- Preserve existing known values.
- Return updated dictionary.

#### `generate_action_plan(profile, eligible_programs)`

- Calls Claude.
- Ground response only in matched programs.
- Include recommended first steps, apply URLs/phone numbers, and priority order.
- Use plain language and empathy.
- Include disclaimer: recommendations are not a guarantee of eligibility.
- Return action plan text.

### 4. `databricks_client.py`

Purpose: read trusted benefits data from Unity Catalog through SQL Warehouse.

Environment variables:

- `DATABRICKS_HOST`
- `DATABRICKS_HTTP_PATH`
- `DATABRICKS_TOKEN`
- Optional: `BENEFITS_TABLE`, default `benefits_navigator.trusted.benefit_programs`

Functions:

#### `get_benefit_programs_from_databricks()`

- Validate required env vars.
- Connect using `databricks.sql.connect`.
- Run `SELECT * FROM benefits_navigator.trusted.benefit_programs WHERE active_flag = true`.
- Convert rows to list of dictionaries.
- Close connection.
- On failure, raise exception to caller so `app.py` can fallback to JSON.

Security:

- Never print token.
- Log only safe status messages.

### 5. `lakebase_client.py`

Purpose: primary Lakebase app-state persistence.

Required write functions:

#### `write_family_intake_event(profile, raw_user_text)`

- Generate `intake_id` UUID.
- Insert into `family_intake_events`.
- Store profile as JSON/JSONB.
- Return `intake_id`.

#### `write_program_matches(intake_id, matches)`

- Insert one row per matched program.
- Generate `match_id` UUID.
- Store `match_reasons` as JSON/JSONB.

#### `write_action_plan(intake_id, action_plan_text, generated_by_model)`

- Generate `plan_id` UUID.
- Insert action plan.
- Return `plan_id`.

#### `write_user_feedback(intake_id, rating, feedback_text)`

- Generate `feedback_id` UUID.
- Insert user feedback.
- Return `feedback_id`.

Connection behavior:

- In Databricks App, prefer Lakebase app resource/OAuth credential flow.
- For local testing, allow manual Postgres env vars if available.
- Never log secrets.
- If Lakebase is unavailable, raise exception to caller so `app.py` can fallback to SQLite.

### 6. `local_state_client.py`

Purpose: SQLite fallback app-state persistence for local development only.

Database path:

`.local_state/benefits_navigator_state.db`

Functions:

#### `get_db_path()`

- Return Path object for SQLite DB.
- Create `.local_state` directory if needed.

#### `init_local_db()`

- Create tables if missing:
  - `family_intake_events`
  - `program_matches`
  - `action_plans`
  - `user_feedback`
- Use TEXT columns for JSON-serialized fields.

#### `write_family_intake_event(profile, raw_user_text)`

- Initialize DB.
- Generate intake UUID.
- Insert row.
- Return intake_id.

#### `write_program_matches(intake_id, matches)`

- Insert matched programs.
- Serialize match reasons as JSON.

#### `write_action_plan(intake_id, action_plan_text, generated_by_model)`

- Insert action plan.

#### `write_user_feedback(intake_id, rating, feedback_text)`

- Insert feedback.

#### `write_intake_event(raw_user_text, profile)`

- Alias wrapper for convenience.

#### `write_feedback(intake_id, rating, feedback_text)`

- Alias wrapper for convenience.

#### `get_local_state_counts()`

- Return dictionary of table counts.
- Used only for optional debug expander.

Rules:

- Never store secrets.
- Never commit DB file.
- Warn in logs if running in deployed Databricks App because SQLite is ephemeral there.

### 7. `app.py`

Purpose: Streamlit app orchestration.

Imports:

- `streamlit as st`
- `json`, `os`, `logging`
- `agent`
- `benefits_rules`
- `databricks_client`
- `lakebase_client`
- `local_state_client`

Core functions:

#### `_adapt_databricks_programs(rows)`

- Normalize SQL row dictionaries into program dictionary format expected by `benefits_rules`.
- Convert booleans, numbers, child age fields safely.

#### `load_benefit_programs()`

- Try Databricks first using `databricks_client.get_benefit_programs_from_databricks()`.
- If successful, return `(programs, "databricks")`.
- If failure, load JSON using `benefits_rules.load_programs()` and return `(programs, "json_fallback")`.

Session state keys:

- `step`
- `raw_user_text`
- `profile`
- `questions`
- `answers`
- `matches`
- `action_plan`
- `intake_id`
- `state_storage_mode` with values `lakebase`, `sqlite_fallback`, `none`
- `feedback_saved_where`

UI flow:

1. Title and problem description.
2. Input text area for family situation.
3. Button: “Find Benefits.”
4. Call `extract_profile_from_text`.
5. Call `generate_clarifying_questions`.
6. Show questions and answer fields.
7. Button: “Build My Plan.”
8. Merge profile.
9. Load programs from Databricks or JSON fallback.
10. Screen programs using rules engine.
11. Generate action plan using Claude.
12. Save app state:
    - Try Lakebase first.
    - If Lakebase succeeds, set `state_storage_mode = "lakebase"`.
    - If Lakebase fails, try SQLite.
    - If SQLite succeeds, set `state_storage_mode = "sqlite_fallback"`.
    - If both fail, set `state_storage_mode = "none"`.
13. Show action plan.
14. Show matched program cards.
15. Show state-save message.
16. Feedback form saves feedback to Lakebase first or SQLite fallback.
17. Start Over button clears session state.
18. Optional debug expander if `SHOW_LOCAL_STATE_DEBUG=true`.

Required UI messages:

- Databricks data success: `Using trusted Databricks benefits data.`
- JSON fallback: `Using local fallback benefits data for demo safety.`
- Lakebase success: `Plan saved to Lakebase app-state tables.`
- SQLite fallback: `Plan generated successfully. Lakebase is unavailable, so this session was saved locally in SQLite for demo fallback.`
- No state saved: `Plan generated successfully, but app-state saving failed.`

### 8. `app.yaml`

Purpose: Databricks App deployment configuration.

Template only; do not include real secrets.

Must include command:

```yaml
command: ["streamlit", "run", "app.py"]
```

Must map secrets/resources for:

- `ANTHROPIC_API_KEY`
- `DATABRICKS_HOST`
- `DATABRICKS_HTTP_PATH`
- `DATABRICKS_TOKEN` if needed
- `LAKEBASE_RESOURCE`

Must define resource names consistent with the Databricks App setup.

### 9. SQL files

#### `sql/01_create_trusted_benefit_programs.sql`

- Create catalog/schema/table for trusted benefit programs.
- Insert 8 synthetic/trusted program records.
- Validate row count.

#### `sql/02_create_lakebase_tables.sql`

- Create Lakebase tables:
  - `family_intake_events`
  - `program_matches`
  - `action_plans`
  - `user_feedback`

#### `sql/03_lakebase_service_principal_grants.sql`

- Grant app service principal usage and DML permissions.
- Placeholder: `<APP_SERVICE_PRINCIPAL_CLIENT_ID>`.

#### `sql/04_demo_analytics.sql`

- Query counts.
- Query program demand.
- Query feedback average.
- Create optional `demo_journey_summary` view.

## Rebuild order

1. Create repo and `.gitignore`.
2. Add `requirements.txt`.
3. Add `sample_data/programs.json`.
4. Build `benefits_rules.py`.
5. Build `agent.py`.
6. Build `databricks_client.py`.
7. Build `lakebase_client.py`.
8. Build `local_state_client.py`.
9. Build `app.py` with local JSON + SQLite path first.
10. Test local JSON + SQLite.
11. Add SQL files.
12. Set up Databricks SQL Warehouse and Unity Catalog table.
13. Test local Databricks SQL + SQLite.
14. Set up Lakebase tables.
15. Deploy Databricks App.
16. Add app resources/secrets.
17. Get app service principal ID and run grant SQL.
18. Test Databricks App with Unity Catalog + Lakebase.
19. Run analytics SQL.
20. Record demo video.

## Acceptance criteria

### Local JSON + SQLite

- App starts with `streamlit run app.py`.
- It can generate a plan using JSON benefits data.
- It saves one intake, eight matches, one action plan, and one feedback record to SQLite.
- SQLite count command returns expected rows.

### Local Databricks SQL + SQLite

- App reads 8 programs from Unity Catalog through SQL Warehouse.
- Lakebase is unavailable or disabled locally.
- SQLite saves app state.
- UI says trusted Databricks data and SQLite fallback state.

### Databricks App + Unity Catalog + Lakebase

- App opens through Databricks App URL.
- App reads trusted Databricks benefits data.
- Lakebase writes intake/matches/action plan/feedback.
- Analytics SQL returns rows.

## Local SQLite validation command

```powershell
python -c "import sqlite3; db='.local_state/benefits_navigator_state.db'; conn=sqlite3.connect(db); tables=['family_intake_events','program_matches','action_plans','user_feedback']; [print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]) for t in tables]; conn.close()"
```

Expected after one full test:

```text
family_intake_events 1
program_matches 8
action_plans 1
user_feedback 1
```

## Main test scenario

```text
I am a single mom in New Jersey with two kids ages 3 and 7. I work part-time and make about $1,800 per month. I do not have health insurance right now. I need help with food, childcare, and paying bills.
```

Follow-up answers:

```text
Middlesex County
My 7-year-old is in school. My 3-year-old needs daycare or preschool.
No, I am not currently receiving any government assistance or benefits.
```

Expected result:

- Plan generated.
- 8 programs may be shown depending rules/data.
- Feedback can be saved.
- Correct storage message shown.

## What not to do

- Do not say SQLite is the primary architecture.
- Do not commit `.local_state` or SQLite DB.
- Do not commit `.env` or secrets.
- Do not use real family data.
- Do not claim guaranteed eligibility.
- Do not use old repo as the final submission unless organizers explicitly approve reuse.
