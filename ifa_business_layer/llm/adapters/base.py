from __future__ import annotations

from typing import Protocol

from ..types import LLMRequest, LLMResponse, ModelConfig, ProviderConfig


class BaseLLMAdapter(Protocol):
    name: str

    def invoke(
        self,
        provider: ProviderConfig,
        model: ModelConfig,
        request: LLMRequest,
    ) -> LLMResponse: ...
