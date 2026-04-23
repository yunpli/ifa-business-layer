# A-share Support Agent Buildout Package（business-layer / 2026-04-22）

## 1. Purpose

This document is the **implementation-ready business package** for the three A-share support agents:

- `macro`
- `commodities`
- `ai_tech`

It exists to close the gap between:

- already-frozen business contracts, and
- actual engineering buildout work.

This package is **business-layer owned**. It defines business semantics, stable IDs, output obligations, and acceptance rules. It does **not** define persistence internals or table-level data-platform implementation.

---

## 2. Canonical ownership boundary

### business-layer owns
- support-agent role semantics
- domain / slot / section taxonomy
- required outputs per agent
- relation semantics to main agent (`support|adjust|counter`)
- object-key conventions
- business-side acceptance criteria

### data-platform owns
- input readers
- FSJ persistence schema / store / upsert policy
- slot replay hydration
- observed-record linking
- report artifact persistence

### report-layer owns
- rendering / assembly / ordering / truncation
- UI/report presentation rules
- customer-facing wording polish

If a requirement is about **what the support agent means or must produce**, it belongs here.
If a requirement is about **how rows are read/written**, it does not.

---

## 3. Upstream contracts this package freezes into execution form

This package is derived from and must stay aligned with:

- `docs/A_SHARE_2_0_ONE_MAIN_THREE_SUPPORT_CONTRACT.md`
- `docs/A_SHARE_SUPPORT_AGENTS_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_MAIN_AGENT_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_EARLY_MID_LATE_DATA_CONSUMPTION_CONTRACT_V1.md`
- `docs/A_SHARE_FSJ_AND_EVIDENCE_MAPPING_V1.md`
- `docs/A_SHARE_FSJ_PERSISTENCE_CONTRACT_PHASE1_2026-04-22.md`

This document adds **execution shape**, not new product scope.

---

## 4. Phase-1 build scope

### in scope now
- `early` support bundle for `macro`
- `late` support bundle for `macro`
- `early` support bundle for `commodities`
- `late` support bundle for `commodities`
- `early` support bundle for `ai_tech`
- `late` support bundle for `ai_tech`
- stable relation handoff into main-agent consumption

### explicitly out of scope now
- standalone `mid` support-agent auto-producer
- multi-section support reports per domain
- customer-personalized support variants
- autonomous cross-domain conflict resolution
- support-agent scoring / backtesting / quality analytics

Phase 1 support agents are **support-note producers**, not independent full-report systems.

---

## 5. Stable identity rules

## 5.1 agent domains

Only these domain IDs are valid:

- `macro`
- `commodities`
- `ai_tech`

Do not introduce aliases like:

- `commodity`
- `metal`
- `metals`
- `ai-tech`
- `tech_ai`

Canonical business IDs stay fixed to avoid downstream drift.

## 5.2 slots

Only these support slots are valid in Phase 1:

- `early`
- `late`

## 5.3 section keys

Each support bundle uses exactly one primary section key:

- `support_macro`
- `support_commodities`
- `support_ai_tech`

These are the section keys consumed by the main agent.

## 5.4 bundle identity

A support bundle must be uniquely identifiable by:

- `market = a_share`
- `business_date`
- `slot`
- `agent_domain`
- `section_key`

Recommended bundle id format:

- `a_share:{business_date}:{slot}:{agent_domain}:{section_key}`

Example:

- `a_share:2026-04-22:early:macro:support_macro`

---

## 6. Required output shape

Every support producer must emit one business bundle containing:

- bundle metadata
- `facts[]`
- `signals[]`
- `judgments[]`
- `support_relations[]`
- `summary`

Minimum rule:

- at least `1` judgment
- at least `1` signal
- at least `1-3` facts

A support bundle with only narrative prose is invalid.

---

## 7. Support relation model

Each support bundle must declare how it should affect the main agent.

Allowed relation values:

- `support`
- `adjust`
- `counter`

### meaning
- `support`: strengthens current main thesis
- `adjust`: asks main thesis to change weight / ranking / wording / confidence
- `counter`: provides explicit disconfirming evidence or risk

### hard rule
A support bundle must name **one primary relation**.

Optional secondary relation is allowed only if clearly weaker.

Example:

```yaml
primary_relation: adjust
secondary_relations:
  - support
```

Do not emit all three relations at once.

---

## 8. Domain-specific business obligations

## 8.1 Macro support

