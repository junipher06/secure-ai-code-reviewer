"""Explicit local-only loading of an ignored environment file; never log values."""

import os
from pathlib import Path

from .errors import ReviewError


def load_local_env(path: Path) -> None:
    if os.environ.get("GITHUB_ACTIONS"):
        raise ReviewError("Local environment files are disabled in GitHub Actions.")
    if path.name != ".env":
        raise ReviewError("Local environment file must be named .env and ignored by Git.")
    values = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ReviewError("Invalid local environment file; use KEY=value lines.")
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in {"GROQ_API_KEY", "GITHUB_TOKEN"} or key in values:
            raise ReviewError("Unexpected or duplicate variable in local environment file.")
        values[key] = value.strip().strip("\"'")
    for key, value in values.items():
        os.environ.setdefault(key, value)
