# A-share Phase 1 FSJ 结构定义与章节级证据映射（v1）

## 1. 文档目的

这份文档定义 Phase 1 的第一版：

- FSJ（fact / signal / judgment）对象结构
- 各层责任边界
- section-level evidence mapping 原则
- 证据质量等级

目标不是把所有对象一次定死，而是建立一个足够稳定、可以驱动实现的 v1 合同。

---

## 2. FSJ 的基本思想

所有业务输出都应尽量拆成三层：

- **Fact**：发生了什么
- **Signal**：这些事实在业务上意味着什么变化
- **Judgment**：基于 signals，当前应该如何判断与表述

这样做的目的：

- 避免把原始事实和主观结论混在一起
- 让支持证据可以被复用
- 让主报告能追溯到判断来源
- 为后续 replay / QA / 质检打基础

---

## 3. FSJ v1 对象结构

## 3.1 Fact v1

### 定义
Fact 是已经观察到的、可以追溯到具体来源的事实单元。

### 最低字段建议

```yaml
fact_id: string
agent_domain: main|macro|commodities|ai_tech
slot: early|mid|late
section_key: string
fact_type: market|event|flow|breadth|theme|news|announcement|macro|commodity
statement: string
entity_refs: [string]
metric_refs: [string]
source_layer: lowfreq|midfreq|highfreq|archive_v2|business_seed
source_table: string|null
source_time: datetime|string
freshness_label: string
confidence: high|medium|low
```

### Fact 责任
- 数据 / 素材层提供可追溯事实
- 业务层负责挑选哪些 fact 值得进入 section
- fact 本身不应直接写成判断句

## 3.2 Signal v1

### 定义
Signal 是对多个 facts 的业务解释，表示“变化方向”或“结构状态”。

### 最低字段建议

```yaml
signal_id: string
agent_domain: main|macro|commodities|ai_tech
slot: early|mid|late
section_key: string
signal_type: strengthening|weakening|rotation|divergence|confirmation|risk
statement: string
based_on_fact_ids: [string]
signal_strength: high|medium|low
horizon: intraday|same_day|t_plus_1
confidence: high|medium|low
```

### Signal 责任
- signal 允许解释，但必须绑定 fact
- signal 可以是 support / adjust / counter
- signal 仍不等于最终 judgment

## 3.3 Judgment v1

### 定义
Judgment 是面向最终报告消费者的业务结论。

### 最低字段建议

```yaml
judgment_id: string
agent_domain: main|macro|commodities|ai_tech
slot: early|mid|late
section_key: string
judgment_type: thesis|support|risk|watch_item|next_step
statement: string
direction: bullish|bearish|mixed|neutral|conditional
based_on_signal_ids: [string]
priority: p0|p1|p2
invalidators: [string]
confidence: high|medium|low
```

### Judgment 责任
- judgment 必须可读、可执行、可复盘
- judgment 必须引用 signal
- judgment 可以存在不确定性，但不能脱离证据

---

## 4. FSJ 的责任边界

## 4.1 数据层责任
- 提供事实来源、时间、freshness、表级可追溯性
- 不负责最终业务 judgment

## 4.2 业务层责任
- 定义 section 需要什么类型的 FSJ
- 决定哪些 signals 可以升级为 judgment
- 决定哪些 judgment 进入最终主报告

## 4.3 报告层责任
- 按章节装配 FSJ
- 保留 judgment -> signal -> fact 的可追溯关系
- 在 evidence 不足时做降级显示

---

## 5. 章节级 evidence mapping 原则

## 5.1 原则一：每个 section 至少要有 judgment，但不能只有 judgment

每个正式章节都应满足：

- 至少 1 个 judgment
- 至少 1 个 signal
- 至少 1-3 个 supporting facts

如果只剩判断、没有信号和事实，说明该 section 不可审计。

## 5.2 原则二：主章节证据要求高于 support 章节

- 主 Agent 主结论 section：证据要求最高
- support summary section：可以更压缩，但仍需保留核心证据链

## 5.3 原则三：盘中章节允许证据降级，但必须显式标注

对于 early / mid：

- 可以使用 highfreq working 与 best-effort lowfreq
- 但必须标注 freshness / confidence / degrade 状态

## 5.4 原则四：晚报章节优先使用 daily-final / archive-compatible 证据

对于 late：

- 优先 midfreq daily-final
- 优先 lowfreq 已沉淀文本事实
- 优先 T-1 archive_v2 背景事实

---

## 6. 证据质量等级（Phase 1）

## E1 - Finalized evidence
适用：
- midfreq daily-final
- 已稳定沉淀的 lowfreq history
- archive_v2 finalized daily facts

特点：
- 最适合晚报主章节
- 可支持较强 judgment

## E2 - Working but timely evidence
适用：
- highfreq working
- 盘前 snapshot
- event stream

特点：
- 适合早报 / 中报
- 必须带 freshness / confidence
- 不应伪装成 final truth

## E3 - Reference / seed evidence
适用：
- focus list
- key focus
- business seed
- 静态 watchlist / mapping

特点：
- 可说明“看什么”
- 不能单独支撑“今天发生了什么”的 judgment

## E4 - Narrative-only weak evidence
适用：
- 未绑定表级或对象级来源的文字判断
- 二手归纳且无明确事实锚点的叙述

特点：
- Phase 1 不应单独作为正式 judgment 依据
- 仅可作为弱补充

---

## 7. Section 级最小映射表

| Section 类型 | 最小 Judgment | 最小 Signal | 最小 Fact | 可接受证据等级 |
|---|---:|---:|---:|---|
| 主 Agent 早报主结论 | 1 | 1 | 2 | E2/E3，必要时混合 E1 |
| 主 Agent 中报主结论 | 1 | 2 | 2-3 | E2 为主，可辅 E1 |
| 主 Agent 晚报主结论 | 1 | 2 | 3 | E1 为主，可辅 E2 |
| 宏观 support | 1 | 1 | 1-2 | E1/E3，早盘可辅 E2 |
| 商品 support | 1 | 1 | 1-2 | E1/E2/E3 |
| AI科技 support | 1 | 1 | 2 | E2/E1/E3 |
| 风险提示 section | 1 | 1 | 1 | 任一等级均可，但必须标注 confidence |

---

## 8. 实施建议

Phase 1 不要求立刻做成复杂对象数据库，但至少应保证：

- 每个关键 section 可以明确列出 judgment / signal / fact
- judgment 能回溯到 signal
- signal 能回溯到 fact
- fact 至少能回溯到 source layer + source table/seed

如果工程上暂时无法完全结构化，也必须在文档/JSON 中保留同等语义字段。

---

## 9. Phase 1 与后续阶段的边界

## Phase 1 内
- 定义 FSJ v1
- 定义 section evidence minimum
- 定义 evidence quality levels
- 定义 degrade 原则

## 后续阶段
- FSJ 对象标准化落库
- 质量打分
- judgment review loop
- cross-day replay comparison
- signal hit-rate / invalidation analytics
