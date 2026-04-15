# IFA Business Layer LLM Utility — Specification, Implementation Plan, and Test Plan

## 1. Document purpose

This document defines the **design, implementation plan, configuration model, testing strategy, and acceptance criteria** for a reusable LLM utility in the **business layer** of the iFA repository.

This is the **first deliverable** for review before final implementation is locked.

This document is intentionally written as an engineering spec rather than a casual sketch. Its goal is to make later implementation predictable, reviewable, and reusable across multiple iFA business workflows.

---

## 2. Background and design intent

### 2.1 Why this utility is needed

The iFA repository already has a clear direction:
- data/runtime substrate in repo scope
- report-oriented future workflows
- provider-agnostic architecture principles already used in ingestion/adaptor design

The business layer will need a reusable LLM access utility for tasks such as:
- fact extraction from prepared material
- narrative generation
- report generation
- structured JSON generation
- long prompt handling
- file-based prompt input
- future block/section-oriented workflow composition

Without a reusable utility, LLM access will likely fragment into:
- one-off scripts
- hardcoded provider/model settings
- repeated auth/config logic
- inconsistent response parsing
- poor testability

This utility is intended to avoid that fragmentation.

### 2.2 Product-level role

This utility is **not** the product itself.

It is a **reusable business-layer LLM utility / gateway** that sits above durable data/material preparation and below higher-level iFA workflows such as:
- fact extraction
- narrative generation
- report generation
- structured JSON generation
- section/block-oriented workflow assembly

It should be reusable by multiple iFA workflows, not tied to a single script or one report type.

Boundary clarification:
- this is **not** a generic chat playground
- this is **not** an open-ended experimentation sandbox
- this is **not** a standalone model lab tool
- this is a controlled business-layer utility intended to serve concrete iFA workflow needs

---

## 3. Scope of this task

## 3.1 In scope for this planning/spec step

This step produces a complete Markdown design/specification covering:
- what will be built
- why it is designed that way
- proposed file structure
- config structure
- secret handling
- adapter strategy
- CLI input/output contract
- dependency assumptions
- implementation order
- test plan
- acceptance criteria
- usage examples
- required README contents for the later implementation step

## 3.2 In scope for later implementation

The planned utility must support:
- short prompt input
- long prompt input from files
- JSON input files
- stdout output
- output-to-file
- text output
- JSON output
- provider/model external configuration
- future multi-provider reuse

## 3.3 Explicitly out of scope for the first implementation version

The first version should **not** center around direct binary attachment parsing such as:
- PDF parsing
- Word parsing
- image OCR
- direct image understanding

For v1, attachments should be treated as already-preprocessed:
- text
- markdown
- JSON

The first version should also **not** be framed as a generic model playground. It should not add product scope such as:
- arbitrary free-form chat lab behavior
- open-ended provider experimentation without workflow purpose
- standalone benchmark/lab tooling detached from iFA business use cases

## 3.4 Explicitly out of scope for this task

This task does **not** require final production code yet.

The immediate deliverable is the specification document itself.

---

## 4. Repository and environment constraints

Repository:
- `/Users/neoclaw/repos/ifa-business-layer`

These are **hard execution constraints**, not suggestions:
- this work belongs to the **business layer** repo, not the data-platform repo
- implementation must align to the actual repo boundary and package layout of `ifa-business-layer`
- it must use the **existing shared environment** already mandated by this repo: `/Users/neoclaw/repos/ifa-data-platform/.venv`
- **do not create any new virtualenv / conda env / poetry env**
- dependency completion is already pre-approved when needed for clean implementation
- routine package installation and dependency completion should be handled directly without unnecessary interruption
- do not commit real secrets
- do not hardwire the design to a single provider/model

Execution rule:
- treat shared-environment reuse as non-negotiable unless a real blocker proves the repo cannot operate that way
- do not pause for approval on ordinary dependency additions, package installs, or routine environment completion work
- only escalate if there is a real blocker, conflict, or risk that materially changes implementation direction

### 4.1 Existing repository signals that influence this design

