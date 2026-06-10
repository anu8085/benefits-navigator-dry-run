# Benefits Navigator Hackathon Simple Execution Kit V9

Use V9 only. Ignore older V4/V5/V6/V7 kits.

## What changed in V9

- Section 3A Local laptop setup is now much more detailed.
- The playbook now includes exact Python virtual environment creation and activation commands.
- Each major section has clearer step-by-step execution, validation, exit criteria, and fallback notes.
- The kit includes a detailed local setup guide: `docs/LOCAL_LAPTOP_SETUP_DETAILED.md`.
- The latest uploaded code is included only as a cleaned reference under `starter_project_latest_code_reference/`.

## Simple order

1. Before hackathon: store this ZIP in `C:\Hackathon\prep` and backup to Google Drive.
2. At official start: create a brand-new public GitHub repo.
3. Clone the new repo into `C:\Hackathon\work`.
4. Open the V9 playbook: `00_SIMPLE_EXECUTION_PLAYBOOK.docx`.
5. Complete Section 3A local setup first.
6. Complete Section 3B Databricks prerequisite setup.
7. Use the Claude section only if AI coding assistants are allowed.
8. Test in this order: JSON + SQLite, Unity Catalog + SQLite, Databricks App + Lakebase.
9. Record demo and submit.

## Most important files

- `00_SIMPLE_EXECUTION_PLAYBOOK.docx` - main step-by-step guide.
- `docs/LOCAL_LAPTOP_SETUP_DETAILED.md` - detailed Python local setup.
- `docs/DATABRICKS_PREREQUISITE_SETUP.md` - new Databricks env setup.
- `docs/FULL_PROJECT_RECREATION_BLUEPRINT.md` - file-by-file project build blueprint.
- `prompts/00_MASTER_PROMPT_START_HERE.md` - master AI prompt if AI is allowed.
- `prompts/01_ORDERED_CLAUDE_CODE_PROMPTS.md` - build prompts in order.
- `prompts/03_IF_CLAUDE_NOT_ALLOWED_OR_ALTERNATE_AI_RECREATE_PROMPT.md` - no-Claude/alternate-AI path.


## V9 update
Section 6 of the simple playbook now includes 8 concrete testing scenarios covering the main demo, pregnancy, child health coverage, utilities, childcare, immigration-sensitive, senior/disabled adult, and negative/control tests. Use Scenario 1 for the official demo unless a different scenario works better on the day.
