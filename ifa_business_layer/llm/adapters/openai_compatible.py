from __future__ import annotations

import json
from typing import Any

import requests

from ..config import load_api_key
from ..types import LLMRequest, LLMResponse, ModelConfig, ProviderConfig


class OpenAICompatibleAdapter:
    name = "openai-compatible"

    def invoke(self, provider: ProviderConfig, model: ModelConfig, request: LLMRequest) -> LLMResponse:
        api_key = load_api_key(provider)
        url = provider.base_url.rstrip("/") + "/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **provider.headers,
        }
        body = {
            "model": model.model_id,
            "messages": self._build_messages(request),
            "stream": False,
        }
        max_tokens = request.max_tokens if request.max_tokens is not None else provider.default_max_tokens
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        temperature = request.temperature if request.temperature is not None else provider.default_temperature
        if temperature is not None:
            body["temperature"] = temperature

        resp = requests.post(url, headers=headers, json=body, timeout=provider.timeout_seconds)
        raw = self._safe_json(resp)
        resp.raise_for_status()
        if not isinstance(raw, dict):
            raise RuntimeError("openai-compatible adapter expected JSON object response")
        choice = ((raw.get("choices") or [{}])[0]) if isinstance(raw, dict) else {}
        message = choice.get("message") or {}
        text = message.get("content")
        parsed_json = self._maybe_parse_json(text, request.parse_json_response)
        return LLMResponse(
            provider_name=provider.name,
            model_alias=model.alias,
            model_id=model.model_id,
            adapter_name=self.name,
            raw_text=text,
            parsed_json=parsed_json,
            finish_reason=choice.get("finish_reason"),
            usage=raw.get("usage") if isinstance(raw, dict) else None,
            raw_response=raw,
        )

    def _build_messages(self, request: LLMRequest) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if request.system_text:
            messages.append({"role": "system", "content": request.system_text})
        if request.loaded_input.mode == "json":
            content = json.dumps(request.loaded_input.json_value, ensure_ascii=False, indent=2)
        else:
            content = request.loaded_input.text or ""
        messages.append({"role": "user", "content": content})
        return messages

    def _maybe_parse_json(self, text: str | None, enabled: bool) -> dict[str, Any] | list[Any] | None:
        if not enabled or not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _safe_json(self, response: requests.Response) -> dict[str, Any] | list[Any]:
        try:
            return response.json()
        except Exception:
            return {"non_json_body": response.text}
