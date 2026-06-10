# Simple Testing Guide

## Test A — Fully local fallback
Purpose: prove the app works even if Databricks/Lakebase are unavailable.

Setup:
- `.env` has only `ANTHROPIC_API_KEY`.
- No `DATABRICKS_*` values.
- No `LAKEBASE_*` values.

Run:
```powershell
streamlit run app.py
```
Expected UI:
- `Using local fallback benefits data`
- After plan: `Lakebase is unavailable, so this session was saved locally in SQLite for demo fallback.`
- After feedback: `Saved locally in SQLite for demo fallback.`

SQLite count check:
```powershell
python -c "import sqlite3; db='.local_state/benefits_navigator_state.db'; conn=sqlite3.connect(db); tables=['family_intake_events','program_matches','action_plans','user_feedback']; [print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]) for t in tables]; conn.close()"
```

## Test B — Local with Unity Catalog + SQLite
Purpose: prove trusted Databricks data works locally while still using SQLite fallback for state.

Setup `.env`:
```powershell
ANTHROPIC_API_KEY=<key>
DATABRICKS_SERVER_HOSTNAME=<host>
DATABRICKS_HTTP_PATH=<path>
DATABRICKS_TOKEN=<token>
```
Do not set Lakebase env values.

Expected UI:
- `Using trusted Databricks benefits data`
- After plan: SQLite fallback save message.

## Test C — Databricks App with Unity Catalog + Lakebase
Purpose: final hackathon path.

Expected UI:
- `Using trusted Databricks benefits data`
- After plan: `Plan saved to Lakebase app-state tables.`
- Feedback: `Saved to Lakebase.`

Validate Lakebase counts:
```sql
SELECT COUNT(*) AS intake_count FROM family_intake_events;
SELECT COUNT(*) AS match_count FROM program_matches;
SELECT COUNT(*) AS plan_count FROM action_plans;
SELECT COUNT(*) AS feedback_count FROM user_feedback;
```

## Main scenario
```text
I am a single mom in New Jersey with two kids ages 3 and 7. I work part-time and make about $1,800 per month. I do not have health insurance right now. I need help with food, childcare, and paying bills.
```
Follow-up answers:
```text
Middlesex County
My 7-year-old is in school. My 3-year-old needs daycare or preschool.
No, I am not currently receiving any government assistance or benefits.
```
Expected:
- Plan generated.
- Around 8 matched programs for the main demo scenario.
- Intake, matches, action plan, and feedback persisted in selected state layer.

## Scenario Set — V9 detailed cases

Run these in local JSON + SQLite, local Unity Catalog + SQLite, and deployed Databricks App + Unity Catalog + Lakebase when time allows.

### Scenario 1 — Main winning demo: single mom with two kids
Input: I am a single mom in New Jersey with two kids ages 3 and 7. I work part-time and make about $1,800 per month. I do not have health insurance right now. I need help with food, childcare, and paying bills.
Follow-ups: Middlesex County / My 7-year-old is in school. My 3-year-old needs daycare or preschool. / No, I am not currently receiving any government assistance or benefits.
Expected: SNAP, WIC, NJ FamilyCare, childcare assistance, preschool, utility/support programs, and clear next steps.

### Scenario 2 — Pregnant mother needing groceries and health coverage
Input: I live in New Jersey and I am pregnant. I work part-time and make around $2,200 per month. I need help with groceries and health coverage. I am not sure what programs I can apply for.
Expected: WIC, NJ FamilyCare, SNAP if applicable, source-grounded action plan, and pregnancy-sensitive next steps.

### Scenario 3 — Higher-income family needing child health coverage
Input: We are a family of four in New Jersey. Our monthly income is about $7,500. Our kids are 8 and 14. We mainly need affordable health insurance options for the children.
Expected: child health coverage guidance if present in trusted data, realistic explanation, and no guaranteed eligibility claim.

### Scenario 4 — Utility bill emergency
Input: I live alone in New Jersey. I lost work hours recently and I am behind on my utility bill. I need help keeping my heat and electricity on.
Expected: LIHEAP or utility assistance programs, 2-1-1 / emergency support guidance, and urgent next steps.

### Scenario 5 — Childcare-focused working parent
Input: I am a working parent in New Jersey with one child age 4. I work full-time and pay a lot for daycare. My monthly income is about $3,200. I need help with childcare costs.
Expected: Child Care Assistance Program, preschool-related options if present, and practical application guidance.

### Scenario 6 — Immigration-sensitive family
Input: I am a parent in New Jersey with a 3-year-old child. I am worried about applying because not everyone in my household has the same immigration status. We need food and preschool help.
Expected: careful, non-legal guidance, source-grounded program suggestions, and recommendation to verify eligibility with official sources/local assistance.

### Scenario 7 — Senior or disabled adult needing healthcare and bills support
Input: I am an older adult in New Jersey living on a fixed income. I need help with healthcare costs, prescriptions, groceries, and utility bills.
Expected: healthcare/help-with-bills/grocery support programs that exist in trusted data, plus safe next steps.

### Scenario 8 — Negative/control test: user may not qualify for many programs
Input: I live in New Jersey with my spouse and two children. Our monthly income is about $14,000. We are not in an emergency, but I want to know if there are any child or family programs we should check.
Expected: fewer matches, careful wording, no forced eligibility claims, and suggestions to check official sources.

### Pass criteria for every scenario
- Useful follow-up questions when needed.
- Matches come from trusted data or approved fallback data only.
- Action plan is specific and understandable.
- No guaranteed eligibility claims.
- State saves to SQLite locally or Lakebase in deployed Databricks App.
- Feedback save works.
- No secret/token/debug leakage in UI.