From current `ifa-business-layer` repo/docs state:
- the repo already explicitly mandates reuse of the unified shared venv at `/Users/neoclaw/repos/ifa-data-platform/.venv`
- the repo currently uses the root package layout `ifa_business_layer/` (not `src/ifa_data_platform`)
- the repo already has `docs/`, `scripts/`, and `tests/`
- the repo is intentionally scoped to business-layer objects and maintenance surfaces, not collection/runtime development

Therefore, the LLM utility should follow the same engineering style:
- package-based implementation under `ifa_business_layer/`
- configuration externalization
- testable boundaries
- repo-native documentation and README
- strict respect for business-layer scope

---

## 5. Architectural position in iFA

## 5.1 Layer placement

Proposed placement:

`prepared evidence/materials -> business-layer llm utility -> higher-level business workflows`

This utility should not own:
- raw source ingestion
- durable evidence acquisition
- rendering system
- delivery system
- OpenClaw orchestration

It should own:
- model/provider config resolution
- request construction
- file/prompt ingestion normalization
- output parsing / shaping
- reusable invocation interface
- adapter selection across API styles

## 5.2 Design principle

The utility should be treated as a **business-layer infrastructure component**, not as a one-off CLI.

That means:
- code should be importable from workflows
- CLI should be a thin wrapper over reusable library code
- providers/models/secrets should be externalized
- test strategy should validate both library and CLI behavior

---

## 6. Design goals

The utility must be:

1. **Reusable**
   - usable by future report/fact/narrative workflows

2. **Configurable**
   - no hardcoded provider/model/token/base URL in code

3. **Provider-agnostic**
   - support multiple provider/API styles through adapters

4. **Operationally testable**
   - each configured model should be smoke-testable individually

5. **File-friendly**
   - support long prompt workflows through file input

6. **Business-layer aligned**
   - behave as a stable utility for downstream workflows, not a toy demo

7. **Maintainable**
   - clear file structure, clear contracts, minimal hidden magic

---

## 7. Non-goals

The first implementation should **not** attempt to solve everything.

Non-goals for v1:
- PDF/Word/image native parsing
- streaming UI integration
- agent orchestration
- multi-turn conversation memory store
- automatic retrieval augmentation
- rendering HTML/PDF reports directly
- workflow-specific business logic baked into the utility

This utility is a gateway/client layer, not the full workflow engine.

---

## 8. Functional requirements

## 8.1 Input modes

The utility must support:

### A. Short prompt input
- `--prompt "..."`

### B. Long input from file
- `--input-file path/to/file`

### C. Optional stdin support
- if no `--prompt` and no `--input-file`, optionally allow stdin
- this is recommended because it improves shell composability

## 8.2 Supported input file types (v1 minimum)

- `.txt`
- `.md`
- `.json`

### Input interpretation rules

- `.txt` / `.md` -> read as UTF-8 text prompt body
- `.json` -> read as structured input payload; utility may either:
  - serialize to prompt text according to selected mode, or
  - pass as structured payload for JSON-oriented request mode

The exact mode should be explicit in the CLI and library contract.

## 8.3 Output modes

### Default
- stdout

### Optional file output
- `--output-file path/to/output.txt`

## 8.4 Output formats (v1 minimum)

- `text`
- `json`

### Rules
- `--output-format text` -> emit model output as text
- `--output-format json` -> emit normalized JSON object with at least:
  - request metadata
  - provider/model identifiers
  - output text and/or parsed JSON body
  - error fields when relevant

## 8.5 Configuration requirements

The utility must resolve provider/model details from external config, including:
- provider name
- provider base URL
- API protocol type
- API key environment variable name
- model alias
- real model id
- display name
- context window
- optional capability tags

## 8.6 Secrets requirements

- real secrets must **not** be committed
- config files may specify **which environment variable name** to read
- a single token may serve multiple models under the same provider
- design must support that cleanly

## 8.7 Test requirements

For each configured model/endpoint under test, the utility must be able to:
- load config
- load auth from env
- call endpoint
- parse response
- output to stdout
- output to file

Minimal round trip prompt:
- `Who are you?`

Plus one file-based test.

---

