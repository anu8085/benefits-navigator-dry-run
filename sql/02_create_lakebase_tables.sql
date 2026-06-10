-- 02_create_lakebase_tables.sql
-- Run in Lakebase/Postgres SQL editor for your NEW hackathon Lakebase database.
-- This is the primary durable app-state schema.

CREATE TABLE IF NOT EXISTS family_intake_events (
  intake_id TEXT PRIMARY KEY,
  event_ts TIMESTAMPTZ DEFAULT now(),
  raw_user_text TEXT,
  profile JSONB
);

CREATE TABLE IF NOT EXISTS program_matches (
  match_id TEXT PRIMARY KEY,
  intake_id TEXT REFERENCES family_intake_events(intake_id),
  event_ts TIMESTAMPTZ DEFAULT now(),
  program_id TEXT,
  program_name TEXT,
  category TEXT,
  match_reasons JSONB
);

CREATE TABLE IF NOT EXISTS action_plans (
  plan_id TEXT PRIMARY KEY,
  intake_id TEXT REFERENCES family_intake_events(intake_id),
  event_ts TIMESTAMPTZ DEFAULT now(),
  action_plan_text TEXT,
  generated_by_model TEXT
);

CREATE TABLE IF NOT EXISTS user_feedback (
  feedback_id TEXT PRIMARY KEY,
  intake_id TEXT REFERENCES family_intake_events(intake_id),
  event_ts TIMESTAMPTZ DEFAULT now(),
  rating INTEGER,
  feedback_text TEXT
);

SELECT 'family_intake_events' AS table_name, COUNT(*) FROM family_intake_events
UNION ALL SELECT 'program_matches', COUNT(*) FROM program_matches
UNION ALL SELECT 'action_plans', COUNT(*) FROM action_plans
UNION ALL SELECT 'user_feedback', COUNT(*) FROM user_feedback;