### early must answer
1. Is today’s macro background risk-on, risk-off, or neutral for A-share?
2. What macro change must be surfaced before the open?
3. What macro misread risk could distort the main thesis today?

### late must answer
1. Did macro actually matter today, or was it just background noise?
2. Did macro act as driver, amplifier, or weak backdrop?
3. What macro variable must roll into next-day monitoring?

### recommended object keys
- `macro:liquidity`
- `macro:rates`
- `macro:fx`
- `macro:policy_expectation`
- `macro:risk_appetite`

### invalid outputs
- rewriting the whole market recap
- listing all overseas headlines without A-share relevance
- giving a strong directional macro judgment with no evidence chain

## 8.2 Commodities support

### early must answer
1. Which commodity/resource chains deserve attention before open?
2. Which A-share directions could they support or pressure?
3. Which mapping is most worth validating intraday?

### late must answer
1. Which commodity-to-equity mapping actually held today?
2. Which apparent linkage was only superficial correlation?
3. Which chain remains actionable for the next session?

### recommended object keys
- `commodity:oil_chain`
- `commodity:industrial_metals`
- `commodity:gold`
- `commodity:black_chain`
- `commodity:chemicals`
- `commodity:agri_chain`

### invalid outputs
- standalone commodity-market daily report
- broad cycle commentary without A-share mapping
- forcing stock conclusions from weak commodity moves

## 8.3 AI-tech support

### early must answer
1. Does AI-tech have pre-open mainline candidacy today?
2. Which subthemes deserve priority monitoring?
3. Which names/themes are stale leftovers rather than fresh signal?

### late must answer
1. Was AI-tech today a mainline, branch line, or noise?
2. Did the diffusion chain really form?
3. Should AI-tech keep high priority tomorrow?

### recommended object keys
- `ai_tech:mainline_status`
- `ai_tech:compute_chain`
- `ai_tech:model_chain`
- `ai_tech:application_chain`
- `ai_tech:leader_diffusion`
- `ai_tech:theme_exhaustion`

### invalid outputs
- rewriting the whole A-share tech complex
- inferring sector-wide strength from one hot stock
- collapsing all technology themes into one undifferentiated thesis

---

## 9. Required judgment types by slot

### early
Support bundles should usually end in:

- `judgment_type = support` or `watch_item`
- `judgment_action = support | adjust | observe | prepare`

### late
Support bundles should usually end in:

- `judgment_type = support | risk | next_step`
- `judgment_action = confirm | downgrade | observe | prepare`

### hard rule
Support agents do **not** own the final market-wide thesis.

They may conclude inside their own domain, but their output must remain support-facing.

---

## 10. Degrade discipline

When evidence is thin, the support producer must degrade.

### allowed degrade moves
- lower confidence
- switch from `support` to `adjust` or `counter`
- switch final judgment from strong support to watch/risk
- explicitly name evidence gap in `invalidation / caution`

### forbidden behavior
- same tone after evidence loss
- reference-only inputs pretending to be same-day confirmed evidence
- hiding missing support data behind broad prose

---

## 11. Producer checklist per bundle

Every support bundle must satisfy all of the following:

1. valid `agent_domain`
2. valid `slot`
3. valid `section_key`
4. exactly one primary relation
5. at least one fact
6. at least one signal linked to fact(s)
7. at least one judgment linked to signal(s)
8. summary sentence exists
9. invalidation/caution exists, even if brief
10. no cross-domain drift outside the agent’s remit

---

## 12. Engineering handoff: what should be built next

For each of the three domains, engineering should implement:

1. one producer for `early`
2. one producer for `late`
3. domain-specific assembler logic using this package’s section key and object-key rules
4. output compatible with FSJ bundle persistence contract
5. relation payload that main-agent assembly can consume directly

Recommended producer naming pattern:

- `EarlyMacroSupportProducer`
- `LateMacroSupportProducer`
- `EarlyCommoditiesSupportProducer`
- `LateCommoditiesSupportProducer`
- `EarlyAITechSupportProducer`
- `LateAITechSupportProducer`

This naming is recommended, not mandatory. Semantics are mandatory.

---

## 13. Acceptance standard for this package

This package is considered correctly implemented only when all six support bundles can be produced with:

- correct domain identity
- correct section key
- valid FSJ chain
- explicit primary relation
- domain-bounded judgment
- degrade-safe behavior

If a build produces prose without stable IDs and relation semantics, it is not accepted.