## 9. Proposed implementation shape

## 9.1 High-level architecture

Proposed internal architecture:

1. **CLI layer**
   - argument parsing
   - input file/stdin loading
   - output handling
   - delegates to service layer

2. **Service layer**
   - request normalization
   - config resolution
   - provider/model resolution
   - adapter dispatch
   - normalized result shaping

3. **Provider adapter layer**
   - different protocol styles behind one common interface

4. **Config layer**
   - provider registry
   - model registry
   - environment variable mapping

5. **Test layer**
   - config loading tests
   - input/output tests
   - adapter parsing tests
   - optional live smoke tests

## 9.2 Why this structure is preferred

This structure avoids three common failure modes:
- CLI script and core logic becoming tangled
- provider-specific details leaking everywhere
- testing becoming difficult because network calls and file handling are mixed together

---

## 10. Proposed file structure

Recommended file structure for later implementation:

```text
ifa_business_layer/llm/
  __init__.py
  types.py
  config.py
  loader.py
  service.py
  adapters/
    __init__.py
    base.py
    openai_compatible.py
    anthropic_messages.py
  io/
    __init__.py
    input_loader.py
    output_writer.py

scripts/
  ifa_llm_cli.py

config/
  llm/
    providers.example.yaml
    models.example.yaml

tests/unit/llm/
  test_config_loader.py
  test_input_loader.py
  test_output_writer.py
  test_service.py
  test_openai_compatible_adapter.py
  test_anthropic_messages_adapter.py

tests/integration/llm/
  test_llm_cli_smoke.py
  test_llm_cli_file_input.py

docs/
  IFA_BUSINESS_LAYER_LLM_UTILITY_SPEC.md

README_llm_utility.md
```

### Notes

- `scripts/ifa_llm_cli.py` is the thin executable entrypoint
- reusable logic lives under `ifa_business_layer/llm/`
- config templates live under `config/llm/`
- actual secrets remain in env, not in YAML
- dedicated README should be added during implementation step

---

## 11. Configuration architecture

## 11.1 Core principle

Configuration should be split into:

1. **provider-level config**
2. **model-level config**
3. **runtime invocation config** (CLI flags / optional defaults)
4. **secret injection via environment variables**

This keeps provider access stable while allowing many models per provider.

## 11.2 Provider-level configuration

Provider-level config should define connection/auth/protocol shape.

### Proposed provider fields

```yaml
providers:
  jmr-oai:
    base_url: https://example.invalid/
    api_type: openai-completions
    api_key_env: JMR_API_KEY
    timeout_seconds: 60
    headers: {}

  jmr-anthropic:
    base_url: https://example.invalid/
    api_type: anthropic-messages
    api_key_env: JMR_API_KEY
    timeout_seconds: 60
    headers: {}
```

### Required provider fields
- `base_url`
- `api_type`
- `api_key_env`

### Recommended provider fields
- `timeout_seconds`
- `headers`
- `default_max_tokens`
- `default_temperature`

## 11.3 Model-level configuration

Model-level config should define logical model aliases and capabilities.

### Proposed model fields

```yaml
models:
  grok41_expert:
    provider: jmr-oai
    model_id: grok-4.1-expert
    display_name: Grok 4.1 Expert
    context_window: 200000
    capabilities: [text, json, long_context]

  grok41_thinking:
    provider: jmr-oai
    model_id: grok-4.1-thinking
    display_name: Grok 4.1 Thinking
    context_window: 200000
    capabilities: [text, json, reasoning, long_context]

  gemini31_pro_jmr:
    provider: jmr-oai
    model_id: gemini-3.1-pro
    display_name: Gemini 3.1 Pro
    context_window: 200000
    capabilities: [text, json, long_context]
```

### Required model fields
- `provider`
- `model_id`

### Recommended model fields
- `display_name`
- `context_window`
- `capabilities`
- `notes`

## 11.4 Why separate providers from models

Because:
- one provider may host many models
- one token may access many models
- base URL / auth style belongs to provider level
- model id / capabilities belong to model level

This is cleaner and avoids duplicated config.

---

