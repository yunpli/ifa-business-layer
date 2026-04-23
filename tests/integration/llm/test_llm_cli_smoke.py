from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path('/Users/neoclaw/repos/ifa-business-layer')
PYTHON = Path('/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python')
CLI = REPO / 'scripts' / 'ifa_llm_cli.py'


def test_cli_requires_key_for_live_models():
    env = os.environ.copy()
    env['PYTHONPATH'] = str(REPO)
    env.pop('JMR_API_KEY', None)
    proc = subprocess.run(
        [str(PYTHON), str(CLI), '--model', 'grok41_expert', '--prompt', 'Who are you?'],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert 'JMR_API_KEY' in proc.stderr
