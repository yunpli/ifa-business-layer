from __future__ import annotations

from pathlib import Path

from ifa_business_layer.llm.io import render_output, write_output


def test_render_json_and_write(tmp_path: Path):
    rendered = render_output({"ok": True}, "json")
    assert '"ok": true' in rendered
    out = tmp_path / "out.json"
    write_output(rendered, out)
    assert out.exists()
    assert '"ok": true' in out.read_text(encoding="utf-8")
