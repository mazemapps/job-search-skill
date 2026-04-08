#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "workspace-template"
POINTER_ROOT = Path(os.environ.get("JOB_APP_WORKFLOW_HOME", Path.home() / ".codex" / "job-application-workflow"))
POINTER_FILE = POINTER_ROOT / "config.json"

REQUIRED_COMMANDS = ("git", "python3", "pandoc", "tectonic", "pdffonts", "pdfinfo")
TRACKING_COLUMNS = [
    "id",
    "date",
    "company",
    "role",
    "link",
    "status",
    "last_action",
    "next_action",
    "next_due",
    "folder",
    "contact",
    "notes",
]
PACKAGE_MAP = {
    "brew": {
        "git": "git",
        "python3": "python",
        "pandoc": "pandoc",
        "tectonic": "tectonic",
        "pdffonts": "poppler",
        "pdfinfo": "poppler",
    },
    "apt": {
        "git": "git",
        "python3": "python3",
        "pandoc": "pandoc",
        "tectonic": "tectonic",
        "pdffonts": "poppler-utils",
        "pdfinfo": "poppler-utils",
    },
    "dnf": {
        "git": "git",
        "python3": "python3",
        "pandoc": "pandoc",
        "tectonic": "tectonic",
        "pdffonts": "poppler-utils",
        "pdfinfo": "poppler-utils",
    },
    "winget": {
        "git": "Git.Git",
        "python3": "Python.Python.3.12",
        "pandoc": "JohnMacFarlane.Pandoc",
        "tectonic": "TectonicTypesetting.Tectonic",
        "pdffonts": "oschwartz10612.Poppler",
        "pdfinfo": "oschwartz10612.Poppler",
    },
    "choco": {
        "git": "git",
        "python3": "python",
        "pandoc": "pandoc",
        "tectonic": "tectonic",
        "pdffonts": "poppler",
        "pdfinfo": "poppler",
    },
}
SETUP_STEPS = [
    "Welcome",
    "Source mode",
    "Profile basics",
    "Summary",
    "Skills, education, languages",
    "Experience",
    "Review",
]


def command_exists(command: str) -> bool:
    if command == "python3":
        return shutil.which("python3") is not None or shutil.which("python") is not None
    return shutil.which(command) is not None


def detect_package_managers() -> list[str]:
    system = platform.system().lower()
    candidates: list[str]
    if system == "darwin":
        candidates = ["brew"]
    elif system == "windows":
        candidates = ["winget", "choco"]
    else:
        candidates = ["apt", "dnf"]
    return [candidate for candidate in candidates if shutil.which(candidate) is not None]


def missing_commands() -> list[str]:
    return [command for command in REQUIRED_COMMANDS if not command_exists(command)]


def manual_install_commands(package_manager: str) -> list[str]:
    package_map = PACKAGE_MAP[package_manager]
    packages = []
    for command in missing_commands():
        package = package_map[command]
        if package not in packages:
            packages.append(package)

    if not packages:
        return []

    if package_manager == "brew":
        return [f"brew install {' '.join(packages)}"]
    if package_manager == "apt":
        return [
            "sudo apt-get update",
            f"sudo apt-get install -y {' '.join(packages)}",
        ]
    if package_manager == "dnf":
        return [f"sudo dnf install -y {' '.join(packages)}"]
    if package_manager == "winget":
        return [
            f'winget install --id {package} -e --accept-package-agreements --accept-source-agreements'
            for package in packages
        ]
    if package_manager == "choco":
        return [f"choco install -y {' '.join(packages)}"]
    raise ValueError(f"Unsupported package manager: {package_manager}")


def attempt_dependency_install() -> None:
    managers = detect_package_managers()
    if not managers:
        return

    manager = managers[0]
    commands = manual_install_commands(manager)
    if not commands:
        return

    for command in commands:
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            break


def ensure_dependencies(skip_install: bool) -> None:
    if not missing_commands():
        return

    if not skip_install:
        attempt_dependency_install()

    after = missing_commands()
    if not after:
        return

    managers = detect_package_managers()
    lines = ["Missing required commands after bootstrap dependency check:"]
    lines.extend(f"- {command}" for command in after)
    if managers:
        lines.append("")
        lines.append("Try one of these commands:")
        for command in manual_install_commands(managers[0]):
            lines.append(command)
    raise SystemExit("\n".join(lines))


