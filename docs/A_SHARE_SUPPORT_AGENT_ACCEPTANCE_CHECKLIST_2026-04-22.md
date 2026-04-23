# A-share Support Agent Acceptance Checklist（business-layer / 2026-04-22）

Use this checklist before accepting any support-agent implementation as phase-1 complete.

---

## 1. Repo-boundary check

- [ ] All new business semantics live in `/Users/neoclaw/repos/ifa-business-layer`
- [ ] No mainline support-agent business buildout was placed in `ifa-data-platform`
- [ ] No business requirement here depends on data-platform-only path assumptions

---

## 2. Domain correctness

- [ ] Only these domains are used: `macro`, `commodities`, `ai_tech`
- [ ] No alias drift: `commodity` / `metals` / `ai-tech` / `tech_ai`
- [ ] Each domain maps to the correct section key

Required mapping:
- `macro -> support_macro`
- `commodities -> support_commodities`
- `ai_tech -> support_ai_tech`

---

## 3. Slot correctness

- [ ] Only `early` and `late` are implemented for phase 1
- [ ] No fake `mid` support auto-producer is claimed as complete
- [ ] Slot behavior matches business contract expectations

---

## 4. FSJ chain completeness

For every produced support bundle:

- [ ] at least 1 fact exists
- [ ] at least 1 signal exists
- [ ] at least 1 judgment exists
- [ ] every signal references fact(s)
- [ ] every judgment references signal(s)
- [ ] invalidation/caution field exists

---

## 5. Relation semantics

- [ ] every support bundle declares exactly one primary relation
- [ ] primary relation is one of `support|adjust|counter`
- [ ] relation reflects impact on main-agent judgment rather than narrative tone

---

## 6. Domain-bounded behavior

### macro
- [ ] does not rewrite full market recap
- [ ] focuses on macro relevance to A-share
- [ ] distinguishes driver vs amplifier vs background

### commodities
- [ ] does not become a standalone commodity-market report
- [ ] explains A-share chain mapping explicitly
- [ ] does not overclaim weak correlation as causation

### ai_tech
- [ ] does not generalize from one stock to the whole sector
- [ ] distinguishes mainline vs branch vs noise
- [ ] identifies whether diffusion is real or false

---

## 7. Degrade discipline

- [ ] thin evidence lowers confidence or conclusion strength
- [ ] weak inputs can degrade to watch/risk style judgment
- [ ] no strong conclusion is emitted from reference-only inputs
- [ ] missing evidence is surfaced rather than hidden

---

## 8. Main-agent consumability

- [ ] output can be consumed as `support_macro`, `support_commodities`, `support_ai_tech`
- [ ] output is concise enough for main-agent assembly
- [ ] output is structured enough for persistence and replay
- [ ] no support output tries to replace the main agent’s market-wide thesis

---

## 9. Production-grade rejection conditions

Reject the build if any of the following is true:

- [ ] wrong repo
- [ ] wrong domain IDs
- [ ] wrong section keys
- [ ] prose-only output with no stable FSJ chain
- [ ] relation semantics missing
- [ ] support agent oversteps into full main-agent behavior
- [ ] implementation claims `mid` support automation without business approval

---

## 10. Completion bar

Support-agent phase-1 buildout is accepted only when:

- [ ] all three domains are specified
- [ ] both required slots are specified
- [ ] payload spec is frozen
- [ ] acceptance checklist passes
- [ ] the package is stored in the canonical business repo