## 12. Known provider/model context and Grok-related compatibility

The design must support the already known structure similar to OpenCore / OpenClaw-style provider-model configuration:
- a provider entry with shared token/base URL/protocol
- multiple models attached under that provider

Known example pattern to support structurally:
- `jmr` / `jmr-oai`
- `grok-4.1-expert`
- `grok-4.1-thinking`
- `gemini-3.1-pro`
- potentially more later

Important design requirement:
- **do not hardwire the utility to a single Grok model**
- **do not assume only Grok exists**
- **do not assume only one provider exists**

Relationship to OpenCore / OpenClaw configuration:
- the design should reference already-known OpenCore / OpenClaw-style provider/model structure as an input reality
- however, the iFA utility should **not** be tightly coupled to OpenCore’s internal raw config format
- iFA should define and own its **own lightweight, maintainable config schema** for business-layer use
- the utility should be able to **map from known provider/model structures used elsewhere** into that iFA-owned schema

The design should therefore make future provider additions straightforward without inheriting another system’s internal config shape as a hard dependency.

---

## 13. Secret handling approach

## 13.1 Rules

- no real token is committed to repo
- provider config stores **env var name**, not token value
- actual token is injected by environment at runtime
- multiple models can reuse same provider token

## 13.2 Example

```yaml
providers:
  jmr-oai:
    base_url: https://jmrai.example/
    api_type: openai-completions
    api_key_env: JMR_API_KEY
```

Then runtime resolves:
- `os.environ["JMR_API_KEY"]`

## 13.3 .env / secrets strategy

Recommended approach for implementation:
- keep `.env.example` with placeholders only
- use actual `.env` or environment injection locally
- document export examples in README
- do not place actual token in YAML, code, tests, or docs

## 13.4 Acceptance rule

If required env var is missing, the utility should fail clearly with a message like:
- provider name
- required env var name
- model alias being requested

---

## 14. Adapter strategy for multiple API styles

## 14.1 Why adapters are required

Different providers may expose different request/response styles.

At minimum we should expect at least two families:
- OpenAI-compatible/completions/chat-style API
- Anthropic messages-style API

If those differences are not isolated, business workflows will become provider-coupled.

## 14.2 Proposed adapter interface

A base adapter should expose something like:

```python
class BaseLLMAdapter(Protocol):
    def invoke(self, request: LLMRequest, provider: ProviderConfig, model: ModelConfig) -> LLMResponse:
        ...
```

## 14.3 Proposed normalized request object

```python
@dataclass
class LLMRequest:
    model_alias: str
    input_text: str | None
    input_json: dict | list | None
    output_format: Literal["text", "json"]
    temperature: float | None = None
    max_tokens: int | None = None
```

## 14.4 Proposed normalized response object

```python
@dataclass
class LLMResponse:
    provider_name: str
    model_alias: str
    model_id: str
    raw_text: str | None
    parsed_json: dict | list | None
    finish_reason: str | None
    usage: dict | None
    raw_response: dict | None
```

## 14.5 Initial adapter set

For first implementation, plan for:
- `OpenAICompatibleAdapter`
- `AnthropicMessagesAdapter`

This is sufficient for the currently known direction and leaves room for future adapters.

---

## 15. Input contract details

## 15.1 CLI arguments (proposed)

```text
--model <alias>              required
--prompt <text>              optional
--input-file <path>          optional
--output-format <text|json>  default=text
--output-file <path>         optional
--stdin                      optional explicit stdin mode
--temperature <float>        optional
--max-tokens <int>           optional
--config-dir <path>          optional override, defaults to config/llm
--system-file <path>         optional future-safe extension
```

## 15.2 Input resolution rules

Recommended precedence:
1. `--prompt`
2. `--input-file`
3. `--stdin`

The utility should reject ambiguous combinations unless explicitly supported.

Recommended rule:
- allow only one primary input source for v1

## 15.3 File type handling

### `.txt` / `.md`
- read as UTF-8 text
- pass as text prompt content

### `.json`
- parse as JSON
- then either:
  - use as structured input in request object
  - or serialize in deterministic JSON text form if provider only accepts text-style prompting

