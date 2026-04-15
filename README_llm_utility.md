# IFA Business Layer LLM Utility

## Purpose

This utility is a reusable **business-layer** LLM gateway for iFA workflows such as:
- fact extraction
- narrative generation
- report generation
- structured JSON generation

It is **not** a generic playground or standalone model lab.

## Environment rule

Use the existing shared environment only:
- `/Users/neoclaw/repos/ifa-data-platform/.venv`

Do not create a separate venv.

## Config files

- `config/llm/providers.yaml`
- `config/llm/models.yaml`

Current live probing confirmed that the provider base URL should remain:
- `https://jmrai.net/`

while adapters should call:
- OpenAI-compatible: `/v1/chat/completions`
- Anthropic-messages: `/v1/messages`

Example templates:
- `config/llm/providers.example.yaml`
- `config/llm/models.example.yaml`

## Secret injection

Set env var(s) locally, for example:

```bash
export JMR_API_KEY='...'
```

Do not commit real secrets.

## CLI usage

### Short prompt

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --prompt "Who are you?"
```

### File input

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --input-file tests/fixtures/llm/who_are_you.md
```

### Output to file

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --prompt "Who are you?" \
  --output-file /tmp/ifa_llm_out.txt
```

### JSON envelope output

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --prompt "Who are you?" \
  --output-format json
```

## Testing

### Unit/integration tests

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python -m pytest tests/unit/llm tests/integration/llm -q
```

### Live probing

See:
- `docs/LLM_LIVE_VALIDATION_MATRIX.md`

Important current finding:
- `gemini-3.1-pro` was validated successfully on the Anthropic-messages path in this environment
- it was not validated successfully on the OpenAI-compatible path

## Troubleshooting

### Missing key
- Ensure `JMR_API_KEY` is exported.

### Unknown model alias
- Check `config/llm/models.yaml`.

### Unsupported API path
- Validate provider `api_type` in `config/llm/providers.yaml`.

### Non-JSON / parse issues
- Use `--output-format text` unless JSON envelope is explicitly needed.
