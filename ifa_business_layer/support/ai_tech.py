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


PROMPT_VERSION = "ai_tech_support_v1"
PRODUCER_VERSION = "ai_tech_support_v1"
AGENT_DOMAIN = "ai_tech"
SECTION_KEY = "support_ai_tech"
SECTION_TYPE = "support"
PRODUCER = "business-layer"


class SupportsInvoke(Protocol):
    def invoke(self, request: LLMRequest) -> LLMResponse: ...


@dataclass(slots=True)
class AITechSupportProducer:
    slot: str
    llm_service: SupportsInvoke | None = None
    model_alias: str = "grok41_expert"

    def produce(self, *, business_date: str, evidence_items: list[dict[str, Any]]) -> SupportPayload:
        if self.slot not in {"early", "late"}:
            raise SupportValidationError(f"unsupported slot: {self.slot}")
        if not evidence_items:
            raise SupportValidationError("ai_tech support requires at least one evidence item")

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
            "You are assembling a phase-1 A-share AI-tech support bundle. "
            "Return strict JSON only. Keep domain bounded to AI-tech relevance for A-share. "
            "Do not rewrite the whole market report. "
            "Ensure at least 1 fact, 1 signal, 1 judgment. "
            "Judgment must include invalidators. "
            "Use only allowed object keys: ai_tech:mainline_status, ai_tech:compute_chain, "
            "ai_tech:model_chain, ai_tech:application_chain, ai_tech:leader_diffusion, ai_tech:theme_exhaustion."
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
                        "object_key": "ai_tech:*",
                        "fsj_kind": "fact",
                        "fact_type": "market|breadth|theme|news|announcement|event",
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
                        "object_key": "ai_tech:*",
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
                        "object_key": "ai_tech:*",
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
            loaded_input=LoadedInput(mode="json", text=None, json_value=input_value, source="ai_tech_support_producer"),
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
        fact_id = f"fact:ai_tech:{self.slot}:{self._slug(object_key)}"
        signal_id = f"signal:ai_tech:{self.slot}:{self._slug(object_key)}"
        judgment_id = f"judgment:ai_tech:{self.slot}:{self._slug(object_key)}"

        bundle = SupportBundle(
            bundle_id=f"a_share:{business_date}:{self.slot}:ai_tech:support_ai_tech",
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
            fact_type=self._fallback_fact_type(top),
            statement=str(top.get("statement") or top.get("headline") or "AI-tech evidence requires operator review."),
            entity_refs=list(top.get("entity_refs") or [top.get("theme") or top.get("topic") or "ai_tech"]),
            metric_refs=list(top.get("metric_refs") or []),
            source_layer=str(top.get("source_layer") or "slot_replay"),
            freshness_label=str(top.get("freshness_label") or "unknown"),
            confidence=str(top.get("confidence") or "low"),
        )
        signal = SupportSignal(
            signal_id=signal_id,
            object_key=object_key,
            fsj_kind="signal",
            signal_type=self._fallback_signal_type(bundle.primary_relation, top),
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
            judgment_action=self._fallback_action(bundle.primary_relation),
            based_on_signal_ids=[signal_id],
            direction=self._fallback_direction(top),
            priority="p1",
            invalidators=[self._fallback_invalidator(top)],
            confidence=fact.confidence,
        )
        return SupportPayload(bundle=bundle, facts=[fact], signals=[signal], judgments=[judgment])

    def _fallback_object_key(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or item.get("theme") or "").lower()
        mapping = {
            "mainline_status": "ai_tech:mainline_status",
            "mainline": "ai_tech:mainline_status",
            "compute_chain": "ai_tech:compute_chain",
            "compute": "ai_tech:compute_chain",
            "model_chain": "ai_tech:model_chain",
            "models": "ai_tech:model_chain",
            "application_chain": "ai_tech:application_chain",
            "applications": "ai_tech:application_chain",
            "leader_diffusion": "ai_tech:leader_diffusion",
            "diffusion": "ai_tech:leader_diffusion",
            "theme_exhaustion": "ai_tech:theme_exhaustion",
            "exhaustion": "ai_tech:theme_exhaustion",
        }
        return mapping.get(topic, "ai_tech:mainline_status")

    def _fallback_fact_type(self, item: dict[str, Any]) -> str:
        fact_type = str(item.get("fact_type") or "").lower()
        if fact_type in {"market", "breadth", "theme", "news", "announcement", "event"}:
            return fact_type
        return "theme"

    def _fallback_relation(self, item: dict[str, Any]) -> str:
        bias = str(item.get("impact_bias") or item.get("bias") or "neutral").lower()
        if bias in {"supportive", "bullish", "positive", "mainline", "fresh"}:
            return "support"
        if bias in {"risk_off", "bearish", "negative", "exhausted", "stale"}:
            return "adjust"
        return "adjust"

    def _fallback_summary(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or item.get("theme") or "AI-tech")
        view = str(item.get("impact_bias") or item.get("bias") or "neutral").replace("_", " ")
        return f"AI-tech support treats {topic} as a {view} domain input that can refine mainline priority without replacing the main A-share thesis."

    def _fallback_signal_type(self, primary_relation: str, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or item.get("theme") or "").lower()
        if "diffusion" in topic:
            return "rotation"
        if "exhaust" in topic or primary_relation in {"adjust", "counter"}:
            return "risk"
        return "confirmation"

    def _fallback_signal(self, item: dict[str, Any]) -> str:
        topic = str(item.get("topic") or item.get("theme") or "AI-tech")
        return f"{topic} should be tracked as an AI-tech priority filter for same-session A-share theme selection, not as a standalone market-wide call."

    def _fallback_judgment(self, item: dict[str, Any]) -> str:
        if self.slot == "early":
            return "Use AI-tech as a prioritized monitoring lane at the open and demand diffusion or breadth confirmation before promoting it to mainline status."
        return "Carry the AI-tech read into next-session planning only if leadership, diffusion, or closing strength confirmed the theme during today’s tape."

    def _fallback_action(self, primary_relation: str) -> str:
        if self.slot == "early":
            return "support" if primary_relation == "support" else "observe"
        return "confirm" if primary_relation == "support" else "prepare"

    def _fallback_direction(self, item: dict[str, Any]) -> str:
        bias = str(item.get("impact_bias") or item.get("bias") or "neutral").lower()
        if bias in {"supportive", "bullish", "positive", "mainline", "fresh"}:
            return "bullish"
        if bias in {"risk_off", "bearish", "negative", "exhausted", "stale"}:
            return "bearish"
        if bias in {"mixed", "split"}:
            return "mixed"
        return "neutral"

    def _fallback_invalidator(self, item: dict[str, Any]) -> str:
        return str(
            item.get("caution")
            or item.get("invalidation")
            or "If AI-tech fails to show breadth, diffusion, or close-strength confirmation, downgrade this bundle to watch-only status."
        )

    def _required_questions(self) -> list[str]:
        if self.slot == "early":
            return [
                "Does AI-tech have pre-open mainline candidacy today?",
                "Which subthemes deserve priority monitoring?",
                "Which names/themes are stale leftovers rather than fresh signal?",
            ]
        return [
            "Was AI-tech today a mainline, branch line, or noise?",
            "Did the diffusion chain really form?",
            "Should AI-tech keep high priority tomorrow?",
        ]

    def _slug(self, object_key: str) -> str:
        return object_key.split(":", 1)[1].replace(":", "_")


class EarlyAITechSupportProducer(AITechSupportProducer):
    def __init__(self, llm_service: SupportsInvoke | None = None, model_alias: str = "grok41_expert") -> None:
        super().__init__(slot="early", llm_service=llm_service, model_alias=model_alias)


class LateAITechSupportProducer(AITechSupportProducer):
    def __init__(self, llm_service: SupportsInvoke | None = None, model_alias: str = "grok41_expert") -> None:
        super().__init__(slot="late", llm_service=llm_service, model_alias=model_alias)
