# LLM Live Validation Matrix

This file records actual provider/model live probing and validation results.

Validation notes:
- Shared environment used: `/Users/neoclaw/repos/ifa-data-platform/.venv`
- Token injected via env var only: `JMR_API_KEY`
- Confirmed valid API prefixes:
  - OpenAI-compatible: `/v1/chat/completions`
  - Anthropic-messages: `/v1/messages`
- Confirmed invalid / misleading paths:
  - `/chat/completions` -> returned site HTML, not API JSON
  - `/messages` -> returned site HTML, not API JSON
  - `/api/v1/...` -> invalid URL / 404

| Provider | Model Alias | Real Model ID | API Style / Adapter | Test Command | Stdout | File Output | File Input | Overall | Response Summary | Error Notes |
|---|---|---|---|---|---:|---:|---:|---|---|---|
| jmr-oai | grok41_expert | grok-4.1-expert | openai-compatible | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model grok41_expert --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，返回中文身份说明文本。 | - |
| jmr-oai | grok41_thinking | grok-4.1-thinking | openai-compatible | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model grok41_thinking --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，返回英文/中文混合友好身份说明。 | - |
| jmr-oai | gemini31_pro_jmr | gemini-3.1-pro | openai-compatible | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model gemini31_pro_jmr --prompt 'Who are you?'` | FAIL | FAIL | FAIL | FAIL | - | OpenAI-compatible path timed out in live probing; not accepted as working path. |
| jmr-oai | gpt_oss_120b_free | openai/gpt-oss-120b:free | openai-compatible | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model gpt_oss_120b_free --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，自述为 ChatGPT / OpenAI language model。 | - |
| jmr | grok41_expert | grok-4.1-expert | anthropic-messages | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model grok41_expert --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，Anthropic-style path 可用。 | - |
| jmr | grok41_thinking | grok-4.1-thinking | anthropic-messages | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model grok41_thinking --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，Anthropic-style path 可用。 | - |
| jmr | gemini31_pro_jmr | gemini-3.1-pro | anthropic-messages | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model gemini31_pro_jmr --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，含 `<think>` 段 + 正文，Anthropic-style path 可用。 | Response includes reasoning-style `<think>` block in returned text. |
| jmr | gpt_oss_120b_free | openai/gpt-oss-120b:free | anthropic-messages | `/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py --model gpt_oss_120b_free --prompt 'Who are you?'` | PASS | PASS | PASS | PASS | 回答正常，自述为 ChatGPT / OpenAI language model。 | - |

## Probe summary

### Confirmed working provider/model access paths
1. `jmr-oai` + OpenAI-compatible adapter works for:
   - `grok-4.1-expert`
   - `grok-4.1-thinking`
   - `openai/gpt-oss-120b:free`

2. `jmr` + Anthropic-messages adapter works for:
   - `grok-4.1-expert`
   - `grok-4.1-thinking`
   - `gemini-3.1-pro`
   - `openai/gpt-oss-120b:free`

### Important discovery
- `gemini-3.1-pro` should currently be treated as **working on the Anthropic-messages path** in this environment.
- It should **not** be treated as validated on the OpenAI-compatible path, because live probing there timed out.

### Recommended v1 default posture
- Keep both adapters implemented.
- Treat provider/model compatibility as config-driven and validated by matrix, not assumed.
- Do not collapse everything into one protocol assumption.
