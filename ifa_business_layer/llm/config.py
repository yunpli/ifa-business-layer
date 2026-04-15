from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .types import ModelConfig, ProviderConfig


class ConfigError(RuntimeError):
    pass


@dataclass(slots=True)
class ConfigBundle:
    providers: dict[str, ProviderConfig]
    models: dict[str, ModelConfig]


class ConfigLoader:
    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir

    def load(self) -> ConfigBundle:
        providers_raw = self._read_yaml(self.config_dir / "providers.yaml", fallback=self.config_dir / "providers.example.yaml")
        models_raw = self._read_yaml(self.config_dir / "models.yaml", fallback=self.config_dir / "models.example.yaml")
        providers = self._parse_providers(providers_raw)
        models = self._parse_models(models_raw)
        return ConfigBundle(providers=providers, models=models)

    def _read_yaml(self, path: Path, fallback: Path | None = None) -> dict[str, Any]:
        target = path if path.exists() else fallback
        if target is None or not target.exists():
            raise ConfigError(f"config file not found: {path}")
        return yaml.safe_load(target.read_text(encoding="utf-8")) or {}

    def _parse_providers(self, payload: dict[str, Any]) -> dict[str, ProviderConfig]:
        raw = payload.get("providers") or {}
        out: dict[str, ProviderConfig] = {}
        for name, cfg in raw.items():
            out[name] = ProviderConfig(
                name=name,
                base_url=cfg["base_url"],
                api_type=cfg["api_type"],
                api_key_env=cfg["api_key_env"],
                timeout_seconds=int(cfg.get("timeout_seconds", 60)),
                headers=dict(cfg.get("headers") or {}),
                default_max_tokens=cfg.get("default_max_tokens"),
                default_temperature=cfg.get("default_temperature"),
            )
        return out

    def _parse_models(self, payload: dict[str, Any]) -> dict[str, ModelConfig]:
        raw = payload.get("models") or {}
        out: dict[str, ModelConfig] = {}
        for alias, cfg in raw.items():
            out[alias] = ModelConfig(
                alias=alias,
                provider=cfg["provider"],
                model_id=cfg["model_id"],
                display_name=cfg.get("display_name"),
                context_window=cfg.get("context_window"),
                capabilities=list(cfg.get("capabilities") or []),
                notes=cfg.get("notes"),
            )
        return out


def load_api_key(provider: ProviderConfig) -> str:
    value = os.environ.get(provider.api_key_env)
    if not value:
        raise ConfigError(
            f"missing API key for provider '{provider.name}'; expected env var {provider.api_key_env}"
        )
    return value
