# A股 2.0 FSJ 持久化对接合同（Phase 1）

_日期：2026-04-22_

## 1. 文档目的

这份文档不是再解释一次 FSJ 概念，而是把 **A 股 2.0 在 Phase 1 里必须交付给持久化层的业务合同** 定死。

它回答四个问题：

1. FSJ 在业务语义上到底是什么，不能被误解成什么。
2. 一条可持久化 FSJ 记录最低必须带哪些字段。
3. business-layer、data-platform、report-layer 的所有权边界怎么划。
4. Phase 1 到底要求落什么“持久化-facing contract”，哪些增强能力明确留到后续。

本文与以下文档配套：

- `docs/A_SHARE_2_0_ONE_MAIN_THREE_SUPPORT_CONTRACT.md`
- `docs/A_SHARE_MAIN_AGENT_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_SUPPORT_AGENTS_DELIVERY_CONTRACT.md`
- `docs/A_SHARE_EARLY_MID_LATE_DATA_CONSUMPTION_CONTRACT_V1.md`
- `docs/A_SHARE_FSJ_AND_EVIDENCE_MAPPING_V1.md`
- `docs/A_SHARE_FSJ_LLM_ASSIST_POLICY_PHASE1_2026-04-22.md`
- `/Users/neoclaw/repos/ifa-data-platform/docs/A_SHARE_FSJ_LOCAL_PERSISTENCE_STRATEGY_PHASE1_2026-04-22.md`

---

## 2. FSJ 的业务语义（正式口径）

## 2.1 FSJ 不是“三段文案”，而是三层可追溯业务对象

在 A 股 2.0 中：

- **Fact**：已观察到的事实。
- **Signal**：业务上对事实组合后的结构解释。
- **Judgment**：面向最终报告/决策消费者的结论、提示或下一步动作。

FSJ 的最核心要求不是“写得像分析”，而是：

- judgment 不能脱离 signal
- signal 不能脱离 fact
- fact 不能脱离证据来源

所以 FSJ 的本质是：

> **一个带证据链、带时段语义、带业务归属、可重放/可审计/可再装配的分析对象。**

## 2.2 FSJ 的业务定位

FSJ 位于以下边界中间：

- **上游**：slot 数据消费结果、focus/seed、live/working/finalized evidence、support agent 提供的辅助证据
- **下游**：主报告 section 装配、support summary 装配、回放 QA、人工复核、未来 hit-rate / invalidation 分析

因此 FSJ 既不是：

- 原始采集数据
- Archive V2 的 source-retained truth
- 最终排版后的报告段落

也不是“想到什么就存什么”的临时 JSON。

它是 **business-layer 对证据进行语义提升后的标准交付对象**。

## 2.3 一条 FSJ 代表的最小业务单元

Phase 1 里，推荐把“一条 FSJ”理解为：

- 属于某个 `agent_domain`
- 属于某个 `slot`
- 服务于某个 `section_key`
- 围绕一个明确主题/对象集合
- 从 fact 到 signal 到 judgment 完成一条最短可审计链

也就是说，FSJ 的默认粒度不是整篇报告，也不是全市场总摘要，而是：

> **一个 section 内可独立成立、可独立解释、可独立回溯的一条分析链。**

例如：

- “竞价阶段机器人链条出现确认度提升”
- “午间主线从机器人扩散到电力设备但龙头一致性下降”
- “收盘后判断今日主线强度仍在，但明日需防高位分歧”

每一条都应能独立落成 FSJ bundle。

---

## 3. 业务侧必须稳定的主键维度

Phase 1 里，FSJ 的业务唯一性不能只靠文案内容。必须至少由以下维度共同确定：

- `market = a_share`
- `agent_domain`：`main|macro|commodities|ai_tech`
- `slot`：`early|mid|late`
- `business_date`
- `section_key`
- `fsj_kind`：`fact|signal|judgment`
- `object_key`：该条对象在本 bundle 内的稳定键

其中：

- `section_key` 决定这条 FSJ 服务哪个业务章节
- `object_key` 决定同一 section 下同类对象的稳定身份
- `business_date + slot + agent_domain + section_key + object_key + fsj_kind` 应构成业务上的幂等写入键

### 3.1 object_key 约束

`object_key` 不是随机 UUID 的替代品，而是业务稳定键，建议按以下来源构造：

- theme / sector：`theme:<normalized_name>`
- stock：`stock:<ts_code>`
- event：`event:<source>:<event_id_or_hash>`
- macro：`macro:<topic_key>`
- composite thesis：`thesis:<section_key>:<topic_key>`

