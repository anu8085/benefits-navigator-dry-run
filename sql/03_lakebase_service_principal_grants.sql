-- 03_lakebase_service_principal_grants.sql
-- Run after your Databricks App is created/deployed once and you know the App service principal/client ID.
-- Replace <APP_SERVICE_PRINCIPAL_CLIENT_ID> with the actual ID.

GRANT USAGE ON SCHEMA public TO "<APP_SERVICE_PRINCIPAL_CLIENT_ID>";

GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE family_intake_events,
         program_matches,
         action_plans,
         user_feedback
TO "<APP_SERVICE_PRINCIPAL_CLIENT_ID>";

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO "<APP_SERVICE_PRINCIPAL_CLIENT_ID>";

-- Validate permissions by running the app and then checking row counts:
SELECT COUNT(*) AS intake_count FROM family_intake_events;
SELECT COUNT(*) AS match_count FROM program_matches;
SELECT COUNT(*) AS plan_count FROM action_plans;
SELECT COUNT(*) AS feedback_count FROM user_feedback;
