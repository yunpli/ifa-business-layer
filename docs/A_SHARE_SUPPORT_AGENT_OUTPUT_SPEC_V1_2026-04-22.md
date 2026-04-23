# A-share Support Agent Output Spec v1（business-layer / 2026-04-22）

## 1. Purpose

This file defines the **minimum business payload** a support-agent producer must assemble before persistence or report rendering.

It is intentionally narrow:
- no storage details
- no table names
- no adapter logic
- only the business object shape

---

## 2. Bundle payload

```yaml
bundle_id: string
market: a_share
business_date: YYYY-MM-DD
slot: early|late
agent_domain: macro|commodities|ai_tech
section_key: support_macro|support_commodities|support_ai_tech
section_type: support
producer: business-layer
producer_version: string
assembly_mode: rule_assembled|hybrid
summary: string
primary_relation: support|adjust|counter
secondary_relations: [support|adjust|counter]
```

Constraints:
- `section_type` is always `support`
- `primary_relation` is required
- `secondary_relations` may be empty
- `summary` must be one sentence, not a full paragraph

---

## 3. Fact payload

```yaml
fact_id: string
object_key: string
fsj_kind: fact
fact_type: market|event|flow|breadth|theme|news|announcement|macro|commodity
statement: string
entity_refs: [string]
metric_refs: [string]
source_layer: business_seed|lowfreq|midfreq|highfreq|archive_v2|slot_replay
freshness_label: fresh|same_slot|t_minus_1|stale|unknown
confidence: high|medium|low
```

Constraints:
- fact statement must be observational, not interpretive
- fact must stay inside the agent’s domain
- at least one fact per bundle is required

---

## 4. Signal payload

```yaml
signal_id: string
object_key: string
fsj_kind: signal
signal_type: strengthening|weakening|rotation|divergence|confirmation|risk
statement: string
based_on_fact_ids: [string]
signal_strength: high|medium|low
horizon: intraday|same_day|t_plus_1
confidence: high|medium|low
```

Constraints:
- `based_on_fact_ids` cannot be empty
- signal is interpretation, not final advice
- at least one signal per bundle is required

---

## 5. Judgment payload

```yaml
judgment_id: string
object_key: string
fsj_kind: judgment
judgment_type: support|risk|watch_item|next_step
statement: string
judgment_action: support|adjust|confirm|downgrade|observe|prepare
based_on_signal_ids: [string]
direction: bullish|bearish|mixed|neutral|conditional
priority: p0|p1|p2
invalidators: [string]
confidence: high|medium|low
```

Constraints:
- `based_on_signal_ids` cannot be empty
- `invalidators` must exist; empty list is allowed but omission is not
- at least one judgment per bundle is required
- judgment must remain domain-scoped rather than market-totalizing

---

## 6. Domain-to-section mapping

| agent_domain | section_key | allowed fact focus |
|---|---|---|
| `macro` | `support_macro` | macro / policy / rates / FX / liquidity |
| `commodities` | `support_commodities` | commodity / resource / chain mapping |
| `ai_tech` | `support_ai_tech` | AI-tech themes / leader-diffusion / subtheme state |

No other `section_key` is valid for phase-1 support producers.

---

## 7. Relation usage rules

## `support`
Use when the support domain clearly reinforces the main thesis.

## `adjust`
Use when the support domain does not overturn the main thesis but should change:
- confidence
- priority
- wording
- sequencing

## `counter`
Use when the support domain provides explicit contradiction or risk to the main thesis.

Hard rule:
- relation is about impact on the main agent, not internal tone.

---

## 8. Minimal valid examples

### macro / early
```yaml
bundle:
  agent_domain: macro
  slot: early
  section_key: support_macro
  primary_relation: adjust
facts:
  - fact_id: fact:macro:early:liquidity
signals:
  - signal_id: signal:macro:early:risk_appetite
judgments:
  - judgment_id: judgment:macro:early:open_bias
```

### commodities / late
```yaml
bundle:
  agent_domain: commodities
  slot: late
  section_key: support_commodities
  primary_relation: support
facts:
  - fact_id: fact:commodities:late:industrial_metals
signals:
  - signal_id: signal:commodities:late:chain_validation
judgments:
  - judgment_id: judgment:commodities:late:next_day_watch
```

### ai_tech / late
```yaml
bundle:
  agent_domain: ai_tech
  slot: late
  section_key: support_ai_tech
  primary_relation: counter
facts:
  - fact_id: fact:ai_tech:late:leader_break
signals:
  - signal_id: signal:ai_tech:late:diffusion_failure
judgments:
  - judgment_id: judgment:ai_tech:late:priority_cut
```

---

## 9. Invalid examples

Invalid:
- `agent_domain: metal`
- `section_key: support_ai-tech`
- fact with no source-layer meaning
- signal with empty `based_on_fact_ids`
- judgment with empty `based_on_signal_ids`
- support bundle that contains only a summary paragraph
- support bundle that declares both `support` and `counter` as equally primary

---

## 10. Acceptance use

Engineering and QA should use this file as the business payload validator for phase-1 support-agent producers.