如果没有可解释业务键，说明对象粒度还没定义清楚，不应直接进入正式持久化合同。

---

## 4. Phase 1 必填字段合同

## 4.1 FSJ bundle 级别必填字段

每次业务侧向持久化层交付，不是散落三张表碎片，而应至少能还原出一个 bundle。bundle 级最低字段：

```yaml
bundle_id: string                     # 业务生成的稳定/可追踪 id
market: a_share
business_date: YYYY-MM-DD
slot: early|mid|late
agent_domain: main|macro|commodities|ai_tech
section_key: string
section_type: thesis|support|risk|watch|plan|recap
producer: business-layer
producer_version: string
assembly_mode: manual_curated|rule_assembled|hybrid
report_run_id: string|null            # 若本 bundle 来自某次报告装配
slot_run_id: string|null              # 若能绑定 slot 执行/回放 run，必须填
replay_id: string|null                # slot replay / freeze / QA replay id
status: active|superseded|withdrawn
supersedes_bundle_id: string|null
summary: string                       # bundle 的一句话业务摘要
```

## 4.2 Fact 必填字段

```yaml
object_id: string
fsj_kind: fact
object_key: string
statement: string
fact_type: market|event|flow|breadth|theme|news|announcement|macro|commodity
entity_refs: [string]
metric_refs: [string]
evidence_level: E1|E2|E3|E4
source_layer: lowfreq|midfreq|highfreq|archive_v2|business_seed|slot_replay
source_family: string|null
source_table: string|null
source_record_locator: object|null
observed_at: datetime|string|null
freshness_label: fresh|same_slot|t_minus_1|stale|unknown
confidence: high|medium|low
```

### 4.2.1 Fact 的硬约束

- `statement` 必须是事实句，不能偷带结论。
- 必须能指出 `source_layer`。
- Phase 1 不要求所有 fact 都带到行级主键，但至少要能带到 `source_table` 或 `source_family`，以及必要时的 `source_record_locator`。
- 如果事实来自 slot freeze/replay 包，`source_layer` 必须写 `slot_replay`，不能伪装成实时 live source。

## 4.3 Signal 必填字段

```yaml
object_id: string
fsj_kind: signal
object_key: string
statement: string
signal_type: strengthening|weakening|rotation|divergence|confirmation|risk
based_on_fact_keys: [string]
signal_strength: high|medium|low
horizon: intraday|same_day|t_plus_1
confidence: high|medium|low
```

### 4.3.1 Signal 的硬约束

- `based_on_fact_keys` 不允许为空。
- signal 是解释，不是终局判断。
- signal 的 `object_key` 可以与上游核心 thesis 对齐，但不能丢失其依赖 facts 的关系。

## 4.4 Judgment 必填字段

```yaml
object_id: string
fsj_kind: judgment
object_key: string
statement: string
judgment_type: thesis|support|risk|watch_item|next_step
judgment_action: hold|upgrade|downgrade|observe|avoid|prepare|confirm|null
direction: bullish|bearish|mixed|neutral|conditional
based_on_signal_keys: [string]
priority: p0|p1|p2
invalidators: [string]
confidence: high|medium|low
```

### 4.4.1 Judgment 的硬约束

- `based_on_signal_keys` 不允许为空。
- `invalidators` Phase 1 可以简写，但不能完全缺失；如果确实没有，至少填 `[]`。
- `judgment_action` 用来保证这条 judgment 可执行、可被下游 UI/report 归类，而不是只剩情绪性描述。

---

## 5. 持久化-facing contract：业务层到底要交什么

## 5.1 Phase 1 必须交付 bundle + edges，而不是只交纯文本块

业务层交付给 data-platform 的最小合同应包含三类信息：

1. **bundle metadata**
2. **fsj objects**（facts / signals / judgments）
3. **lineage edges**（fact->signal、signal->judgment、bundle->evidence）

如果只交：

- 一段 final markdown
- 一块 summary json
- 或只有 judgment 文案数组

都不满足 Phase 1 FSJ 合同。

## 5.2 推荐交付结构（JSON 口径）

