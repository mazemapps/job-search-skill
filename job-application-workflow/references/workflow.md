# Apply Workflow SOP

Use this document when the user wants to capture a vacancy, tailor documents, export PDFs, and update tracking.

## Local Source Of Truth

- `config/candidate.yaml`
- `source/originals/*`
- `source/working/master_resume_2p.md`
- `applications/YYYY-MM-DD_company_role/vacancy.md`

## Deterministic Helpers

- Capture a vacancy:

```bash
python scripts/bootstrap.py capture-vacancy --company "<company>" --role "<role>" --link "<url>" --jd-file ./jd.txt
```

- Track an event:

```bash
python scripts/bootstrap.py track-event --application-id YYYY-MM-DD_company_role --status APPLIED --last-action "application submitted" --next-action "follow up" --next-due YYYY-MM-DD --log-note "Application submitted via company site."
```

- Export PDFs from the workspace:

```bash
python scripts/export_resume_pdf.py <workspace-or-vacancy-dir>
python scripts/export_cover_letter_pdf.py <vacancy-dir>
```

## Canonical Flow

1. Capture the vacancy data and create `applications/YYYY-MM-DD_company_role/`.
2. Save `vacancy.md` and initialize `log.md`.
3. Tailor artifacts from `source/working/master_resume_2p.md` and the saved vacancy.
4. Save the generated markdown artifacts in the vacancy folder.
5. Export the tailored resume to the candidate-specific PDF filename from `config/candidate.yaml`.
6. Update `tracking/applications.csv`.
7. After every event, update both `log.md` and `tracking/applications.csv`.

## Required Vacancy Files

- `vacancy.md`
- `log.md`
- `resume_tailored.md`
- candidate resume PDF basename from `config/candidate.yaml`
- `fit_analysis.md`
- `cover_letter.md` when needed
- `outreach_message.md` when needed

## Truthfulness Rules

- Never invent unsupported facts.
- If a JD requirement is not evidenced in the source materials, record it as a gap instead of claiming it.
- Keep chronology factual.
- Keep final files HR-safe and free of process notes.

## Tracking Columns

`id,date,company,role,link,status,last_action,next_action,next_due,folder,contact,notes`
