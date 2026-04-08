#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from workspace_utils import find_workspace_root, read_candidate_config


REQUIRED_COMMANDS = ("pandoc", "tectonic")


def ensure_commands() -> None:
    missing = [command for command in REQUIRED_COMMANDS if shutil.which(command) is None]
    if missing:
        raise SystemExit(f"Missing required commands: {', '.join(missing)}")


def resolve_paths(target: Path) -> tuple[Path, Path]:
    workspace = find_workspace_root(target)
    candidate = read_candidate_config(workspace)
    basename = candidate.get("pdf_cover_letter_basename", "cover_letter.pdf")

    if target.is_dir() and (target / "cover_letter.md").exists():
        source = target / "cover_letter.md"
        output = target / basename
        return source, output

    source = workspace / "templates" / "cover_letter.md"
    output = source.parent / basename
    return source, output


def export_pdf(target: Path) -> Path:
    ensure_commands()
    source, output = resolve_paths(target)
    if not source.exists():
        raise SystemExit(f"Missing input markdown file: {source}")

    command = [
        "pandoc",
        str(source),
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
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a cover letter PDF.")
    parser.add_argument("target", nargs="?", default=".", help="Workspace root or vacancy folder")
    args = parser.parse_args()
    output = export_pdf(Path(args.target))
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
