from __future__ import annotations

import json
import sys
from pathlib import Path

from ..types import LoadedInput


class InputError(RuntimeError):
    pass


ALLOWED_SUFFIXES = {".txt", ".md", ".json"}


def load_input(prompt: str | None, input_file: Path | None, stdin: bool) -> LoadedInput:
    chosen = sum(bool(x) for x in [prompt, input_file, stdin])
    if chosen != 1:
        raise InputError("exactly one input source must be provided: --prompt, --input-file, or --stdin")

    if prompt is not None:
        return LoadedInput(mode="text", text=prompt, json_value=None, source="prompt")

    if input_file is not None:
        suffix = input_file.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise InputError(f"unsupported input file type: {suffix}")
        raw = input_file.read_text(encoding="utf-8")
        if suffix == ".json":
            value = json.loads(raw)
            return LoadedInput(mode="json", text=None, json_value=value, source=str(input_file))
        return LoadedInput(mode="text", text=raw, json_value=None, source=str(input_file))

    raw = sys.stdin.read()
    if not raw.strip():
        raise InputError("stdin input is empty")
    return LoadedInput(mode="text", text=raw, json_value=None, source="stdin")
