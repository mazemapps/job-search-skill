# Job Application Workflow Skill

This repository packages `job-application-workflow` as a public, installable Codex skill.
The installable skill lives in [`job-application-workflow`](/Users/mirroring/Desktop/job-search-skill/job-application-workflow) and is self-contained: the SOP, bootstrap scripts, workspace templates, and sample data all ship inside that folder so it can be installed directly from a GitHub path.

## What This Repo Provides

- A public Codex skill for two scenarios:
  - `setup`: bootstrap a fresh job-search workspace on a clean machine
  - `apply`: run the job-application workflow after the workspace exists
- A cross-platform bootstrap entrypoint:
  - `python scripts/bootstrap.py setup --workspace <path>`
- Workspace scaffolding for:
  - `source/originals/`
  - `source/working/`
  - `source/intake/`
  - `applications/`
  - `tracking/`
  - `templates/`
  - `scripts/`
- PDF export helpers that use `pandoc + tectonic + poppler`
- CI smoke tests for macOS, Linux, and Windows

## Install The Skill

Install from a GitHub path once the repo is published:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo OWNER/REPO \
  --path job-application-workflow
```

For local development, the equivalent bootstrap command is:

```bash
python job-application-workflow/scripts/bootstrap.py setup --workspace ~/job-search
```

Restart Codex after installation so it picks up the new skill.

## Quickstart

1. Install the skill, then run bootstrap:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup --workspace ~/job-search
```

When setup starts, it now behaves like a guided wizard:

- it prints a short welcome/manual
- it asks about existing resume/CV files first
- it supports adding a LinkedIn URL as a guided reference
- it saves `START_HERE.md` in the workspace with the next actions

2. If you want a non-interactive setup, pass the sample-style candidate JSON:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup \
  --workspace ~/job-search \
  --candidate-file ~/.codex/skills/job-application-workflow/assets/samples/sample_candidate_profile.json
```

3. Optional: import existing materials during setup:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup \
  --workspace ~/job-search \
  --import ~/Downloads/linkedin_profile.pdf \
  --import ~/Documents/resume.md
```

You can also skip `--import` and let the interactive wizard ask for files during setup.

If you only have LinkedIn at hand, the wizard supports a LinkedIn URL as a reference source. It does not scrape LinkedIn automatically; instead it stores the URL, creates guided instructions, and helps the user continue with one of these paths:

- add a LinkedIn PDF/export
- paste relevant profile text manually
- continue with a lightweight manual intake

You can also pass a LinkedIn URL directly:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup \
  --workspace ~/job-search \
  --linkedin-url https://www.linkedin.com/in/your-profile/
```

4. After setup, scaffold a vacancy record:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py capture-vacancy \
  --company "Example Co" \
  --role "Senior iOS Engineer" \
  --link "https://example.com/jobs/senior-ios-engineer" \
  --jd-file ./job_description.txt
```

5. Export PDFs from the generated workspace:

```bash
python ~/job-search/scripts/export_resume_pdf.py ~/job-search
python ~/job-search/scripts/rebuild_pdfs.py ~/job-search/applications
```

## First-Run Experience

After `setup`, the workspace will contain:

- `START_HERE.md` with the first three user actions
- `config/candidate.yaml`
- `source/intake/resume_intake.md`
- `source/working/master_resume_clean_source.md`
- `source/working/master_resume_2p.md`
- `source/intake/linkedin_import_instructions.md` when a LinkedIn URL was provided

The onboarding is intentionally optimized for low-friction completion. A rough but source-backed baseline is enough for the first run.

## Supported Operating Systems

- macOS
- Linux
- Windows

## Dependency Matrix

The bootstrap script checks these commands and tries to install missing ones automatically using an available package manager.

| Tool | Purpose | Typical package |
| --- | --- | --- |
| `git` | clone/import workflows and general repo hygiene | `git` |
| `python3` | run bootstrap and workspace utilities | `python3` / `python` |
| `pandoc` | Markdown to PDF conversion | `pandoc` |
| `tectonic` | TeX PDF engine used by `pandoc` | `tectonic` |
| `pdffonts` | PDF font audit | `poppler-utils` / `poppler` |
| `pdfinfo` | PDF page-size audit | `poppler-utils` / `poppler` |

Package manager order by platform:

- macOS: `brew`
- Linux: `apt`, then `dnf`
- Windows: `winget`, then `choco`

If auto-install fails, bootstrap prints exact fallback commands for the detected platform.

## Candidate Seed File

For automation and CI, bootstrap accepts a JSON seed file. The sample lives at [`sample_candidate_profile.json`](/Users/mirroring/Desktop/job-search-skill/job-application-workflow/assets/samples/sample_candidate_profile.json).

Expected schema:

```json
{
  "full_name": "Alex Example",
  "target_role_family": "Senior iOS Engineer",
  "email": "alex@example.com",
  "phone": "+351 000 000 000",
  "location": "Lisbon, Portugal",
  "linkedin_url": "https://www.linkedin.com/in/alex-example/",
  "portfolio_url": "https://alex.example.com",
  "pdf_resume_basename": "Alex_Example_Resume.pdf",
  "pdf_cover_letter_basename": "Alex_Example_Cover_Letter.pdf",
  "default_language": "English",
  "professional_summary": "Short, source-backed summary.",
  "core_skills": ["Swift", "UIKit", "SwiftUI"],
  "languages": ["English — C1", "Portuguese — A2"],
  "education": ["B.Sc. in Computer Science — Example University"],
  "experiences": [
    {
      "company": "Example Co",
      "role": "Senior iOS Engineer",
      "location": "Remote",
      "dates": "2022-2026",
      "tech_stack": ["Swift", "SwiftUI", "Combine"],
      "bullets": [
        "Delivered a reusable mobile architecture for a subscription product.",
        "Improved release confidence by standardizing CI and review workflows."
      ]
    }
  ]
}
```

## Repository Layout

```text
job-application-workflow/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── assets/
    ├── workspace-template/
    └── samples/
```

## CI

The GitHub Actions workflow at [`.github/workflows/ci.yml`](/Users/mirroring/Desktop/job-search-skill/.github/workflows/ci.yml) runs bootstrap and PDF smoke tests on macOS, Linux, and Windows.
