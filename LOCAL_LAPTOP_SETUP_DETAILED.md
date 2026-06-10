# Local Laptop Setup - Detailed Execution Guide

Use this section after the hackathon officially starts and after you create the new repo.
This creates a clean local Python environment so you can test safely before deploying to Databricks Apps.

## 1. Prerequisites to check

Open PowerShell and run:

```powershell
python --version
git --version
```

Recommended Python: 3.11.x or 3.12.x. Your current Python 3.11.4 is fine.

Optional but helpful:

```powershell
code --version
databricks --version
```

If `databricks --version` does not work, that is okay. You can do most setup in the Databricks UI.

## 2. Create working folders

```powershell
mkdir C:\Hackathon\work -Force
cd C:\Hackathon\work
```

Clone your NEW hackathon repo after creating it in GitHub:

```powershell
git clone <NEW_PUBLIC_HACKATHON_REPO_URL>
cd <NEW_REPO_FOLDER>
```

## 3. Create local Python virtual environment

Use one of these. Prefer the first command if `py` works on your laptop.

```powershell
py -3.11 -m venv .venv
```

Fallback:

```powershell
python -m venv .venv
```

## 4. Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this for the current PowerShell window only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Expected prompt should show `(.venv)`.

## 5. Upgrade pip and install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If dependencies fail, capture the error and fix one package at a time. Do not install random packages unless needed.

## 6. Create local environment variables

Create `.env` locally only. Never commit it.

```powershell
notepad .env
```

For local JSON + SQLite fallback testing, you only need Anthropic:

```text
ANTHROPIC_API_KEY=your_anthropic_key_here
BENEFITS_DATA_MODE=json_only
SHOW_LOCAL_STATE_DEBUG=true
```

For local Unity Catalog + SQLite testing, use:

```text
ANTHROPIC_API_KEY=your_anthropic_key_here
BENEFITS_DATA_MODE=databricks_first
DATABRICKS_SERVER_HOSTNAME=<workspace-host-without-https>
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/<warehouse-id>
DATABRICKS_TOKEN=<your_pat_for_local_testing_only>
SHOW_LOCAL_STATE_DEBUG=true
```

Do not set Lakebase variables for SQLite fallback tests.

## 7. Verify `.gitignore`

`.gitignore` must include:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.local_state/
*.db
*.sqlite
*.sqlite3
```

Run:

```powershell
git status
```

Make sure `.env`, `.venv`, `.local_state`, and SQLite DB files are not shown.

## 8. Run local app

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## 9. Check local SQLite fallback rows

After one full test and one feedback submission:

```powershell
python -c "import sqlite3; db='.local_state/benefits_navigator_state.db'; conn=sqlite3.connect(db); tables=['family_intake_events','program_matches','action_plans','user_feedback']; [print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]) for t in tables]; conn.close()"
```

Expected:

```text
family_intake_events 1
program_matches 8
action_plans 1
user_feedback 1
```

## 10. Clean local SQLite state when needed

```powershell
Remove-Item -Recurse -Force .local_state
```

## 11. Commit only safe files

```powershell
git status
git add app.py agent.py benefits_rules.py databricks_client.py lakebase_client.py local_state_client.py requirements.txt README.md sample_data sql docs config .gitignore
git commit -m "Build Benefits Navigator app foundation"
git push
```

Before commit, verify no secrets or local state are included.
