#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path('/Users/neoclaw/repos/ifa-business-layer')
PY = Path('/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python')
CLI = REPO / 'scripts' / 'ifa_llm_cli.py'
MATRIX = REPO / 'docs' / 'LLM_LIVE_VALIDATION_MATRIX.md'
FIXTURE = REPO / 'tests' / 'fixtures' / 'llm' / 'who_are_you.md'

TOKEN = os.environ['JMR_API_KEY']


def write_models(provider: str) -> None:
    path = REPO / 'config' / 'llm' / 'models.yaml'
    path.write_text(
        f'''models:\n  grok41_expert:\n    provider: {provider}\n    model_id: grok-4.1-expert\n  grok41_thinking:\n    provider: {provider}\n    model_id: grok-4.1-thinking\n  gemini31_pro_jmr:\n    provider: {provider}\n    model_id: gemini-3.1-pro\n  gpt_oss_120b_free:\n    provider: {provider}\n    model_id: openai/gpt-oss-120b:free\n''',
        encoding='utf-8',
    )


def run_cmd(args: list[str], timeout_sec: int = 25) -> tuple[bool, str, str]:
    env = os.environ.copy()
    env['PYTHONPATH'] = str(REPO)
    env['JMR_API_KEY'] = TOKEN
    try:
        proc = subprocess.run(
            args,
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return proc.returncode == 0, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ''
        if isinstance(stdout, bytes):
            stdout = stdout.decode('utf-8', errors='replace')
        stderr = e.stderr or ''
        if isinstance(stderr, bytes):
            stderr = stderr.decode('utf-8', errors='replace')
        extra = f'timeout after {timeout_sec}s'
        if stderr:
            extra += f'; {stderr}'
        return False, stdout, extra


def short(text: str, n: int = 100) -> str:
    return (text or '').strip().replace('\n', ' ').replace('|', '/')[:n] or '-'


def validate(provider: str, adapter: str, alias: str, real_model: str) -> str:
    cmd = [str(PY), str(CLI), '--model', alias, '--prompt', 'Who are you?']
    ok, stdout, stderr = run_cmd(cmd)
    stdout_pass = ok and bool(stdout.strip())
    summary = short(stdout)
    notes = short(stderr, 180) if stderr.strip() else '-'

    out_path = Path(f'/tmp/{alias}_live_out.txt')
    ok_file, _, stderr_file = run_cmd([str(PY), str(CLI), '--model', alias, '--prompt', 'Who are you?', '--output-file', str(out_path)])
    file_pass = ok_file and out_path.exists() and out_path.read_text(encoding='utf-8').strip() != ''
    if not file_pass and notes == '-':
        notes = short(stderr_file, 180)

    ok_input, stdout_input, stderr_input = run_cmd([str(PY), str(CLI), '--model', alias, '--input-file', str(FIXTURE)])
    input_pass = ok_input and bool(stdout_input.strip())
    if not input_pass and notes == '-':
        notes = short(stderr_input, 180)

    overall = stdout_pass and file_pass and input_pass
    return (
        f"| {provider} | {alias} | {real_model} | {adapter} | "
        f"`{str(PY)} scripts/ifa_llm_cli.py --model {alias} --prompt 'Who are you?'` | "
        f"{'PASS' if stdout_pass else 'FAIL'} | {'PASS' if file_pass else 'FAIL'} | {'PASS' if input_pass else 'FAIL'} | "
        f"{'PASS' if overall else 'FAIL'} | {summary} | {notes} |"
    )


def main() -> int:
    rows: list[str] = []

    write_models('jmr-oai')
    rows.append(validate('jmr-oai', 'openai-compatible', 'grok41_expert', 'grok-4.1-expert'))
    rows.append(validate('jmr-oai', 'openai-compatible', 'grok41_thinking', 'grok-4.1-thinking'))
    rows.append(validate('jmr-oai', 'openai-compatible', 'gemini31_pro_jmr', 'gemini-3.1-pro'))
    rows.append(validate('jmr-oai', 'openai-compatible', 'gpt_oss_120b_free', 'openai/gpt-oss-120b:free'))

    write_models('jmr')
    rows.append(validate('jmr', 'anthropic-messages', 'grok41_expert', 'grok-4.1-expert'))
    rows.append(validate('jmr', 'anthropic-messages', 'grok41_thinking', 'grok-4.1-thinking'))
    rows.append(validate('jmr', 'anthropic-messages', 'gemini31_pro_jmr', 'gemini-3.1-pro'))
    rows.append(validate('jmr', 'anthropic-messages', 'gpt_oss_120b_free', 'openai/gpt-oss-120b:free'))

    MATRIX.write_text(
        '# LLM Live Validation Matrix\n\n'
        'This file records actual provider/model live probing and validation results.\n\n'
        '| Provider | Model Alias | Real Model ID | API Style / Adapter | Test Command | Stdout | File Output | File Input | Overall | Response Summary | Error Notes |\n'
        '|---|---|---|---|---|---:|---:|---:|---|---|---|\n' + '\n'.join(rows) + '\n',
        encoding='utf-8',
    )
    print(MATRIX.read_text(encoding='utf-8'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
