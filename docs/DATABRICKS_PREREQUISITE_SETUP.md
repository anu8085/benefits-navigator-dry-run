# New Databricks Environment Prerequisite Setup

Use this after the hackathon officially starts and after you create your new repo.

## Goal
Prepare a clean Databricks environment for Benefits Navigator.

## Step 1 — SQL Warehouse
1. In Databricks, create or start a small SQL Warehouse.
2. Copy:
   - Workspace hostname without `https://`
   - SQL Warehouse HTTP path
3. Save them for local `.env` and `app.yaml.template`.

Validation SQL:
```sql
SELECT current_catalog(), current_schema(), current_timestamp();
```

## Step 2 — Unity Catalog trusted table
Run:
```text
sql/01_create_trusted_benefit_programs.sql
```
Expected:
```text
total_programs = 12
```

## Step 3 — Local Databricks SQL env values
Create `.env` locally only. Do not commit it.
```powershell
ANTHROPIC_API_KEY=<your-key>
DATABRICKS_SERVER_HOSTNAME=<workspace-hostname-without-https>
DATABRICKS_HTTP_PATH=<sql-warehouse-http-path>
DATABRICKS_TOKEN=<local-test-token>
```

## Step 4 — Lakebase
1. Create Lakebase database/project.
2. Open Lakebase SQL editor or psql connection.
3. Run:
```text
sql/02_create_lakebase_tables.sql
```
Expected: all four tables exist.

## Step 5 — Databricks App
1. Create Databricks App from your GitHub repo.
2. Attach resources/secrets:
   - `anthropic-api-key`
   - `databricks-token` if your app uses token env for SQL Warehouse
   - Lakebase database resource named `lakebase-db`
3. Use `config/app.yaml.template` as the starting point.
4. Deploy once.

## Step 6 — App service principal grants
After first deployment, find the Databricks App service principal/client ID.
Then run:
```text
sql/03_lakebase_service_principal_grants.sql
```
Replace `<APP_SERVICE_PRINCIPAL_CLIENT_ID>` first.

## Step 7 — Final Databricks validation
In the deployed app:
1. Confirm caption: `Using trusted Databricks benefits data`.
2. Run the main test scenario.
3. Submit feedback.
4. Check Lakebase row counts.
5. Run `sql/04_demo_analytics.sql`.
