# Bootstrap SOP

Use this document when the user needs a fresh setup or does not yet have a usable job-search workspace.

## Goal

Create a working local workspace that is ready for vacancy-specific tailoring and tracking.
The primary setup path is agent-first: the user talks to the agent, and the agent quietly calls the deterministic backend.

## Primary Flow

1. Agent checks `~/.codex/job-application-workflow/config.json`.
2. If no workspace exists, agent proposes a default path such as `~/job-search`.
3. Agent collects source inputs in chat:
   - local paths / files
   - LinkedIn URL
   - pasted text
   - manual gap fill
4. Agent shows a compact review summary in chat.
5. Agent writes a temporary JSON payload and runs:

```bash
python scripts/bootstrap.py setup-from-payload --payload-file <temp-json>
```

6. Agent reports the created artifacts back to the user without asking them to manually run bootstrap commands.

## Fallback CLI

Keep this documented for debugging, CI, and automation:

```bash
python scripts/bootstrap.py setup --workspace <path>
```

## Bootstrap Responsibilities

1. Verify required tooling: `git`, `python3`, `pandoc`, `tectonic`, `pdffonts`, `pdfinfo`.
2. Attempt installation through the first available package manager for the current OS.
3. If auto-install fails in backend mode, return an actionable error the agent can explain.
4. Create the public workspace contract:
   - `config/`
   - `source/originals/`
   - `source/working/`
   - `source/intake/`
   - `applications/`
   - `tracking/`
   - `templates/`
   - `scripts/`
5. Import any user-provided CV, LinkedIn export, PDF, or Markdown sources into `source/originals/`.
6. Save the LinkedIn URL as a reference when provided, but do not scrape it automatically.
7. Create `config/candidate.yaml`.
8. Generate:
   - `source/intake/resume_intake.md`
   - `source/working/master_resume_clean_source.md`
   - `source/working/master_resume_2p.md`
   - `tracking/applications.csv`
   - `START_HERE.md`
   - `source/intake/linkedin_import_instructions.md` when relevant
9. Copy workspace helper scripts and templates.
10. Write the local workspace pointer to `~/.codex/job-application-workflow/config.json`.

## Backend Payload Contract

`setup-from-payload` accepts a JSON payload with:

- `workspace_path`
- `import_paths`
- `linkedin_url`
- `linkedin_followup`
- `manual_sections`
- `source_modes`
- `candidate`

The `candidate` object should include:

- required text fields such as `full_name`, `target_role_family`, `email`, `location`, PDF basenames, `default_language`, `professional_summary`
- lists for `core_skills`, `languages`, `education`
- a non-empty `experiences` array

## Intake Rules

- Agent-first path should ask about files and LinkedIn before asking the user to manually rebuild their history.
- If the user imports documents, preserve them as immutable originals and list them in the intake file.
- If the user gives a LinkedIn URL, explain the supported follow-up paths:
  - add a PDF/export
  - paste profile text into the generated guidance file
  - continue manually
- The user should never need to manually run bootstrap commands in the primary path.

## Success Criteria

- The workspace is self-contained and can be used without this repository clone.
- `master_resume_2p.md` exists and is exportable to PDF.
- `START_HERE.md` gives clear first steps.
- The user can immediately start the apply workflow.
