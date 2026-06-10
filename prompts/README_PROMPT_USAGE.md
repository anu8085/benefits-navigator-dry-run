# Prompt Usage

Use prompts in this order.

## 1. Master prompt

After the hackathon officially starts and you create the new repo, open Claude Code or another organizer-approved coding assistant in the new repo and paste:

`prompts/00_MASTER_PROMPT_START_HERE.md`

Then say:

`Start Phase 0 and guide me step by step.`

## 2. Ordered build prompts

Use:

`prompts/01_ORDERED_CLAUDE_CODE_PROMPTS.md`

Run one prompt at a time. Test and commit after each stable milestone.

## 3. Databricks prerequisite prompt

Use:

`prompts/02_DATABRICKS_PREREQUISITE_SETUP_PROMPT.md`

when you are ready to set up the new Databricks environment.

## 4. If Claude Code is not allowed

First check organizer guidance.

If no AI coding assistant is allowed, do not use Claude or another AI to write code. Use:

`docs/FULL_PROJECT_RECREATION_BLUEPRINT.md`

as a manual build specification.

If Claude is not allowed but another AI assistant is explicitly allowed, give that allowed AI:

- `prompts/03_IF_CLAUDE_NOT_ALLOWED_OR_ALTERNATE_AI_RECREATE_PROMPT.md`
- `docs/FULL_PROJECT_RECREATION_BLUEPRINT.md`

and ask it to recreate the project one file at a time.
