# Databricks Prerequisite Setup Prompt for Claude

Help me complete the new Databricks environment setup for Benefits Navigator. Do not code until each prerequisite is validated.

I need you to guide me through:
1. SQL Warehouse creation/start and connection details.
2. Unity Catalog catalog/schema/table creation using `sql/01_create_trusted_benefit_programs.sql`.
3. Validation that the trusted table has 12 programs.
4. Lakebase database/project creation.
5. Lakebase tables using `sql/02_create_lakebase_tables.sql`.
6. Databricks App creation from my new GitHub repo.
7. App resources/secrets: `anthropic-api-key`, `databricks-token` if needed, `lakebase-db`.
8. First app deployment.
9. Capture Databricks App service principal/client ID.
10. Lakebase grants using `sql/03_lakebase_service_principal_grants.sql`.
11. Final Databricks App test with Unity Catalog + Lakebase.

For each step, give exact UI path, commands/SQL, validation, expected result, and fallback if it fails.
