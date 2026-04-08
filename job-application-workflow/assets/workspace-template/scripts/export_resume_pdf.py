#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from workspace_utils import find_workspace_root, read_candidate_config


REQUIRED_COMMANDS = ("pandoc", "tectonic")


def ensure_commands() -> None:
    missing = [command for command in REQUIRED_COMMANDS if shutil.which(command) is None]
    if missing:
        raise SystemExit(f"Missing required commands: {', '.join(missing)}")


def normalize_resume_markdown(content: str) -> str:
    lines = content.splitlines()
    output: list[str] = []
    previous = None
    for line in lines:
        if previous is not None:
            if line.startswith("Tech stack:") and not previous.endswith("\\") and not previous.endswith("  "):
                previous = previous + " \\"
            output.append(previous)
        previous = line
    if previous is not None:
        output.append(previous)
    return "\n".join(output) + "\n"


def resolve_paths(target: Path) -> tuple[Path, Path]:
    workspace = find_workspace_root(target)
    candidate = read_candidate_config(workspace)
    basename = candidate.get("pdf_resume_basename", "resume.pdf")

    if target.is_dir() and (target / "resume_tailored.md").exists():
        source = target / "resume_tailored.md"
        output = target / basename
        return source, output

    source = workspace / "source" / "working" / "master_resume_2p.md"
    output = source.parent / basename
    return source, output


def export_pdf(target: Path) -> Path:
    ensure_commands()
    source, output = resolve_paths(target)
    if not source.exists():
        raise SystemExit(f"Missing input markdown file: {source}")

    normalized = normalize_resume_markdown(source.read_text(encoding="utf-8"))
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write(normalized)
        temp_path = Path(handle.name)

    try:
        command = [
            "pandoc",
            str(temp_path),
            "--pdf-engine=tectonic",
            "-V",
            "geometry:margin=0.7in",
            "-V",
            "fontfamily=tgheros",
            "-V",
            "fontsize=10pt",
            "-V",
            "linestretch=1.08",
            "-V",
            "urlcolor=black",
            "-V",
            "papersize=letter",
            "-o",
            str(output),
        ]
        subprocess.run(command, check=True)
    finally:
        temp_path.unlink(missing_ok=True)

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a baseline or tailored resume PDF.")
    parser.add_argument("target", nargs="?", default=".", help="Workspace root or vacancy folder")
    args = parser.parse_args()
    output = export_pdf(Path(args.target))
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
