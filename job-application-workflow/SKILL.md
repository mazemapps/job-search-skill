---
name: job-application-workflow
description: Bootstrap and run a public job-application workspace for Codex. Use when the user wants to set up a job-search repository on a fresh machine, create a master resume baseline, scaffold vacancy folders, or apply/respond to a vacancy with tracked artifacts.
---

# Job Application Workflow

Use this skill for two intent families:

- `setup` intents such as "set up job application workflow", "help me create a master resume", or "prepare a workspace for applications"
- `apply` intents such as "податься на вакансию", "apply to this role", or "capture this job description and prepare artifacts"

## Setup Mode

- Read [references/bootstrap.md](references/bootstrap.md).
- Use `scripts/bootstrap.py` as the public bootstrap entrypoint.
- Prefer:
  `python scripts/bootstrap.py setup --workspace <path>`
- Treat setup as a guided onboarding wizard, not a raw questionnaire.
- The wizard should:
  - explain what will be created
  - ask about existing files first
  - support a LinkedIn URL as a guided reference source
  - save `START_HERE.md` in the workspace
- The bootstrap script writes the workspace pointer to:
  `~/.codex/job-application-workflow/config.json`
- If the pointer is missing and the user asks for apply-mode work, help them run setup first or ask for the workspace path.

## Apply Mode

- Read [references/workflow.md](references/workflow.md).
- Resolve the workspace from `~/.codex/job-application-workflow/config.json` unless the user gives a different path.
- Prefer deterministic helpers when they fit:
  - `python scripts/bootstrap.py capture-vacancy ...`
  - `python scripts/bootstrap.py track-event ...`
  - workspace PDF utilities under `scripts/`

## Guardrails

- Keep candidate facts source-backed. Do not invent achievements, metrics, tools, dates, domains, or scope.
- Treat `config/candidate.yaml`, `source/originals/`, `source/working/`, and saved `vacancy.md` as the local source of truth.
- Keep generated markdown ATS-safe and HR-safe.
- Use runtime assets from this skill folder only; do not depend on external unpublished files.
