from __future__ import annotations

import json
from typing import Any

import requests

from ..config import load_api_key
from ..types import LLMRequest, LLMResponse, ModelConfig, ProviderConfig


class AnthropicMessagesAdapter:
    name = "anthropic-messages"

    def invoke(self, provider: ProviderConfig, model: ModelConfig, request: LLMRequest) -> LLMResponse:
        api_key = load_api_key(provider)
        url = provider.base_url.rstrip("/") + "/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            **provider.headers,
        }
        body = {
            "model": model.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": self._content_text(request),
                }
            ],
            "max_tokens": request.max_tokens if request.max_tokens is not None else provider.default_max_tokens or 512,
            "stream": False,
        }
        if request.system_text:
            body["system"] = request.system_text
        if request.temperature is not None:
            body["temperature"] = request.temperature
        elif provider.default_temperature is not None:
            body["temperature"] = provider.default_temperature

        resp = requests.post(url, headers=headers, json=body, timeout=provider.timeout_seconds)
        raw = self._safe_json(resp)
        resp.raise_for_status()
        if not isinstance(raw, dict):
            raise RuntimeError("anthropic-messages adapter expected JSON object response")
        content = raw.get("content") if isinstance(raw, dict) else []
        text_parts = []
        for item in content or []:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text") or "")
        text = "\n".join(x for x in text_parts if x)
        parsed_json = self._maybe_parse_json(text, request.parse_json_response)
        return LLMResponse(
            provider_name=provider.name,
            model_alias=model.alias,
            model_id=model.model_id,
            adapter_name=self.name,
            raw_text=text,
            parsed_json=parsed_json,
            finish_reason=raw.get("stop_reason") if isinstance(raw, dict) else None,
            usage=raw.get("usage") if isinstance(raw, dict) else None,
            raw_response=raw,
        )

    def _content_text(self, request: LLMRequest) -> str:
        if request.loaded_input.mode == "json":
            return json.dumps(request.loaded_input.json_value, ensure_ascii=False, indent=2)
        return request.loaded_input.text or ""

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
