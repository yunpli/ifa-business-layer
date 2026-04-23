from __future__ import annotations

from dataclasses import dataclass

import pytest

from ifa_business_layer.llm.types import LLMResponse
from ifa_business_layer.support.ai_tech import EarlyAITechSupportProducer, LateAITechSupportProducer
from ifa_business_layer.support.types import SupportValidationError


@dataclass
class StubLLMService:
    response: LLMResponse

    def invoke(self, request):
        return self.response


def sample_evidence(**overrides):
    base = {
        "topic": "leader_diffusion",
        "statement": "GPU and inference names extended beyond the first two leaders before the open.",
        "entity_refs": ["CPO", "GPU", "Inference"],
        "metric_refs": ["breadth_ratio", "limit_up_count"],
        "source_layer": "slot_replay",
        "freshness_label": "fresh",
        "confidence": "medium",
        "impact_bias": "supportive",
        "caution": "If the move stays concentrated in one leader and breadth stalls, treat the theme as narrow heat only.",
    }
    base.update(overrides)
    return base


def llm_json_payload(slot: str):
    return {
        "bundle": {
            "bundle_id": f"a_share:2026-04-22:{slot}:ai_tech:support_ai_tech",
            "market": "a_share",
            "business_date": "2026-04-22",
            "slot": slot,
            "agent_domain": "ai_tech",
            "section_key": "support_ai_tech",
            "section_type": "support",
            "producer": "business-layer",
            "producer_version": "ai_tech_support_v1",
            "assembly_mode": "hybrid",
            "summary": "AI-tech support says diffusion is broad enough to keep the theme on the mainline watchlist, but only with breadth confirmation.",
            "primary_relation": "support",
            "secondary_relations": ["adjust"],
        },
        "facts": [
            {
                "fact_id": f"fact:ai_tech:{slot}:leader_diffusion",
                "object_key": "ai_tech:leader_diffusion",
                "fsj_kind": "fact",
                "fact_type": "breadth",
                "statement": "GPU and inference names extended beyond the first two leaders before the open.",
                "entity_refs": ["CPO", "GPU", "Inference"],
                "metric_refs": ["breadth_ratio", "limit_up_count"],
                "source_layer": "slot_replay",
                "freshness_label": "fresh",
                "confidence": "medium",
            }
        ],
        "signals": [
            {
                "signal_id": f"signal:ai_tech:{slot}:leader_diffusion",
                "object_key": "ai_tech:leader_diffusion",
                "fsj_kind": "signal",
                "signal_type": "rotation",
                "statement": "Breadth expansion suggests the AI-tech move is diffusing beyond a single hot leader.",
                "based_on_fact_ids": [f"fact:ai_tech:{slot}:leader_diffusion"],
                "signal_strength": "medium",
                "horizon": "same_day" if slot == "early" else "t_plus_1",
                "confidence": "medium",
            }
        ],
        "judgments": [
            {
                "judgment_id": f"judgment:ai_tech:{slot}:leader_diffusion",
                "object_key": "ai_tech:leader_diffusion",
                "fsj_kind": "judgment",
                "judgment_type": "watch_item" if slot == "early" else "next_step",
                "statement": "Keep AI-tech high on the watchlist, but require breadth confirmation before upgrading conviction.",
                "judgment_action": "support" if slot == "early" else "confirm",
                "based_on_signal_ids": [f"signal:ai_tech:{slot}:leader_diffusion"],
                "direction": "bullish",
                "priority": "p1",
                "invalidators": ["If diffusion collapses back into one leader, downgrade AI-tech from mainline candidate to narrow speculation."],
                "confidence": "medium",
            }
        ],
    }


def test_early_ai_tech_support_producer_accepts_llm_json_candidate():
    service = StubLLMService(
        response=LLMResponse(
            provider_name="stub",
            model_alias="grok41_thinking",
            model_id="stub-model",
            adapter_name="stub",
            raw_text=None,
            parsed_json=llm_json_payload("early"),
            finish_reason="stop",
            usage=None,
            raw_response={},
        )
    )
    payload = EarlyAITechSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence()],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["section_key"] == "support_ai_tech"
    assert as_dict["signals"][0]["based_on_fact_ids"] == ["fact:ai_tech:early:leader_diffusion"]


def test_late_ai_tech_support_producer_falls_back_when_llm_text_is_not_json():
    service = StubLLMService(
        response=LLMResponse(
            provider_name="stub",
            model_alias="grok41_thinking",
            model_id="stub-model",
            adapter_name="stub",
            raw_text="not-json",
            parsed_json=None,
            finish_reason="stop",
            usage=None,
            raw_response={},
        )
    )
    payload = LateAITechSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence(topic="theme_exhaustion", impact_bias="stale")],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["primary_relation"] == "adjust"
    assert as_dict["judgments"][0]["judgment_type"] == "next_step"
    assert as_dict["judgments"][0]["judgment_action"] == "prepare"


def test_ai_tech_support_producer_requires_evidence():
    with pytest.raises(SupportValidationError):
        EarlyAITechSupportProducer().produce(business_date="2026-04-22", evidence_items=[])


def test_ai_tech_support_producer_rejects_invalid_llm_object_key():
    bad = llm_json_payload("early")
    bad["facts"][0]["object_key"] = "ai_tech:unknown"
    service = StubLLMService(
        response=LLMResponse(
            provider_name="stub",
            model_alias="grok41_thinking",
            model_id="stub-model",
            adapter_name="stub",
            raw_text=None,
            parsed_json=bad,
            finish_reason="stop",
            usage=None,
            raw_response={},
        )
    )
    with pytest.raises(SupportValidationError):
        EarlyAITechSupportProducer(llm_service=service).produce(
            business_date="2026-04-22",
            evidence_items=[sample_evidence()],
        )