This behavior should be documented and deterministic.

---

## 16. Output contract details

## 16.1 Text output

For `--output-format text`:
- print model output text only to stdout by default
- if `--output-file` provided, write that same text to file

## 16.2 JSON output

For `--output-format json`, emit a normalized JSON envelope like:

```json
{
  "provider": "jmr-oai",
  "model_alias": "grok41_expert",
  "model_id": "grok-4.1-expert",
  "finish_reason": "stop",
  "text": "Hello ...",
  "parsed_json": null,
  "usage": {},
  "error": null
}
```

## 16.3 Optional parsed JSON mode

If the response is intended to be JSON, the utility may support one of two approaches:
- `--output-format json` only wraps the response envelope
- optional future flag `--parse-json-response` attempts JSON parsing from model output

For v1, this should be explicit and not magical.

---

## 17. Error handling design

The utility should fail clearly and predictably.

### Error classes to support
1. config load error
2. missing provider error
3. missing model alias error
4. missing env var / secret error
5. file read error
6. request/network error
7. response parsing error
8. output write error

### Principles
- error messages should be short and actionable
- include model alias/provider name when relevant
- avoid opaque stack traces for routine CLI usage
- preserve enough detail for debugging in JSON mode or logs

---

## 18. Dependency assumptions

## 18.1 Existing dependencies already present
Current `pyproject.toml` already includes:
- `requests`
- `pyyaml`
- `pydantic`
- `pydantic-settings`

These are enough for a basic v1.

## 18.2 Recommended additions

Recommended to add for implementation quality:
- `httpx>=0.27.0`

### Why `httpx` is recommended
- cleaner timeout handling
- better modern HTTP ergonomics
- easier future async extension if needed
- strong sync client support for v1

If the repo prefers to avoid adding `httpx` right now, v1 can still be implemented with `requests`.

### Recommendation
Preferred implementation choice:
- use `httpx` for the utility layer
- keep dependency addition scoped and justified

## 18.3 No new virtual environment
Implementation must use existing repo `.venv` / shared environment approach.

---

## 19. Testing plan

The testing goal is intentionally simple and explicit:

For each configured model under test, verify that the utility can:
- load config
- load auth
- connect successfully
- receive a valid response
- print to stdout
- optionally write to output file

## 19.1 Test categories

### A. Unit tests
No live network required.

Covers:
- config loading
- model/provider resolution
- input file parsing
- output writing
- adapter request building
- adapter response normalization
- error handling

### B. Integration tests (mocked / local)
Optional staged tests with controlled fixtures.

Covers:
- CLI invocation flow
- file input to output path
- JSON mode end-to-end without real external endpoint

### C. Live smoke tests
Real endpoint/auth dependent.

Covers:
- auth works
- endpoint works
- parsing works
- stdout works
- output-file works

## 19.2 Minimal smoke test design

For each configured model alias under test:

Command shape:

```bash
python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --prompt "Who are you?"
```

Expected result:
- exits 0
- returns non-empty text
- provider/model metadata resolvable in logs or JSON mode

## 19.3 File input smoke test

Prepare a text file, for example:

`tests/fixtures/llm/who_are_you.md`

Content:

```md
Please answer briefly: Who are you?
```

Command shape:

```bash
python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --input-file tests/fixtures/llm/who_are_you.md \
  --output-file /tmp/ifa_llm_smoke.txt
```

Expected result:
- exits 0
- output file exists
- file is non-empty

## 19.4 JSON input smoke test

Prepare fixture:

`tests/fixtures/llm/simple_payload.json`

Example content:

```json
{
  "task": "identity_check",
  "question": "Who are you?",
  "style": "brief"
}
```

Command shape:

```bash
python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --input-file tests/fixtures/llm/simple_payload.json \
  --output-format json
```

Expected result:
- exits 0
- stdout valid JSON
- envelope contains provider/model/text fields

## 19.5 Per-model validation matrix

The implementation step should include a simple validation matrix like:

| Model Alias | Provider | Auth OK | Endpoint OK | Stdout OK | Output File OK | Notes |
|---|---|---:|---:|---:|---:|---|
| grok41_expert | jmr-oai | TBD | TBD | TBD | TBD | |
| grok41_thinking | jmr-oai | TBD | TBD | TBD | TBD | |
| gemini31_pro_jmr | jmr-oai | TBD | TBD | TBD | TBD | |

This allows one-by-one endpoint confirmation once real tokens are supplied.

## 19.6 Recommended test file layout

```text
tests/fixtures/llm/
  who_are_you.md
  who_are_you.txt
  simple_payload.json
```

## 19.7 Post-token live validation procedure (mandatory after real secrets/config are supplied)

Once real token(s) and any additional provider configuration are supplied, the implementation must not stop at static code completion. It must perform **live endpoint-by-endpoint validation**.

Required live-validation procedure:

1. enumerate every configured active model/endpoint under test
2. validate them **one by one**
3. run at minimum a simple round-trip prompt such as:
   - `Who are you?`
4. verify both:
   - stdout output
   - output-to-file behavior
5. run at least one file-input validation case per active provider path
6. record results in a validation matrix / report

Minimum required validation matrix columns:
- provider
- model alias
- real model ID
- test command
- pass / fail
- short response summary
- error notes (if any)

Recommended matrix shape:

| Provider | Model Alias | Real Model ID | Test Command | Stdout | File Output | File Input | Pass/Fail | Response Summary | Error Notes |
|---|---|---|---|---:|---:|---:|---|---|---|

Minimum live validation set per active model:
1. short prompt smoke test
2. stdout validation
3. `--output-file` validation
4. at least one `--input-file` validation

Required deliverable after secrets are supplied:
- a live validation report / matrix stored in the repo for review

---

## 20. Proposed implementation sequence

Implementation should proceed in this order:

### Phase 1 — config and types
- create provider/model config schemas
- create loader for YAML config
- validate env var resolution

### Phase 2 — adapter contracts
- implement base adapter interface
- implement openai-compatible adapter
- implement anthropic-messages adapter

### Phase 3 — input/output utilities
- implement text/json file loading
- implement stdout and output-file writers

### Phase 4 — service layer
- connect config + input + adapter + normalized response

### Phase 5 — CLI
- add script entrypoint
- parse args
- invoke service

### Phase 6 — tests
- unit tests for config/io/service/adapters
- CLI integration tests
- fixture files

### Phase 7 — live validation
- run per-model smoke tests once secrets are provided

### Phase 8 — README
- complete usage/config/testing/troubleshooting docs

---

## 20.1 Execution style requirement

Implementation should follow a low-friction execution style aligned to actual iFA engineering work.

Required behavior:
- make reasonable engineering decisions proactively
- handle routine dependency/package/minor implementation choices directly
- do not repeatedly interrupt execution for routine clarification
- do not fragment the work into many small confirmation loops
- escalate only real blockers, conflicts, or decisions that materially change scope or architecture

The implementation goal is to complete the work cleanly and reviewably, not to maximize intermediate back-and-forth.

## 21. Acceptance criteria

The implementation following this spec should be accepted only if all of the following are true:

### Repo alignment
- implementation lives in the `ifa-business-layer` repo, not in `ifa-data-platform`
- package layout matches this repo’s actual structure (`ifa_business_layer/`)
- execution uses the shared unified venv already mandated by this repo

### Functional
- can invoke by model alias
- can read `--prompt`
- can read `--input-file`
- supports `.txt`, `.md`, `.json`
- outputs to stdout by default
- supports `--output-file`
- supports `text` and `json` output modes

### Configuration
- no hardcoded token/base URL/model id in code
- provider config and model config are externalized
- one provider token can serve multiple models

### Engineering quality
- reusable code lives in package modules, not only in a script
- provider-specific logic isolated via adapters
- CLI is thin wrapper over reusable service
- code follows existing repo structure and style

### Testing
- unit tests exist for config/io/service/adapters
- smoke test plan exists for each configured model
- file-input test exists
- stdout and output-file behavior validated

### Security
- no real secret committed
- missing env vars fail clearly

