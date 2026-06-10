# Environment Variables (standardized)

All environment variables used by Benefits Navigator. **Secrets live only in a
local `.env` (gitignored) or in Databricks App secret resources — never in code
or committed files.**

## Standardized naming decision

We use **`DATABRICKS_SERVER_HOSTNAME`** for the SQL Warehouse host, because that
is what the V9 playbook (`docs/LOCAL_LAPTOP_SETUP_DETAILED.md`) uses. The older
blueprint name `DATABRICKS_HOST` is **deprecated** in this repo. Code, the
deployment template (`app.yaml.template`), and docs all use
`DATABRICKS_SERVER_HOSTNAME`.

## Anthropic (always required)

| Var | Example | Notes |
|-----|---------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Claude reasoning. Secret. |
| `CLAUDE_MODEL` | (optional) | Overrides default model id. Confirmed in Prompt 3. |

## Databricks SQL Warehouse / Unity Catalog (trusted data path)

| Var | Example | Notes |
|-----|---------|-------|
| `DATABRICKS_SERVER_HOSTNAME` | `dbc-xxxx.cloud.databricks.com` | Host **without** `https://`. |
| `DATABRICKS_HTTP_PATH` | `/sql/1.0/warehouses/<warehouse-id>` | From the SQL Warehouse connection details. |
| `DATABRICKS_TOKEN` | `dapi...` | PAT — **local testing only**. Secret. |
| `BENEFITS_TABLE` | `benefits_navigator.trusted.benefit_programs` | Optional override. |

## Lakebase (primary app-state, Prompt 5)

| Var | Notes |
|-----|-------|
| `LAKEBASE_HOST` / `LAKEBASE_DB` / `LAKEBASE_USER` / `LAKEBASE_PASSWORD` | Local Postgres testing. In a deployed app, prefer the Lakebase app-resource/OAuth flow. Secrets. |

## App behavior flags

| Var | Values | Notes |
|-----|--------|-------|
| `BENEFITS_DATA_MODE` | `json_only` \| `databricks_first` | Data source preference. |
| `SHOW_LOCAL_STATE_DEBUG` | `true` \| `false` | Shows the SQLite debug expander locally. |

## Example local `.env` (DO NOT COMMIT)

```text
ANTHROPIC_API_KEY=your_anthropic_key_here
BENEFITS_DATA_MODE=json_only
SHOW_LOCAL_STATE_DEBUG=true
```
