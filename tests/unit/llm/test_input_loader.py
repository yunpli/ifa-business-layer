from __future__ import annotations

from pathlib import Path

from ifa_business_layer.llm.io import InputError, load_input


FIX = Path(__file__).resolve().parents[2] / "fixtures" / "llm"


def test_load_prompt():
    loaded = load_input("hello", None, False)
    assert loaded.mode == "text"
    assert loaded.text == "hello"


def test_load_markdown_file():
    loaded = load_input(None, FIX / "who_are_you.md", False)
    assert loaded.mode == "text"
    assert "Who are you" in loaded.text


def test_load_json_file():
    loaded = load_input(None, FIX / "simple_payload.json", False)
    assert loaded.mode == "json"
    assert loaded.json_value["task"] == "identity_check"


def test_reject_ambiguous_sources():
    try:
        load_input("hello", FIX / "who_are_you.md", False)
    except InputError:
        return
    raise AssertionError("expected InputError")
