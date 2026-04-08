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
- Treat setup as agent-first onboarding, not as a user-run terminal flow.
- First check `~/.codex/job-application-workflow/config.json`.
- If no workspace pointer exists:
  - propose a default path such as `~/job-search`
  - collect source inputs in chat: local paths/files first, then LinkedIn URL, then pasted text/manual gap fill
  - collect missing profile, summary, skills, education, languages, and experiences in short chat blocks
  - show a compact review summary in chat
  - write a temporary JSON payload and call the hidden backend:
    `python scripts/bootstrap.py setup-from-payload --payload-file <temp-json>`
- The user should not need to manually run `python scripts/bootstrap.py setup ...` in the primary path.
- Keep `setup` as a fallback CLI/debug path only.
- The bootstrap script writes the workspace pointer to:
  `~/.codex/job-application-workflow/config.json`
- After backend success, tell the user only the important outcomes:
  - `START_HERE.md`
  - master resume files
  - tracking file
  - workspace path

## Apply Mode

- Read [references/workflow.md](references/workflow.md).
- Resolve the workspace from `~/.codex/job-application-workflow/config.json` unless the user gives a different path.
- If the pointer is missing, automatically switch into setup mode in the same chat and complete onboarding before continuing.
- Prefer deterministic helpers when they fit:
  - `python scripts/bootstrap.py capture-vacancy ...`
  - `python scripts/bootstrap.py track-event ...`
  - workspace PDF utilities under `scripts/`

## Guardrails

- Keep candidate facts source-backed. Do not invent achievements, metrics, tools, dates, domains, or scope.
- Treat `config/candidate.yaml`, `source/originals/`, `source/working/`, and saved `vacancy.md` as the local source of truth.
- Keep generated markdown ATS-safe and HR-safe.
- Use runtime assets from this skill folder only; do not depend on external unpublished files.
- LinkedIn remains a guided reference source only. Do not scrape or auto-parse it from the network.