def load_candidate_seed(candidate_file: Path | None) -> dict[str, Any]:
    if candidate_file is None:
        return {}
    data = json.loads(candidate_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Candidate seed file must contain a JSON object.")
    return data


def is_interactive() -> bool:
    return sys.stdin.isatty()


def print_step(index: int, title: str) -> None:
    print(f"\n[{index}/{len(SETUP_STEPS)}] {title}")


def print_block(text: str) -> None:
    print(text.rstrip())


def prompt(message: str, default: str | None = None) -> str:
    if not is_interactive():
        if default is not None:
            return default
        raise SystemExit(f"Missing required bootstrap data for prompt: {message}")
    suffix = f" [{default}]" if default is not None else ""
    while True:
        answer = input(f"{message}{suffix}: ").strip()
        if answer:
            return answer
        if default is not None:
            return default


def prompt_optional(message: str, default: str | None = None) -> str:
    if not is_interactive():
        return default or ""
    suffix = f" [{default}]" if default else ""
    answer = input(f"{message}{suffix}: ").strip()
    if answer:
        return answer
    return default or ""


def prompt_yes_no(message: str, default: bool = True) -> bool:
    default_label = "Y/n" if default else "y/N"
    answer = prompt(f"{message} ({default_label})", "").lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def prompt_choice(message: str, options: list[tuple[str, str]], default_key: str | None = None) -> str:
    if not is_interactive():
        if default_key is not None:
            return default_key
        raise SystemExit(f"Missing required choice for prompt: {message}")

    print(message)
    for key, label in options:
        marker = " (default)" if default_key == key else ""
        print(f"{key}. {label}{marker}")

    valid = {key for key, _ in options}
    while True:
        answer = input("Choose an option: ").strip()
        if not answer and default_key is not None:
            return default_key
        if answer in valid:
            return answer
        print(f"Please choose one of: {', '.join(sorted(valid))}")


def prompt_list(message: str, existing: list[str] | None = None, minimum: int = 1) -> list[str]:
    if existing:
        return existing
    answer = prompt(f"{message} (comma-separated)")
    values = [item.strip() for item in answer.split(",") if item.strip()]
    if len(values) < minimum:
        raise SystemExit(f"Expected at least {minimum} value(s) for {message}.")
    return values


def prompt_file_paths(existing_paths: list[str]) -> list[str]:
    if not is_interactive():
        return existing_paths

    paths = list(existing_paths)
    print("Add existing resume, CV, LinkedIn export, or markdown files one by one.")
    print("Press Enter on an empty line when you are done.")
    while True:
        raw = input("File path: ").strip()
        if not raw:
            break
        paths.append(raw)
    return paths


def prompt_experiences(existing: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if existing:
        return existing

    print_block("This step creates a usable baseline resume. A compact summary for each role is enough.")
    count_raw = prompt("How many experience entries should the baseline resume include", "1")
    try:
        count = max(1, int(count_raw))
    except ValueError as exc:
        raise SystemExit("Experience count must be an integer.") from exc

    experiences: list[dict[str, Any]] = []
    for index in range(count):
        prefix = f"Experience {index + 1}"
        print_block(f"\n{prefix}: company, title, dates, tech, and 2-4 source-backed bullets.")
        company = prompt(f"{prefix} company")
        role = prompt(f"{prefix} role")
        location = prompt(f"{prefix} location", "Remote")
        dates = prompt(f"{prefix} dates")
        tech_stack = prompt_list(f"{prefix} tech stack", minimum=1)
        bullets = prompt_list(f"{prefix} bullets", minimum=1)
        experiences.append(
            {
                "company": company,
                "role": role,
                "location": location,
                "dates": dates,
                "tech_stack": tech_stack,
                "bullets": bullets,
            }
        )
    return experiences


def mark_manual_section(source_state: dict[str, Any], label: str) -> None:
    if label not in source_state["manual_sections"]:
        source_state["manual_sections"].append(label)


def normalize_path_list(paths: list[str]) -> list[Path]:
    return [Path(item).expanduser().resolve() for item in paths if str(item).strip()]


def ensure_import_paths(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit("Import paths not found:\n" + "\n".join(missing))


def choose_source_state(seed: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    source_state = {
        "import_paths": list(args.imports),
        "linkedin_url": str(getattr(args, "linkedin_url", "") or seed.get("linkedin_url", "")).strip(),
        "linkedin_followup": str(seed.get("linkedin_followup", "")).strip(),
        "source_modes": [],
        "manual_sections": [],
    }

    if not is_interactive():
        source_state["source_modes"] = []
        if source_state["import_paths"]:
            source_state["source_modes"].append("existing_files")
        if source_state["linkedin_url"]:
            source_state["source_modes"].append("linkedin_url")
        if not source_state["source_modes"]:
            source_state["source_modes"].append("start_from_scratch")
        return source_state

    print_step(2, SETUP_STEPS[1])
    print_block(
        "We'll start with your existing sources. You can import files, add a LinkedIn URL as a reference, "
        "or continue from scratch."
    )

    existing_imports = list(source_state["import_paths"])
    if existing_imports:
        keep_imports = prompt_yes_no(
            f"Keep the {len(existing_imports)} source file(s) already queued for import?",
            default=True,
        )
        if not keep_imports:
            source_state["import_paths"] = []

    if prompt_yes_no("Do you want to import existing resume or CV files first?", default=not existing_imports or bool(source_state["import_paths"])):
        source_state["import_paths"] = prompt_file_paths(source_state["import_paths"])

    if source_state["linkedin_url"]:
        keep_linkedin = prompt_yes_no("Keep the current LinkedIn URL reference?", default=True)
        if not keep_linkedin:
            source_state["linkedin_url"] = ""
            source_state["linkedin_followup"] = ""

    if not source_state["linkedin_url"] and prompt_yes_no("Do you want to add a LinkedIn profile URL as a reference?", default=True):
        source_state["linkedin_url"] = prompt("Paste your LinkedIn profile URL")

    if source_state["linkedin_url"] and not source_state["linkedin_followup"]:
        followup_choice = prompt_choice(
            "How do you want to use the LinkedIn profile during setup?",
            [
                ("1", "I will attach a LinkedIn export or PDF"),
                ("2", "I will paste profile text into the generated guidance file"),
                ("3", "Use the URL as a reference and continue with manual answers"),
            ],
            default_key="3",
        )
        source_state["linkedin_followup"] = {
            "1": "attach_export",
            "2": "paste_text",
            "3": "continue_manual",
        }[followup_choice]

    source_state["source_modes"] = []
    if source_state["import_paths"]:
        source_state["source_modes"].append("existing_files")
    if source_state["linkedin_url"]:
        source_state["source_modes"].append("linkedin_url")
    if not source_state["source_modes"]:
        source_state["source_modes"].append("start_from_scratch")

    mode_summary = []
    if "existing_files" in source_state["source_modes"]:
        mode_summary.append("existing files")
    if "linkedin_url" in source_state["source_modes"]:
        mode_summary.append("LinkedIn URL")
    if source_state["source_modes"] == ["start_from_scratch"]:
        mode_summary.append("start from scratch")
    print_block(f"Source mode: {', '.join(mode_summary)}")
    return source_state


def collect_profile_basics(data: dict[str, Any], source_state: dict[str, Any]) -> None:
    print_step(3, SETUP_STEPS[2])
    print_block("Let's capture the profile basics that every generated document needs.")
    required_defaults = {
        "phone": "",
        "portfolio_url": "",
        "default_language": "English",
    }
    required_fields = [
        ("full_name", "Full name"),
        ("target_role_family", "Target role family"),
        ("email", "Email"),
        ("phone", "Phone"),
        ("location", "Location"),
        ("portfolio_url", "Portfolio URL"),
        ("pdf_resume_basename", "Resume PDF filename"),
        ("pdf_cover_letter_basename", "Cover letter PDF filename"),
        ("default_language", "Default language"),
    ]

    if source_state["linkedin_url"]:
        data["linkedin_url"] = source_state["linkedin_url"]
    elif "linkedin_url" not in data:
        data["linkedin_url"] = ""

    for field, label in required_fields:
        if str(data.get(field, "")).strip():
            continue
        default = required_defaults.get(field)
        if field == "pdf_resume_basename" and data.get("full_name"):
            default = f"{str(data['full_name']).replace(' ', '_')}_Resume.pdf"
        if field == "pdf_cover_letter_basename" and data.get("full_name"):
            default = f"{str(data['full_name']).replace(' ', '_')}_Cover_Letter.pdf"
        data[field] = prompt(f"Enter {label.lower()}", default)
        mark_manual_section(source_state, "Profile basics")

    if not data.get("linkedin_url"):
        data["linkedin_url"] = prompt_optional("LinkedIn URL (optional)")
        if data["linkedin_url"]:
            source_state["linkedin_url"] = data["linkedin_url"]
            if "linkedin_url" not in source_state["source_modes"]:
                source_state["source_modes"].append("linkedin_url")

    print_block(f"Checkpoint: baseline docs will be created for {data['full_name']} ({data['target_role_family']}).")


def collect_summary_block(data: dict[str, Any], source_state: dict[str, Any]) -> None:
    print_step(4, SETUP_STEPS[3])
    print_block("Now add a short professional summary. One concise paragraph is enough for the first baseline.")
    if not str(data.get("professional_summary", "")).strip():
        data["professional_summary"] = prompt("Professional summary")
        mark_manual_section(source_state, "Professional summary")
    print_block("Checkpoint: summary captured.")


def collect_list_blocks(data: dict[str, Any], source_state: dict[str, Any]) -> None:
    print_step(5, SETUP_STEPS[4])
    print_block("We'll keep this light: a rough list is fine, especially if you already imported source files.")

    if not data.get("core_skills"):
        data["core_skills"] = prompt_list("Enter core skills", minimum=1)
        mark_manual_section(source_state, "Core skills")

    if not data.get("education"):
        data["education"] = prompt_list("Enter education entries", minimum=1)
        mark_manual_section(source_state, "Education")

    if not data.get("languages"):
        data["languages"] = prompt_list("Enter languages", minimum=1)
        mark_manual_section(source_state, "Languages")

    print_block(
        f"Checkpoint: {len(data['core_skills'])} skill(s), {len(data['education'])} education item(s), "
        f"and {len(data['languages'])} language entry(ies) captured."
    )


def collect_experience_block(data: dict[str, Any], source_state: dict[str, Any]) -> None:
    print_step(6, SETUP_STEPS[5])
    if not data.get("experiences"):
        data["experiences"] = prompt_experiences()
        mark_manual_section(source_state, "Experience")
    print_block(f"Checkpoint: {len(data['experiences'])} experience entry(ies) captured.")


def build_review_summary(data: dict[str, Any], source_state: dict[str, Any], import_paths: list[Path]) -> str:
    imported_names = ", ".join(path.name for path in import_paths) if import_paths else "none"
    linkedin_value = source_state["linkedin_url"] or "not provided"
    manual_sections = ", ".join(source_state["manual_sections"]) if source_state["manual_sections"] else "seed/import sources only"
    experience_titles = ", ".join(f"{item['company']} - {item['role']}" for item in data.get("experiences", []))
    return "\n".join(
        [
            f"Candidate: {data.get('full_name', 'unknown')}",
            f"Role family: {data.get('target_role_family', 'unknown')}",
            f"Imported files: {imported_names}",
            f"LinkedIn: {linkedin_value}",
            f"Manual sections: {manual_sections}",
            f"Skills: {len(data.get('core_skills', []))}",
            f"Education entries: {len(data.get('education', []))}",
            f"Experience entries: {len(data.get('experiences', []))}",
            f"Experience summary: {experience_titles or 'none'}",
        ]
    )


def review_setup_data(data: dict[str, Any], source_state: dict[str, Any], import_paths: list[Path]) -> None:
    if not is_interactive():
        return

    while True:
        print_step(7, SETUP_STEPS[6])
        print_block("Here is the baseline setup summary:")
        print_block(build_review_summary(data, source_state, import_paths))
        decision = prompt_choice(
            "Create the baseline files now, or revisit a section?",
            [
                ("1", "Create files now"),
                ("2", "Edit source mode"),
                ("3", "Edit profile basics"),
                ("4", "Edit professional summary"),
                ("5", "Edit skills, education, and languages"),
                ("6", "Edit experience"),
            ],
            default_key="1",
        )
        if decision == "1":
            return
        if decision == "2":
            updated = choose_source_state(data, argparse.Namespace(imports=[str(path) for path in import_paths]))
            source_state["import_paths"] = updated["import_paths"]
            source_state["linkedin_url"] = updated["linkedin_url"]
            source_state["linkedin_followup"] = updated["linkedin_followup"]
            source_state["source_modes"] = updated["source_modes"]
            import_paths[:] = normalize_path_list(source_state["import_paths"])
            ensure_import_paths(import_paths)
        elif decision == "3":
            for key in [
                "full_name",
                "target_role_family",
                "email",
                "phone",
                "location",
                "portfolio_url",
                "pdf_resume_basename",
                "pdf_cover_letter_basename",
                "default_language",
            ]:
                data.pop(key, None)
            collect_profile_basics(data, source_state)
        elif decision == "4":
            data.pop("professional_summary", None)
            collect_summary_block(data, source_state)
        elif decision == "5":
            data.pop("core_skills", None)
            data.pop("education", None)
            data.pop("languages", None)
            collect_list_blocks(data, source_state)
        elif decision == "6":
            data.pop("experiences", None)
            collect_experience_block(data, source_state)


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    sanitized = []
    previous_underscore = False
    for char in lowered:
        if char.isalnum():
            sanitized.append(char)
            previous_underscore = False
        else:
            if not previous_underscore:
                sanitized.append("_")
            previous_underscore = True
    return "".join(sanitized).strip("_")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_with_unique_name(source: Path, destination_dir: Path) -> Path:
    destination = destination_dir / source.name
    if not destination.exists():
        shutil.copy2(source, destination)
        return destination

    stem = source.stem
    suffix = source.suffix
    counter = 2
    while True:
        candidate = destination_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            shutil.copy2(source, candidate)
            return candidate
        counter += 1


def format_contact_bullets(data: dict[str, Any]) -> str:
    linkedin_line = f"- LinkedIn: {data['linkedin_url']}" if data.get("linkedin_url") else "- LinkedIn: not provided yet"
    portfolio_line = f"- Portfolio: {data['portfolio_url']}" if data.get("portfolio_url") else "- Portfolio: not provided yet"
    return "\n".join(
        [
            f"- Email: {data['email']}",
            f"- Phone: {data['phone']}",
            f"- Location: {data['location']}",
            linkedin_line,
            portfolio_line,
        ]
    )


def format_simple_bullets(values: list[str], fallback: str | None = None) -> str:
    if values:
        return "\n".join(f"- {value}" for value in values)
    if fallback:
        return f"- {fallback}"
    return ""


def format_experience_blocks(experiences: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for experience in experiences:
        tech_stack = ", ".join(experience["tech_stack"])
        bullets = "\n".join(f"- {bullet}" for bullet in experience["bullets"])
        block = (
            f"### {experience['company']} — {experience['role']}\n"
            f"{experience['location']} | {experience['dates']}\n"
            f"Tech stack: {tech_stack}\n\n"
            f"{bullets}"
        )
        blocks.append(block)
    return "\n\n".join(blocks)


def build_welcome_text(workspace: Path) -> str:
    return "\n".join(
        [
            "Welcome to job-application-workflow.",
            "",
            "This setup will:",
            "- create a local job-search workspace",
            "- scaffold source, applications, tracking, templates, and scripts",
            "- help you bootstrap a master resume baseline",
            "- preserve imported files under source/originals/",
            "- save a START_HERE.md guide in the workspace",
            "",
            "You can continue from existing files, add a LinkedIn URL as a reference, or start from scratch.",
            f"Workspace target: {workspace}",
        ]
    )


def build_template_context(
    workspace: Path,
    data: dict[str, Any],
    imported_files: list[Path],
    source_state: dict[str, Any],
) -> dict[str, str]:
    imported_bullets = [f"- {path.name}" for path in imported_files] or ["- No external source files were imported during bootstrap."]
    manual_sections = source_state["manual_sections"] or ["No interactive sections were entered during this run."]
    manual_bullets = [f"- {section}" for section in manual_sections]
    source_modes = [mode.replace("_", " ") for mode in source_state["source_modes"]] or ["start from scratch"]
    linkedin_reference = source_state["linkedin_url"] or "No LinkedIn URL was provided during setup."
    linkedin_next_step_map = {
        "attach_export": "Add a LinkedIn PDF/export file into source/originals/ and update the intake notes.",
        "paste_text": "Paste key LinkedIn profile text into source/intake/linkedin_import_instructions.md and refine the working resume.",
        "continue_manual": "Keep the URL as a reference and continue building the resume from manual answers.",
    }
    linkedin_next_step = linkedin_next_step_map.get(
        source_state["linkedin_followup"],
        "No LinkedIn-specific follow-up is required.",
    )
    return {
        "FULL_NAME": data["full_name"],
        "TARGET_ROLE_FAMILY": data["target_role_family"],
        "EMAIL": data["email"],
        "PHONE": data["phone"],
        "LOCATION": data["location"],
        "LINKEDIN_URL": data.get("linkedin_url", ""),
        "PORTFOLIO_URL": data["portfolio_url"],
        "PDF_RESUME_BASENAME": data["pdf_resume_basename"],
        "PDF_COVER_LETTER_BASENAME": data["pdf_cover_letter_basename"],
        "DEFAULT_LANGUAGE": data["default_language"],
        "GENERATED_AT": dt.datetime.now().isoformat(timespec="seconds"),
        "SUMMARY": data["professional_summary"],
        "CONTACT_BULLETS": format_contact_bullets(data),
        "CORE_SKILLS_BULLETS": format_simple_bullets(data["core_skills"]),
        "EDUCATION_BULLETS": format_simple_bullets(data["education"]),
        "LANGUAGE_BULLETS": format_simple_bullets(data["languages"]),
        "EXPERIENCE_BLOCKS_CLEAN": format_experience_blocks(data["experiences"]),
        "EXPERIENCE_BLOCKS_SUBMISSION": format_experience_blocks(data["experiences"]),
        "IMPORTED_SOURCES_BULLETS": "\n".join(imported_bullets),
        "MANUAL_FACTS_BULLETS": "\n".join(manual_bullets),
        "SOURCE_MODE_BULLETS": "\n".join(f"- {mode}" for mode in source_modes),
        "LINKEDIN_REFERENCE_LINE": linkedin_reference,
        "LINKEDIN_NEXT_STEP": linkedin_next_step,
        "WORKSPACE_PATH": str(workspace),
        "START_HERE_PATH": str(workspace / "START_HERE.md"),
        "MASTER_RESUME_CLEAN_PATH": str(workspace / "source" / "working" / "master_resume_clean_source.md"),
        "MASTER_RESUME_SUBMISSION_PATH": str(workspace / "source" / "working" / "master_resume_2p.md"),
        "TRACKING_PATH": str(workspace / "tracking" / "applications.csv"),
        "APPLICATIONS_PATH": str(workspace / "applications"),
        "RESUME_EXPORT_COMMAND": f"python {workspace / 'scripts' / 'export_resume_pdf.py'} {workspace}",
        "REBUILD_PDFS_COMMAND": f"python {workspace / 'scripts' / 'rebuild_pdfs.py'} {workspace / 'applications'}",
        "CAPTURE_VACANCY_COMMAND": (
            f'python ~/.codex/skills/job-application-workflow/scripts/bootstrap.py capture-vacancy '
            f'--workspace "{workspace}" --company "Example Co" --role "Senior iOS Engineer" '
            f'--link "https://example.com/jobs/senior-ios-engineer" --jd-file ./job_description.txt'
        ),
    }


def render_template(text: str, context: dict[str, str]) -> str:
    rendered = text
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def render_workspace(workspace: Path, context: dict[str, str]) -> None:
    for source in TEMPLATE_ROOT.rglob("*"):
        if "__pycache__" in source.parts:
            continue
        relative = source.relative_to(TEMPLATE_ROOT)
        if source.is_dir():
            (workspace / relative).mkdir(parents=True, exist_ok=True)
            continue

        destination = workspace / relative
        if destination.suffix == ".template":
            destination = destination.with_suffix("")
            content = render_template(source.read_text(encoding="utf-8"), context)
            ensure_parent(destination)
            destination.write_text(content + ("" if content.endswith("\n") else "\n"), encoding="utf-8")
        else:
            ensure_parent(destination)
            shutil.copy2(source, destination)

        if destination.parent.name == "scripts":
            destination.chmod(0o755)


def cleanup_optional_files(workspace: Path, source_state: dict[str, Any]) -> None:
    linkedin_guide = workspace / "source" / "intake" / "linkedin_import_instructions.md"
    if not source_state["linkedin_url"] and linkedin_guide.exists():
        linkedin_guide.unlink()


def ensure_workspace_contract_dirs(workspace: Path) -> None:
    for relative in [
        "applications",
        "config",
        "source/originals",
        "source/working",
        "source/intake",
        "tracking",
        "templates",
        "scripts",
    ]:
        (workspace / relative).mkdir(parents=True, exist_ok=True)


def write_pointer(workspace: Path) -> None:
    POINTER_ROOT.mkdir(parents=True, exist_ok=True)
    data = {
        "workspace_path": str(workspace.resolve()),
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    POINTER_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def resolve_workspace(workspace_arg: str | None) -> Path:
    if workspace_arg:
        return Path(workspace_arg).expanduser().resolve()
    if POINTER_FILE.exists():
        data = json.loads(POINTER_FILE.read_text(encoding="utf-8"))
        workspace_path = data.get("workspace_path")
        if workspace_path:
            return Path(workspace_path).expanduser().resolve()
    raise SystemExit("Workspace path is required. Run setup first or pass --workspace.")


def prepare_candidate_data(seed: dict[str, Any], source_state: dict[str, Any]) -> dict[str, Any]:
    data = dict(seed)
    data["linkedin_url"] = source_state["linkedin_url"] or str(data.get("linkedin_url", "")).strip()
    collect_profile_basics(data, source_state)
    collect_summary_block(data, source_state)
    collect_list_blocks(data, source_state)
    collect_experience_block(data, source_state)
    return data


def run_setup(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    ensure_dependencies(skip_install=args.skip_install)

    if workspace.exists() and any(workspace.iterdir()) and not args.force:
        raise SystemExit(f"Workspace already exists and is not empty: {workspace}. Use --force to continue.")

    workspace.mkdir(parents=True, exist_ok=True)
    ensure_workspace_contract_dirs(workspace)

    print_step(1, SETUP_STEPS[0])
    print_block(build_welcome_text(workspace))

    seed = load_candidate_seed(Path(args.candidate_file).expanduser().resolve() if args.candidate_file else None)
    source_state = choose_source_state(seed, args)
    import_paths = normalize_path_list(source_state["import_paths"])
    ensure_import_paths(import_paths)

    candidate_data = prepare_candidate_data(seed, source_state)
    review_setup_data(candidate_data, source_state, import_paths)

    originals_dir = workspace / "source" / "originals"
    originals_dir.mkdir(parents=True, exist_ok=True)
    imported_files = [copy_with_unique_name(path, originals_dir) for path in import_paths]

    context = build_template_context(workspace, candidate_data, imported_files, source_state)
    render_workspace(workspace, context)
    cleanup_optional_files(workspace, source_state)
    write_pointer(workspace)

    print("\nSetup complete.")
    print(f"- Start here: {workspace / 'START_HERE.md'}")
    print(f"- Master resume: {workspace / 'source' / 'working' / 'master_resume_2p.md'}")
    print(f"- Tracking file: {workspace / 'tracking' / 'applications.csv'}")
    print(workspace)
    return 0


def ensure_tracking_file(workspace: Path) -> Path:
    tracking_path = workspace / "tracking" / "applications.csv"
    ensure_parent(tracking_path)
    if not tracking_path.exists():
        with tracking_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=TRACKING_COLUMNS)
            writer.writeheader()
    return tracking_path


def load_tracking_rows(tracking_path: Path) -> list[dict[str, str]]:
    with tracking_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_tracking_rows(tracking_path: Path, rows: list[dict[str, str]]) -> None:
    with tracking_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKING_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def application_id_for(date_value: dt.date, company: str, role: str) -> str:
    return f"{date_value.isoformat()}_{slugify(company)}_{slugify(role)}"


def append_log(log_path: Path, message: str, timestamp: str | None = None) -> None:
    ensure_parent(log_path)
    if not log_path.exists():
        log_path.write_text("# Application Log\n\n## Timeline\n", encoding="utf-8")
    stamp = timestamp or dt.datetime.now().isoformat(timespec="minutes")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {stamp}: {message}\n")


def run_capture_vacancy(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    tracking_path = ensure_tracking_file(workspace)
    capture_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    application_id = application_id_for(capture_date, args.company, args.role)
    vacancy_dir = workspace / "applications" / application_id
    if vacancy_dir.exists():
        raise SystemExit(f"Application folder already exists: {vacancy_dir}")
    vacancy_dir.mkdir(parents=True, exist_ok=False)

    if args.jd_file:
        jd_text = Path(args.jd_file).expanduser().read_text(encoding="utf-8")
    elif args.jd_text:
        jd_text = args.jd_text
    else:
        raise SystemExit("Either --jd-file or --jd-text is required.")

    vacancy_md = "\n".join(
        [
            f"# {args.company} — {args.role}",
            "",
            f"- Date captured: {capture_date.isoformat()}",
            f"- Company: {args.company}",
            f"- Role: {args.role}",
            f"- Link: {args.link}",
            "",
            "## Full JD",
            "",
            jd_text.strip(),
            "",
        ]
    )
    (vacancy_dir / "vacancy.md").write_text(vacancy_md, encoding="utf-8")

    log_path = vacancy_dir / "log.md"
    log_path.write_text("# Application Log\n\n## Timeline\n", encoding="utf-8")
    append_log(log_path, "vacancy captured", f"{capture_date.isoformat()}T09:00")

    rows = load_tracking_rows(tracking_path)
    if any(row["id"] == application_id for row in rows):
        raise SystemExit(f"Tracking entry already exists for {application_id}")

    rows.append(
        {
            "id": application_id,
            "date": capture_date.isoformat(),
            "company": args.company,
            "role": args.role,
            "link": args.link,
            "status": "NEW",
            "last_action": "vacancy captured",
            "next_action": "prepare documents",
            "next_due": (capture_date + dt.timedelta(days=7)).isoformat(),
            "folder": f"applications/{application_id}",
            "contact": "[ADD CONTACT]",
            "notes": "",
        }
    )
    write_tracking_rows(tracking_path, rows)

    print(vacancy_dir)
    return 0


def run_track_event(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    tracking_path = ensure_tracking_file(workspace)
    rows = load_tracking_rows(tracking_path)
    matched = False

    for row in rows:
        if row["id"] != args.application_id:
            continue
        matched = True
        if args.status:
            row["status"] = args.status
        if args.last_action:
            row["last_action"] = args.last_action
        if args.next_action:
            row["next_action"] = args.next_action
        if args.next_due:
            row["next_due"] = args.next_due
        if args.contact:
            row["contact"] = args.contact
        if args.notes:
            row["notes"] = (row["notes"] + "; " + args.notes).strip("; ")
        log_path = workspace / row["folder"] / "log.md"
        append_log(log_path, args.log_note or args.last_action or "tracking updated")
        break

    if not matched:
        raise SystemExit(f"Application id not found: {args.application_id}")

    write_tracking_rows(tracking_path, rows)
    print(args.application_id)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap and operate the public job application workflow.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="Create a fresh public job-search workspace.")
    setup.add_argument("--workspace", required=True, help="Target workspace path")
    setup.add_argument("--candidate-file", help="JSON file with candidate seed data")
    setup.add_argument("--import", dest="imports", action="append", default=[], help="Existing source file to copy into source/originals")
    setup.add_argument("--linkedin-url", help="LinkedIn profile URL to save as a guided reference source")
    setup.add_argument("--skip-install", action="store_true", help="Skip dependency installation attempts")
    setup.add_argument("--force", action="store_true", help="Allow setup into an existing non-empty workspace")
    setup.set_defaults(handler=run_setup)

    capture = subparsers.add_parser("capture-vacancy", help="Create a vacancy folder and tracking entry.")
    capture.add_argument("--workspace", help="Workspace path. Defaults to pointer config.")
    capture.add_argument("--date", help="Capture date in YYYY-MM-DD format")
    capture.add_argument("--company", required=True, help="Company name")
    capture.add_argument("--role", required=True, help="Role title")
    capture.add_argument("--link", required=True, help="Vacancy URL")
    capture.add_argument("--jd-file", help="File containing the full job description")
    capture.add_argument("--jd-text", help="Inline full job description text")
    capture.set_defaults(handler=run_capture_vacancy)

    track = subparsers.add_parser("track-event", help="Update tracking and append a log entry.")
    track.add_argument("--workspace", help="Workspace path. Defaults to pointer config.")
    track.add_argument("--application-id", required=True, help="Tracking id, e.g. YYYY-MM-DD_company_role")
    track.add_argument("--status", help="New status value")
    track.add_argument("--last-action", help="Value for last_action")
    track.add_argument("--next-action", help="Value for next_action")
    track.add_argument("--next-due", help="Value for next_due in YYYY-MM-DD format")
    track.add_argument("--contact", help="Contact field value")
    track.add_argument("--notes", help="Notes fragment appended to the notes column")
    track.add_argument("--log-note", help="Timeline note appended to log.md")
    track.set_defaults(handler=run_track_event)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