```json
{
  "bundle": {
    "bundle_id": "fsj:a_share:main:2026-04-22:mid:main_thesis:robotics",
    "market": "a_share",
    "business_date": "2026-04-22",
    "slot": "mid",
    "agent_domain": "main",
    "section_key": "main_thesis",
    "section_type": "thesis",
    "producer": "business-layer",
    "producer_version": "phase1",
    "assembly_mode": "hybrid",
    "slot_run_id": "...",
    "replay_id": null,
    "report_run_id": null,
    "status": "active",
    "summary": "盘中机器人主线维持强化，但龙头一致性开始分化"
  },
  "facts": [],
  "signals": [],
  "judgments": [],
  "edges": [
    {
      "edge_type": "fact_to_signal",
      "from_key": "fact:theme:robotics:breadth_up",
      "to_key": "signal:thesis:robotics:strengthening"
    },
    {
      "edge_type": "signal_to_judgment",
      "from_key": "signal:thesis:robotics:strengthening",
      "to_key": "judgment:thesis:robotics:keep_mainline"
    }
  ],
  "evidence_links": [
    {
      "evidence_role": "slot_replay",
      "ref_type": "slot_run_id",
      "ref_value": "..."
    },
    {
      "evidence_role": "archive_background",
      "ref_type": "archive_row_key",
      "ref_value": "..."
    }
  ]
}
```

这不是要求 Phase 1 立刻实现统一 API 服务，而是要求 **所有落盘对象至少在语义上等价于这个结构**。

---

## 6. ownership boundary（所有权边界）

## 6.1 business-layer 负责什么

business-layer 是 FSJ 业务真相的 owner，负责：

- 定义 `section_key` / `section_type`
- 决定哪些 fact 能进入正式业务链
- 决定哪些 signal 可以升级成 judgment
- 决定 judgment 的强度、方向、invalidator、priority
- 决定一条 bundle 是 `active` 还是被 supersede
- 明确 evidence 使用的是 live / working / archive / replay 哪一层

business-layer **不负责**：

- 设计底层物理表结构
- 决定数据库索引细节
- 接管 Archive V2 的 finalized source-truth 语义

## 6.2 data-platform 负责什么

data-platform 是 FSJ 落盘、索引、关联查询、回放对接的 owner，负责：

- 将 bundle / objects / edges 落到本地持久化表
- 为 `business_date / slot / agent_domain / section_key / object_key` 建立可查询主维度
- 存 evidence linkage（slot replay、Archive V2、source evidence、report artifact）
- 支持 active / superseded 的版本语义
- 保持 observed/raw reference 与 corrected/business representation 的并存

data-platform **不负责**：

- 修改 judgment 的业务含义
- 用平台规则偷偷替换 business-layer 的 direction/confidence/priority
- 把 FSJ 降格成“无边结构的 summary blob”

## 6.3 report-layer 负责什么

report-layer 负责：

- 消费 active FSJ bundle
- 按 slot / template / audience 进行 section 装配
- 在报告中展示 judgment，并能按需下钻 signal/fact/evidence
- 当 evidence 不足时，按合同进行降级展示

report-layer **不负责**：

- 发明新的业务 judgment 再反写替代 FSJ
- 无理由裁掉 FSJ 的 lineage，只保留漂亮文案

---

## 7. observed vs corrected：业务上必须同时承认两种表示

Phase 1 必须避免一个常见错误：

> 把“上游观测到的原始对象”直接等同于“最终业务采用的 FSJ 表示”。

正确做法是明确区分：

## 7.1 observed representation

指从数据层、slot replay、Archive V2、文本 history 里观察到的对象表示，例如：

- 原始标题
- 原始主题名
- 原始 source row key
- 原始事件 id/hash
- 原始表字段和值

## 7.2 corrected representation

指业务层经过归一、映射、聚合、去歧义后采用的对象表示，例如：

- 统一后的 `theme_key`
- 纠正后的 `entity_refs`
- 从多个 facts 汇总出的 `signal_type`
- 业务最终采用的 `judgment_action` / `direction`

## 7.3 Phase 1 约束

Phase 1 不要求 data-platform 立刻实现完整双写模型，但业务合同要求：

- fact 层至少能保留 observed source locator
- signal / judgment 层明确属于 corrected/business representation
- 不能因为 corrected 已形成，就丢掉 observed evidence 的追溯链

换句话说：

> **FSJ 的业务表达是 corrected 的；它的可审计性必须能回到 observed。**

---

## 7.4 LLM 参与边界（Phase 1 冻结口径）

FSJ Phase 1 允许在 **business-layer 内部** 使用 LLM 参与“语义提升”步骤，但必须满足以下冻结约束：

- **指定工具**：优先使用 business repo 已实现并已验证的 LLM utility：
  - service: `ifa_business_layer.llm.service.LLMService`
  - CLI: `scripts/ifa_llm_cli.py`
  - model alias: `grok41_thinking`
  - configured model id: `grok-4.1-thinking`
- **允许且预期的任务类型**：
  - 多来源事实摘要/压缩
  - 候选 signal/judgment 提取
  - 近重复叙述去重与 merge 建议
  - 冲突证据整理与 contradiction resolution 建议
  - section synthesis 草稿
