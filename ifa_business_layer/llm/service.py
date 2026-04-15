from __future__ import annotations

from pathlib import Path

from .adapters import AnthropicMessagesAdapter, OpenAICompatibleAdapter
from .config import ConfigError, ConfigLoader
from .types import LLMRequest, LLMResponse


class LLMService:
    def __init__(self, config_dir: Path) -> None:
        self.bundle = ConfigLoader(config_dir).load()
        self.adapters = {
            "openai-completions": OpenAICompatibleAdapter(),
            "anthropic-messages": AnthropicMessagesAdapter(),
        }

    def invoke(self, request: LLMRequest) -> LLMResponse:
        model = self.bundle.models.get(request.model_alias)
        if not model:
            raise ConfigError(f"unknown model alias: {request.model_alias}")
        provider = self.bundle.providers.get(model.provider)
        if not provider:
            raise ConfigError(f"provider not found for model alias '{request.model_alias}': {model.provider}")
        adapter = self.adapters.get(provider.api_type)
        if not adapter:
            raise ConfigError(f"unsupported api_type: {provider.api_type}")
        return adapter.invoke(provider=provider, model=model, request=request)
