from __future__ import annotations

from dataclasses import dataclass

import pytest

from ifa_business_layer.llm.types import LLMResponse
from ifa_business_layer.support.commodities import EarlyCommoditiesSupportProducer, LateCommoditiesSupportProducer
from ifa_business_layer.support.types import SupportValidationError


@dataclass
class StubLLMService:
    response: LLMResponse

    def invoke(self, request):
        return self.response


def sample_evidence(**overrides):
    base = {
        "topic": "industrial_metals",
        "statement": "Copper and aluminum strength persisted into the China open, keeping the equipment and resources mapping alive.",
        "entity_refs": ["CU", "AL", "有色"],
        "metric_refs": ["futures_change_pct", "sector_relative_strength"],
        "source_layer": "slot_replay",
        "freshness_label": "fresh",
        "confidence": "medium",
        "impact_bias": "supportive",
        "caution": "If the A-share metals chain fails to confirm after open, treat the commodity move as unproven cross-asset noise.",
    }
    base.update(overrides)
    return base


def llm_json_payload(slot: str):
    return {
        "bundle": {
            "bundle_id": f"a_share:2026-04-22:{slot}:commodities:support_commodities",
            "market": "a_share",
            "business_date": "2026-04-22",
            "slot": slot,
            "agent_domain": "commodities",
            "section_key": "support_commodities",
            "section_type": "support",
            "producer": "business-layer",
            "producer_version": "commodities_support_v1",
            "assembly_mode": "hybrid",
            "summary": "Commodities support says industrial metals are reinforcing the A-share resource chain, but only while equity mapping remains visible.",
            "primary_relation": "support",
            "secondary_relations": ["adjust"],
        },
        "facts": [
            {
                "fact_id": f"fact:commodities:{slot}:industrial_metals",
                "object_key": "commodity:industrial_metals",
                "fsj_kind": "fact",
                "fact_type": "commodity",
                "statement": "Copper and aluminum strength persisted into the China open, keeping the equipment and resources mapping alive.",
                "entity_refs": ["CU", "AL", "有色"],
                "metric_refs": ["futures_change_pct", "sector_relative_strength"],
                "source_layer": "slot_replay",
                "freshness_label": "fresh",
                "confidence": "medium",
            }
        ],
        "signals": [
            {
                "signal_id": f"signal:commodities:{slot}:industrial_metals",
                "object_key": "commodity:industrial_metals",
                "fsj_kind": "signal",
                "signal_type": "strengthening",
                "statement": "The commodity move is strengthening the A-share industrial-metals mapping instead of acting as isolated futures noise.",
                "based_on_fact_ids": [f"fact:commodities:{slot}:industrial_metals"],
                "signal_strength": "medium",
                "horizon": "same_day" if slot == "early" else "t_plus_1",
                "confidence": "medium",
            }
        ],
        "judgments": [
            {
                "judgment_id": f"judgment:commodities:{slot}:industrial_metals",
                "object_key": "commodity:industrial_metals",
                "fsj_kind": "judgment",
                "judgment_type": "watch_item" if slot == "early" else "next_step",
                "statement": "Keep the chain in the support stack and only promote it when the equity transmission path is confirmed.",
                "judgment_action": "support" if slot == "early" else "confirm",
                "based_on_signal_ids": [f"signal:commodities:{slot}:industrial_metals"],
                "direction": "bullish",
                "priority": "p1",
                "invalidators": ["If the linked A-share metals chain fails to confirm, downgrade the commodity read to weak correlation."],
                "confidence": "medium",
            }
        ],
    }


def test_early_commodities_support_producer_accepts_llm_json_candidate():
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
    payload = EarlyCommoditiesSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence()],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["section_key"] == "support_commodities"
    assert as_dict["signals"][0]["based_on_fact_ids"] == ["fact:commodities:early:industrial_metals"]


def test_late_commodities_support_producer_falls_back_when_llm_text_is_not_json():
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
    payload = LateCommoditiesSupportProducer(llm_service=service).produce(
        business_date="2026-04-22",
        evidence_items=[sample_evidence(topic="gold", impact_bias="false_positive")],
    )
    as_dict = payload.to_dict()
    assert as_dict["bundle"]["assembly_mode"] == "hybrid"
    assert as_dict["bundle"]["primary_relation"] == "counter"
    assert as_dict["judgments"][0]["judgment_type"] == "next_step"
    assert as_dict["judgments"][0]["judgment_action"] == "prepare"


def test_commodities_support_producer_requires_evidence():
    with pytest.raises(SupportValidationError):
        EarlyCommoditiesSupportProducer().produce(business_date="2026-04-22", evidence_items=[])


def test_commodities_support_producer_rejects_invalid_llm_object_key():
    bad = llm_json_payload("early")
    bad["facts"][0]["object_key"] = "commodity:unknown"
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
        EarlyCommoditiesSupportProducer(llm_service=service).produce(
            business_date="2026-04-22",
            evidence_items=[sample_evidence()],
        )