- **不允许外包给 LLM 的确定性职责**：
  - bundle 主维度/幂等键生成
  - `fact -> signal -> judgment` 边的最终落盘结构
  - source locator / evidence link / observed record 的保真写入
  - active/superseded/withdrawn 版本语义
  - `judgment_action` / `direction` / `priority` 的无证据瞎改写
  - producer persistence path / query path / active bundle selection
- **最终业务 owner 仍是 business-layer**：LLM 可以给出候选业务表示，但不能跳过合同字段与 lineage discipline。

因此本合同补充冻结为：

> **`grok41_thinking` 是 FSJ 的 reasoning/synthesis assist layer，不是 schema owner，不是 lineage owner，也不是最终业务语义 owner。**

### 7.4.1 从 LLM 到持久化的收口纪律

LLM 的输出只能是 **candidate business representation**，不能直接视为 persistence-ready bundle。

进入正式 FSJ 落盘前，必须由 deterministic business/data code 明确完成：

- bundle/object/edge 的稳定键生成
- evidence level 与 degrade mode 的最终判定
- lineage edges 与 evidence links 的最终归并
- active/superseded/withdrawn 状态落定
- `FSJStore` 持久化提交与回读校验

这条纪律适用于 early / mid / late 全部 slot。

### 7.4.2 Prompt 版本与输出结构要求

凡使用 `grok41_thinking` 参与 FSJ 生产，审计面至少必须能回答以下问题：

- 用的是哪个 model alias / model id
- 用的是哪个 prompt version
- 该次调用属于哪个 FSJ stage
- 输入证据范围是什么
- 产出的候选结构是什么
- 最终是否被采纳，以及采纳到什么程度

因此至少应保留这些审计位：

- `llm_model_alias`
- `llm_model_id`
- `llm_prompt_version`
- `llm_stage`
- `llm_input_scope`
- `llm_output_schema_name` 或等价结构版本
- `llm_adoption_result`

Phase 1 推荐 `grok41_thinking` 输出使用结构化结果，而不是只返回自由散文。最低应可恢复为：

- candidate facts
- candidate signals
- candidate judgments
- candidate lineage/link hints
- conflict / uncertainty notes
- optional section draft

若输出不能恢复到上述结构，则只能作为人工参考，不应直接进入正式 FSJ persistence contract。

## 8. Phase 1 必做 vs 明确后置

## 8.1 Phase 1 必做

1. 定义稳定 bundle 维度与对象级必填字段。  
2. 明确 `fact -> signal -> judgment` 的边关系必须可恢复。  
3. 明确 `slot_run_id / replay_id / report_run_id` 等关键外部链接位。  
4. 明确 active / superseded / withdrawn 三种版本状态。  
5. 明确 observed evidence 不得丢失到无法追溯。  
6. 明确 FSJ 是 business semantic layer，不等于 source archive，不等于 report markdown。  
7. 若使用 LLM 辅助 FSJ 装配，必须保留 prompt/version/model alias/输入证据范围/输出采纳结果的审计位。  

## 8.2 Phase 1 明确不要求

1. 不要求立刻做通用跨市场 FSJ 平台。  
2. 不要求立刻做评分系统、命中率分析、自动回测。  
3. 不要求每个 fact 都做到物理 row-level FK 严格约束。  
4. 不要求立刻做复杂图数据库。  
5. 不要求业务层一次性解决全部主题归一/实体消歧。  

---

## 9. 成功标准

如果本合同被正确执行，A 股 2.0 的 Phase 1 FSJ 持久化对接应满足：

- 任一主结论都能找到对应 judgment、signals、facts。
- 任一 fact 都能说明来自哪一层证据、哪个 family/table 或 replay 包。 
- data-platform 可以不理解业务内容，但能稳定保存和查询业务关系。 
- report-layer 可以消费 active bundle，而不是只能重新 parse 文案。 
- 后续做 replay / QA / 复盘时，能恢复“当时为什么这么判断”。

---

## 10. 一句话冻结结论

A 股 2.0 的 Phase 1 FSJ 持久化合同已经明确为：

> **business-layer 输出的是带 bundle 元数据、对象级必填字段、fact-signal-judgment 边关系、以及与 slot replay / Archive V2 / source evidence / report artifact 可链接的标准业务对象；当语义提升/摘要/去重/综合推理需要 LLM 时，优先通过 business-layer 的 `grok41_thinking` 工具完成，但 data-platform 仍只负责稳定落盘与查询，不改写业务语义。**
