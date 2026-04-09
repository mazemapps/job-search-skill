# Job Application Workflow

This repository packages `job-application-workflow` as a public, installable Codex skill with a hidden local backend.
The primary user experience is chat-first: the user talks to the agent, and the agent handles onboarding, dependency setup, and workspace creation without asking the user to manually run bootstrap commands in the normal path.

## What This Repo Provides

- A public Codex skill for two scenarios:
  - `setup`: bootstrap a fresh job-search workspace on a clean machine
  - `apply`: run the job-application workflow after the workspace exists
- A deterministic local backend in [bootstrap.py](/Users/mirroring/Desktop/job-search-skill/job-application-workflow/scripts/bootstrap.py) for:
  - dependency checks and installation
  - workspace scaffolding
  - file import
  - pointer writes
  - tracking helpers
- An agent backend entrypoint:
  - `python scripts/bootstrap.py setup-from-payload --payload-file <path>`
- A fallback CLI setup entrypoint for debugging and automation:
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
  --repo https://github.com/mazemapps/job-search-skill
```

For local development, the equivalent bootstrap command is:

```bash
python job-application-workflow/scripts/bootstrap.py setup --workspace ~/job-search
```

Restart Codex after installation so it picks up the new skill.

## Primary Usage

1. Install the skill.
2. Restart Codex.
3. Talk to the agent.

Typical prompts:

- `Set up my job application workflow`
- `Help me create a master resume`
- `Подайся на вакансию` when no workspace exists yet

In the primary path, the agent should:

- propose a default workspace path like `~/job-search`
- ask about existing files first
- support a LinkedIn URL as a guided reference
- collect only the missing facts in chat
- call the backend internally
- report the created artifacts back to the user

## Fallback CLI

CLI is still useful for debugging, CI, or direct local automation.

Setup wizard fallback:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup \
  --workspace ~/job-search \
  --import ~/Downloads/linkedin_profile.pdf \
  --import ~/Documents/resume.md
```

Agent/backend path:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup-from-payload \
  --payload-file ~/.codex/skills/job-application-workflow/assets/samples/sample_agent_setup_payload.json \
  --workspace ~/job-search
```

Seed-based automation path:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py setup \
  --workspace ~/job-search \
  --candidate-file ~/.codex/skills/job-application-workflow/assets/samples/sample_candidate_profile.json
```

## LinkedIn Support

If the user only has LinkedIn at hand, the workflow supports a LinkedIn URL as a reference source. It does not scrape LinkedIn automatically; instead it stores the URL, creates guided instructions, and helps the user continue with one of these paths:

- add a LinkedIn PDF/export
- paste relevant profile text manually
- continue with a lightweight manual intake

## After Setup

The workspace can then be used for vacancy capture:

```bash
python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py capture-vacancy \
  --company "Example Co" \
  --role "Senior iOS Engineer" \
  --link "https://example.com/jobs/senior-ios-engineer" \
  --jd-file ./job_description.txt
```

And PDF export:

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

## Candidate Seed And Agent Payload Files

For automation and CI, bootstrap accepts:

- a candidate seed JSON at [`sample_candidate_profile.json`](/Users/mirroring/Desktop/job-search-skill/job-application-workflow/assets/samples/sample_candidate_profile.json)
- an agent/backend payload JSON at [`sample_agent_setup_payload.json`](/Users/mirroring/Desktop/job-search-skill/job-application-workflow/assets/samples/sample_agent_setup_payload.json)

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

The agent payload wraps the candidate data plus workspace/source metadata for hidden backend setup.

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
