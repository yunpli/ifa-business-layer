#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ifa_business_layer.llm.io import InputError, load_input, render_output, write_output
from ifa_business_layer.llm.service import LLMService
from ifa_business_layer.llm.types import LLMRequest


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="IFA business-layer reusable LLM utility")
    p.add_argument("--model", required=True)
    p.add_argument("--prompt")
    p.add_argument("--input-file", type=Path)
    p.add_argument("--output-format", choices=["text", "json"], default="text")
    p.add_argument("--output-file", type=Path)
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--temperature", type=float)
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--config-dir", type=Path, default=Path("config/llm"))
    p.add_argument("--parse-json-response", action="store_true")
    p.add_argument("--system-file", type=Path)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        loaded = load_input(args.prompt, args.input_file, args.stdin)
        system_text = args.system_file.read_text(encoding="utf-8") if args.system_file else None
        service = LLMService(args.config_dir)
        response = service.invoke(
            LLMRequest(
                model_alias=args.model,
                loaded_input=loaded,
                output_format=args.output_format,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                parse_json_response=args.parse_json_response,
                system_text=system_text,
            )
        )
        payload = response.to_envelope() if args.output_format == "json" else (response.raw_text or "")
        rendered = render_output(payload, args.output_format)
        write_output(rendered, args.output_file)
        print(rendered)
        return 0
    except InputError as e:
        print(f"input_error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