### Documentation
- README added in implementation step with config/run/test/troubleshooting guidance

---

## 22. Usage examples (planned)

## 22.1 Short prompt example

```bash
python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --prompt "Summarize this in 3 bullets"
```

## 22.2 Long markdown input example

```bash
python scripts/ifa_llm_cli.py \
  --model grok41_thinking \
  --input-file materials/report_draft.md \
  --output-file outputs/report_draft_response.txt
```

## 22.3 JSON input example

```bash
python scripts/ifa_llm_cli.py \
  --model gemini31_pro_jmr \
  --input-file materials/facts.json \
  --output-format json
```

## 22.4 Stdin example

```bash
cat prompt.txt | python scripts/ifa_llm_cli.py \
  --model grok41_expert \
  --stdin
```

---

## 22.1 Expected later implementation deliverables checklist

When implementation begins after spec approval, the expected outputs should include at minimum:

- [ ] reusable utility code under repo package structure
- [ ] CLI entrypoint/script for invoking the utility
- [ ] config schema implementation for providers/models
- [ ] example config files/templates
- [ ] explicit secret injection pattern (env-var based)
- [ ] unit tests
- [ ] smoke/integration test script(s)
- [ ] sample input fixtures (`.txt`, `.md`, `.json`)
- [ ] README for configuration, usage, testing, troubleshooting
- [ ] live validation report / test matrix after real secrets are supplied

These deliverables should be treated as concrete expected outputs, not loose suggestions.

## 23. README requirement for implementation step

Once the utility is implemented, the final code must include a dedicated README that explains:

1. what the utility is for
2. where config files live
3. how provider config works
4. how model config works
5. how to inject secrets via env vars
6. how to run it with `--prompt`
7. how to run it with `--input-file`
8. how to use stdout vs `--output-file`
9. how to run smoke tests
10. expected outputs
11. common errors and troubleshooting notes

Recommended filename:
- `README_llm_utility.md`

Optionally later merged into main README once stable.

---

## 24. Recommended config examples for implementation

## 24.1 `config/llm/providers.example.yaml`

```yaml
providers:
  jmr-oai:
    base_url: https://jmrai.net/
    api_type: openai-completions
    api_key_env: JMR_API_KEY
    timeout_seconds: 60

  jmr-anthropic:
    base_url: https://jmrai.net/
    api_type: anthropic-messages
    api_key_env: JMR_API_KEY
    timeout_seconds: 60
```

## 24.2 `config/llm/models.example.yaml`

```yaml
models:
  grok41_expert:
    provider: jmr-oai
    model_id: grok-4.1-expert
    display_name: Grok 4.1 Expert
    context_window: 200000
    capabilities: [text, json, long_context]

  grok41_thinking:
    provider: jmr-oai
    model_id: grok-4.1-thinking
    display_name: Grok 4.1 Thinking
    context_window: 200000
    capabilities: [text, json, reasoning, long_context]

  gemini31_pro_jmr:
    provider: jmr-oai
    model_id: gemini-3.1-pro
    display_name: Gemini 3.1 Pro
    context_window: 200000
    capabilities: [text, json, long_context]
```

These are examples only; real tokens remain external.

---

## 25. Open questions to resolve at implementation review

These are **engineering choices**, not blockers for the current design document:

1. `requests` vs `httpx`
   - recommendation: `httpx`

2. whether JSON response parsing should be explicit via flag
   - recommendation: yes, explicit

3. whether stdin should be implicit fallback or explicit `--stdin`
   - recommendation: explicit is safer for v1

4. whether provider config should allow custom headers
   - recommendation: yes, optional support from day one

5. whether to support system prompt separately in v1
   - recommendation: optional but useful; support `--system-file` if low cost

---

## 26. Final recommendation

The reusable LLM utility should be implemented as a **config-driven, adapter-based, package-first business-layer component** with a thin CLI.

That design best matches iFA’s current direction because it:
- preserves provider/model flexibility
- supports multiple future workflows
- avoids hardcoded one-off scripts
- fits existing repo architecture principles
- is testable and maintainable

This document is intended to be the review baseline before implementation begins.
