#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from workspace_utils import choose_python_command, find_workspace_root


def rebuild(root: Path) -> int:
    workspace = find_workspace_root(root)
    applications_root = root if root != workspace else workspace / "applications"
    exporter = workspace / "scripts" / "export_resume_pdf.py"
    python_command = choose_python_command()
    total = 0

    for resume_path in sorted(applications_root.glob("*/*")):
        if not resume_path.is_file() or resume_path.name != "resume_tailored.md":
            continue
        total += 1
        vacancy_dir = resume_path.parent
        subprocess.run([python_command, str(exporter), str(vacancy_dir)], check=True)

    print(f"rebuilt={total}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild resume PDFs for all application folders.")
    parser.add_argument("root", nargs="?", default=".", help="Workspace root or applications folder")
    args = parser.parse_args()
    return rebuild(Path(args.root))


if __name__ == "__main__":
    sys.exit(main())
