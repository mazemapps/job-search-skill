from __future__ import annotations

import json
import shutil
from pathlib import Path


def read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        cleaned = value.strip().strip('"').strip("'")
        data[key.strip()] = cleaned
    return data


def find_workspace_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / "config" / "candidate.yaml").exists():
            return candidate
    raise FileNotFoundError("Could not find workspace root containing config/candidate.yaml")


def read_candidate_config(workspace: Path) -> dict[str, str]:
    return read_simple_yaml(workspace / "config" / "candidate.yaml")


def choose_python_command() -> str:
    return shutil.which("python3") or shutil.which("python") or "python3"


def to_json(data: dict[str, str]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=True)
