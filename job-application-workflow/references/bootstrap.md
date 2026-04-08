# Bootstrap SOP

Use this document when the user needs a fresh setup or does not yet have a usable job-search workspace.

## Goal

Create a working local workspace that is ready for vacancy-specific tailoring and tracking.
The first-run experience should feel like a short setup wizard rather than a raw form dump.

## Entry Command

```bash
python scripts/bootstrap.py setup --workspace <path>
```

## Bootstrap Responsibilities

1. Verify required tooling: `git`, `python3`, `pandoc`, `tectonic`, `pdffonts`, `pdfinfo`.
2. Attempt installation through the first available package manager for the current OS.
3. If auto-install fails, print exact manual commands for the current platform.
4. Print a short welcome/manual in the terminal so the user understands the setup flow.
5. Start with source selection:
   - existing files
   - LinkedIn URL
   - start from scratch
6. Create the public workspace contract:
   - `config/`
   - `source/originals/`
   - `source/working/`
   - `source/intake/`
   - `applications/`
   - `tracking/`
   - `templates/`
   - `scripts/`
7. Import any user-provided CV, LinkedIn export, PDF, or Markdown sources into `source/originals/`.
8. Save the LinkedIn URL as a reference when provided, but do not scrape it automatically.
9. Create `config/candidate.yaml`.
10. Generate:
   - `source/intake/resume_intake.md`
   - `source/working/master_resume_clean_source.md`
   - `source/working/master_resume_2p.md`
   - `tracking/applications.csv`
   - `START_HERE.md`
   - `source/intake/linkedin_import_instructions.md` when relevant
11. Copy workspace helper scripts and templates.
12. Write the local workspace pointer to `~/.codex/job-application-workflow/config.json`.

## Intake Rules

- Prefer the structured JSON seed file when the user wants non-interactive setup.
- Otherwise prompt interactively in short sections with checkpoint summaries.
- If the user imports documents, preserve them as immutable originals and list them in the intake file.
- If the user gives a LinkedIn URL, explain the supported follow-up paths:
  - add a PDF/export
  - paste profile text into the generated guidance file
  - continue manually

## Success Criteria

- The workspace is self-contained and can be used without this repository clone.
- `master_resume_2p.md` exists and is exportable to PDF.
- `START_HERE.md` gives clear first steps.
- The user can immediately start the apply workflow.
