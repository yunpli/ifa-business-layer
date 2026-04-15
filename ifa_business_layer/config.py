from __future__ import annotations

import os
from pathlib import Path

STANDARD_VENV = "/Users/neoclaw/repos/ifa-data-platform/.venv"
STANDARD_PLATFORM_REPO = "/Users/neoclaw/repos/ifa-data-platform"
DEFAULT_SCHEMA = os.environ.get("IFA_DB_SCHEMA", "ifa2")


def load_database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    env_path = Path(STANDARD_PLATFORM_REPO) / ".env"
    for line in env_path.read_text().splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("DATABASE_URL not found in environment or standard .env")
