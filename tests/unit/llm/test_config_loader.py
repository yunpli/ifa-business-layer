from __future__ import annotations

from pathlib import Path

from ifa_business_layer.llm.config import ConfigLoader


def test_load_default_yaml_examples():
    cfg = ConfigLoader(Path(__file__).resolve().parents[3] / "config" / "llm").load()
    assert "jmr-oai" in cfg.providers
    assert "grok41_expert" in cfg.models
    assert cfg.models["grok41_expert"].model_id == "grok-4.1-expert"
