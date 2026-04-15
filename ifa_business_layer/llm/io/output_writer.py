from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_output(result: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, indent=2)


def write_output(rendered: str, output_file: Path | None) -> None:
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered, encoding="utf-8")
