from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


OutputFormat = Literal["text", "json"]
InputMode = Literal["text", "json"]


@dataclass(slots=True)
class ProviderConfig:
    name: str
    base_url: str
    api_type: str
    api_key_env: str
    timeout_seconds: int = 60
    headers: dict[str, str] = field(default_factory=dict)
    default_max_tokens: int | None = None
    default_temperature: float | None = None


@dataclass(slots=True)
class ModelConfig:
    alias: str
    provider: str
    model_id: str
    display_name: str | None = None
    context_window: int | None = None
    capabilities: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass(slots=True)
class LoadedInput:
    mode: InputMode
    text: str | None
    json_value: dict[str, Any] | list[Any] | None
    source: str


@dataclass(slots=True)
class LLMRequest:
    model_alias: str
    loaded_input: LoadedInput
    output_format: OutputFormat = "text"
    temperature: float | None = None
    max_tokens: int | None = None
    parse_json_response: bool = False
    system_text: str | None = None


@dataclass(slots=True)
class LLMResponse:
    provider_name: str
    model_alias: str
    model_id: str
    adapter_name: str
    raw_text: str | None
    parsed_json: dict[str, Any] | list[Any] | None
    finish_reason: str | None
    usage: dict[str, Any] | None
    raw_response: dict[str, Any] | list[Any] | None
    error: str | None = None

    def to_envelope(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model_alias": self.model_alias,
            "model_id": self.model_id,
            "adapter": self.adapter_name,
            "finish_reason": self.finish_reason,
            "text": self.raw_text,
            "parsed_json": self.parsed_json,
            "usage": self.usage,
            "raw_response": self.raw_response,
            "error": self.error,
        }


@dataclass(slots=True)
class CLIArgs:
    model: str
    prompt: str | None
    input_file: Path | None
    output_format: OutputFormat
    output_file: Path | None
    stdin: bool
    temperature: float | None
    max_tokens: int | None
    config_dir: Path
    parse_json_response: bool
    system_file: Path | None
