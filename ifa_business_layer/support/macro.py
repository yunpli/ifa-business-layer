from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from ifa_business_layer.llm.types import LLMRequest, LLMResponse, LoadedInput

from .types import (
    SupportBundle,
    SupportFact,
    SupportJudgment,
    SupportPayload,
    SupportSignal,
    SupportValidationError,
)


PROMPT_VERSION = "macro_support_v1"
PRODUCER_VERSION = "macro_support_v1"
AGENT_DOMAIN = "macro"
SECTION_KEY = "support_macro"
SECTION_TYPE = "support"
PRODUCER = "business-layer"


class SupportsInvoke(Protocol):
    def invoke(self, request: LLMRequest) -> LLMResponse: ...


@dataclass(slots=True)
class MacroSupportProducer:
    slot: str
    llm_service: SupportsInvoke | None = None
    model_alias: str = "grok41_thinking"

    def produce(self, *, business_date: str, evidence_items: list[dict[str, Any]]) -> SupportPayload:
        if self.slot not in {"early", "late"}:
            raise SupportValidationError(f"unsupported slot: {self.slot}")
        if not evidence_items:
            raise SupportValidationError("macro support requires at least one evidence item")

        assembly_mode = "rule_assembled"
        if self.llm_service is not None:
            response = self.llm_service.invoke(self._build_request(business_date=business_date, evidence_items=evidence_items))
            candidate = self._extract_candidate(response)
            if candidate is not None:
                payload = self._coerce_payload(candidate)
                payload.validate()
                return payload
            assembly_mode = "hybrid"

        payload = self._fallback_payload(
            business_date=business_date,
            evidence_items=evidence_items,
            assembly_mode=assembly_mode,
        )
        payload.validate()
        return payload

    def _build_request(self, *, business_date: str, evidence_items: list[dict[str, Any]]) -> LLMRequest:
        system_text = (
            "You are assembling a phase-1 A-share macro support bundle. "
            "Return strict JSON only. Keep domain bounded to macro relevance for A-share. "
            "Do not rewrite the whole market report. "
            "Ensure at least 1 fact, 1 signal, 1 judgment. "
            "Judgment must include invalidators. "
            "Use only allowed object keys: macro:liquidity, macro:rates, macro:fx, "
            "macro:policy_expectation, macro:risk_appetite."
        )
        input_value = {
            "prompt_version": PROMPT_VERSION,
            "market": "a_share",
            "business_date": business_date,
            "slot": self.slot,
            "agent_domain": AGENT_DOMAIN,
            "section_key": SECTION_KEY,
            "required_questions": self._required_questions(),
            "evidence_items": evidence_items,
            "required_json_shape": {
                "bundle": {
                    "bundle_id": "string",
                    "market": "a_share",
                    "business_date": business_date,
                    "slot": self.slot,
                    "agent_domain": AGENT_DOMAIN,
                    "section_key": SECTION_KEY,
                    "section_type": SECTION_TYPE,
                    "producer": PRODUCER,
                    "producer_version": PRODUCER_VERSION,
                    "assembly_mode": "hybrid",
                    "summary": "one sentence",
                    "primary_relation": "support|adjust|counter",
                    "secondary_relations": ["support|adjust|counter"],
                },
                "facts": [
                    {
                        "fact_id": "string",
                        "object_key": "macro:*",
                        "fsj_kind": "fact",
                        "fact_type": "macro",
                        "statement": "string",
                        "entity_refs": ["string"],
                        "metric_refs": ["string"],
                        "source_layer": "lowfreq|midfreq|highfreq|archive_v2|slot_replay|business_seed",
                        "freshness_label": "fresh|same_slot|t_minus_1|stale|unknown",
                        "confidence": "high|medium|low",
                    }
                ],
                "signals": [
                    {
                        "signal_id": "string",
                        "object_key": "macro:*",
                        "fsj_kind": "signal",
                        "signal_type": "strengthening|weakening|rotation|divergence|confirmation|risk",
                        "statement": "string",
                        "based_on_fact_ids": ["string"],
                        "signal_strength": "high|medium|low",
                        "horizon": "intraday|same_day|t_plus_1",
                        "confidence": "high|medium|low",
                    }
                ],
                "judgments": [
                    {
                        "judgment_id": "string",
                        "object_key": "macro:*",
                        "fsj_kind": "judgment",
                        "judgment_type": "support|risk|watch_item|next_step",
                        "statement": "string",
                        "judgment_action": "support|adjust|confirm|downgrade|observe|prepare",
                        "based_on_signal_ids": ["string"],
                        "direction": "bullish|bearish|mixed|neutral|conditional",
                        "priority": "p0|p1|p2",
                        "invalidators": ["string"],
                        "confidence": "high|medium|low",
                    }
                ],
            },
        }
        return LLMRequest(
            model_alias=self.model_alias,
            loaded_input=LoadedInput(mode="json", text=None, json_value=input_value, source="macro_support_producer"),
            output_format="json",
            parse_json_response=True,
            system_text=system_text,
            temperature=0.2,
        )

    def _extract_candidate(self, response: LLMResponse) -> dict[str, Any] | None:
        if isinstance(response.parsed_json, dict):
            return response.parsed_json
        if response.raw_text:
            try:
                parsed = json.loads(response.raw_text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
        return None

    def _coerce_payload(self, candidate: dict[str, Any]) -> SupportPayload:
        bundle = SupportBundle(**candidate["bundle"])
        facts = [SupportFact(**item) for item in candidate["facts"]]
        signals = [SupportSignal(**item) for item in candidate["signals"]]
        judgments = [SupportJudgment(**item) for item in candidate["judgments"]]
        return SupportPayload(bundle=bundle, facts=facts, signals=signals, judgments=judgments)

    def _fallback_payload(self, *, business_date: str, evidence_items: list[dict[str, Any]], assembly_mode: str) -> SupportPayload:
        top = evidence_items[0]
        object_key = self._fallback_object_key(top)
        fact_id = f"fact:macro:{self.slot}:{self._slug(object_key)}"
        signal_id = f"signal:macro:{self.slot}:{self._slug(object_key)}"
        judgment_id = f"judgment:macro:{self.slot}:{self._slug(object_key)}"

        bundle = SupportBundle(
            bundle_id=f"a_share:{business_date}:{self.slot}:macro:support_macro",
            market="a_share",
            business_date=business_date,
            slot=self.slot,
            agent_domain=AGENT_DOMAIN,
            section_key=SECTION_KEY,
            section_type=SECTION_TYPE,
            producer=PRODUCER,
            producer_version=PRODUCER_VERSION,
            assembly_mode=assembly_mode,
            summary=self._fallback_summary(top),
            primary_relation=self._fallback_relation(top),
            secondary_relations=[],
        )
        fact = SupportFact(
            fact_id=fact_id,
            object_key=object_key,
            fsj_kind="fact",
            fact_type="macro",
            statement=str(top.get("statement") or top.get("headline") or "Macro evidence requires operator review."),
            entity_refs=list(top.get("entity_refs") or [top.get("topic") or "macro"]),
            metric_refs=list(top.get("metric_refs") or []),
            source_layer=str(top.get("source_layer") or "slot_replay"),
            freshness_label=str(top.get("freshness_label") or "unknown"),
            confidence=str(top.get("confidence") or "low"),
        )
        signal = SupportSignal(
            signal_id=signal_id,
            object_key=object_key,
            fsj_kind="signal",
            signal_type="risk" if bundle.primary_relation in {"adjust", "counter"} else "confirmation",
            statement=self._fallback_signal(top),
            based_on_fact_ids=[fact_id],
            signal_strength="medium" if fact.confidence in {"high", "medium"} else "low",
            horizon="same_day" if self.slot == "early" else "t_plus_1",
            confidence=fact.confidence,
        )
        judgment = SupportJudgment(
            judgment_id=judgment_id,
            object_key=object_key,
            fsj_kind="judgment",
            judgment_type="watch_item" if self.slot == "early" else "next_step",
            statement=self._fallback_judgment(top),
            judgment_action="observe" if bundle.primary_relation == "counter" else "adjust",
            based_on_signal_ids=[signal_id],
            direction=self._fallback_direction(top),
            priority="p1",
            invalidators=[self._fallback_invalidator(top)],
            confidence=fact.confidence,
        )
        return SupportPayload(bundle=bundle, facts=[fact], signals=[signal], judgments=[judgment])

    def _fallback_object_key(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or "").lower()
        mapping = {
            "liquidity": "macro:liquidity",
            "rates": "macro:rates",
            "fx": "macro:fx",
            "policy_expectation": "macro:policy_expectation",
            "risk_appetite": "macro:risk_appetite",
        }
        return mapping.get(topic, "macro:risk_appetite")

    def _fallback_relation(self, item: dict[str, Any]) -> str:
        bias = str(item.get("impact_bias") or item.get("bias") or "neutral").lower()
        if bias in {"risk_off", "bearish", "negative"}:
            return "adjust"
        if bias in {"supportive", "bullish", "positive"}:
            return "support"
        return "adjust"

    def _fallback_summary(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or "macro backdrop")
        view = str(item.get("impact_bias") or item.get("bias") or "neutral").replace("_", " ")
        return f"Macro support flags {topic} as a {view} input that should refine, not replace, the main A-share thesis."

    def _fallback_signal(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or "macro backdrop")
        return f"{topic} should be treated as a same-session macro filter for A-share risk appetite rather than a standalone trade thesis."

    def _fallback_judgment(self, item: dict[str, Any]) -> str:
        if self.slot == "early":
            return "Use macro as an opening bias filter and watch whether price action confirms the implied risk appetite shift."
        return "Carry the macro variable into next-session monitoring and downgrade its importance if it failed to influence today’s tape."

    def _fallback_direction(self, item: dict[str, Any]) -> str:
        bias = str(item.get("impact_bias") or item.get("bias") or "neutral").lower()
        if bias in {"supportive", "bullish", "positive"}:
            return "bullish"
        if bias in {"risk_off", "bearish", "negative"}:
            return "bearish"
        return "neutral"

    def _fallback_invalidator(self, item: dict[str, Any]) -> str:
        return str(item.get("caution") or item.get("invalidation") or "If A-share price action ignores the macro cue, downgrade this bundle to background noise.")

    def _required_questions(self) -> list[str]:
        if self.slot == "early":
            return [
                "Is today’s macro background risk-on, risk-off, or neutral for A-share?",
                "What macro change must be surfaced before the open?",
                "What macro misread risk could distort the main thesis today?",
            ]
        return [
            "Did macro actually matter today, or was it just background noise?",
            "Did macro act as driver, amplifier, or weak backdrop?",
            "What macro variable must roll into next-day monitoring?",
        ]

    def _slug(self, object_key: str) -> str:
        return object_key.split(":", 1)[1].replace(":", "_")


class EarlyMacroSupportProducer(MacroSupportProducer):
    def __init__(self, llm_service: SupportsInvoke | None = None, model_alias: str = "grok41_thinking") -> None:
        super().__init__(slot="early", llm_service=llm_service, model_alias=model_alias)


class LateMacroSupportProducer(MacroSupportProducer):
    def __init__(self, llm_service: SupportsInvoke | None = None, model_alias: str = "grok41_thinking") -> None:
        super().__init__(slot="late", llm_service=llm_service, model_alias=model_alias)
