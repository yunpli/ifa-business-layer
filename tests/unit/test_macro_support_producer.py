from __future__ import annotations

from dataclasses import dataclass

import pytest

from ifa_business_layer.llm.types import LLMResponse
from ifa_business_layer.support.macro import EarlyMacroSupportProducer, LateMacroSupportProducer
from ifa_business_layer.support.types import SupportValidationError


@dataclass
class StubLLMService:
    response: LLMResponse

    def invoke(self, request):
        return self.response


def sample_evidence(**overrides):
    base = {
        "topic": "rates",
        "statement": "US yields stayed elevated into the Asia handoff.",
        "entity_refs": ["US10Y"],
        "metric_refs": ["yield_change_bp"],
        "source_layer": "slot_replay",
        "freshness_label": "fresh",
        "confidence": "medium",
        "impact_bias": "risk_off",
        "caution": "If CN beta stays resilient after open, treat rates as weak backdrop only.",
    }
    base.update(overrides)
    return base


def llm_json_payload(slot: str):
    return {
        "bundle": {
            "bundle_id": f"a_share:2026-04-22:{slot}:macro:support_macro",
            "market": "a_share",
            "business_date": "2026-04-22",
            "slot": slot,
            "agent_domain": "macro",
            "section_key": "support_macro",
            "section_type": "support",
            "producer": "business-layer",
            "producer_version": "macro_support_v1",
            "assembly_mode": "hybrid",
            "summary": "Macro support says yields are tightening risk appetite and should trim conviction in aggressive A-share chase setups.",
            "primary_relation": "adjust",
            "secondary_relations": ["counter"],
        },
        "facts": [
            {
                "fact_id": f"fact:macro:{slot}:rates",
                "object_key": "macro:rates",
                "fsj_kind": "fact",
                "fact_type": "macro",
                "statement": "US yields stayed elevated into the Asia handoff.",
                "entity_refs": ["US10Y"],
                "metric_refs": ["yield_change_bp"],
                "source_layer": "slot_replay",
                "freshness_label": "fresh",
                "confidence": "medium",
            }
        ],
        "signals": [
            {
                "signal_id": f"signal:macro:{slot}:rates",
                "object_key": "macro:rates",
                "fsj_kind": "signal",
                "signal_type": "risk",
                "statement": "Higher yields are a risk filter for speculative A-share risk appetite.",
                "based_on_fact_ids": [f"fact:macro:{slot}:rates"],
                "signal_strength": "medium",
                "horizon": "same_day" if slot == "early" else "t_plus_1",
                "confidence": "medium",
            }
        ],
        "judgments": [
            {
                "judgment_id": f"judgment:macro:{slot}:rates",
                "object_key": "macro:rates",
                "fsj_kind": "judgment",
                "judgment_type": "watch_item" if slot == "early" else "next_step",
                "statement": "Use rates as a conviction-adjuster rather than a standalone market call.",
                "judgment_action": "adjust",
                "based_on_signal_ids": [f"signal:macro:{slot}:rates"],
                "direction": "bearish",
                "priority": "p1",
                "invalidators": ["If A-share leadership expands despite higher yields, downgrade macro drag."],
                "confidence": "medium",
            }
        ],
    }


def test_early_macro_support_producer_accepts_llm_json_candidate():
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
    payload = EarlyMacroSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence()],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["section_key"] == "support_macro"
    assert as_dict["signals"][0]["based_on_fact_ids"] == ["fact:macro:early:rates"]


def test_late_macro_support_producer_falls_back_when_llm_text_is_not_json():
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
    payload = LateMacroSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence(topic="fx", impact_bias="neutral")],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["primary_relation"] == "adjust"
    assert as_dict["judgments"][0]["judgment_type"] == "next_step"


def test_macro_support_producer_requires_evidence():
    with pytest.raises(SupportValidationError):
        EarlyMacroSupportProducer().produce(business_date="2026-04-22", evidence_items=[])


def test_macro_support_producer_rejects_invalid_llm_object_key():
    bad = llm_json_payload("early")
    bad["facts"][0]["object_key"] = "macro:unknown"
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
        EarlyMacroSupportProducer(llm_service=service).produce(
            business_date="2026-04-22",
            evidence_items=[sample_evidence()],
        )
