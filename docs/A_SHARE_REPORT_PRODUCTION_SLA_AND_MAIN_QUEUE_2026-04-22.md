# A 股 2.0 报告生产 SLA 与主任务队列（2026-04-22）

## 目的

本文档将 Yunpeng 最新确认的报告生产时点要求，正式冻结为 A 股 2.0 business layer 的当前主线执行约束。

它回答两个问题：
1. **什么时候必须生成完**
2. **当前主任务队列按什么优先级推进**

本文档是当前阶段的 **business-layer canonical queue note**。

---

## 业务范围

当前范围仅针对：
- **A 股 2.0**
- **一主三辅**
  - 主：MAIN
  - 三辅：macro / commodities / ai_tech

---

## 冻结后的生产时点要求（北京时间）

### 1) 早报

**范围：一主三辅全部都要有早报。**

也就是以下 4 份报告：
- MAIN early report
- macro early report
- commodities early report
- ai_tech early report

### SLA
- **必须在 09:15 前生成完成**

### 含义
- 这里说的是 **生成完成**，即系统内部应形成可用报告产物
- 当前阶段不把投递策略写死到本文档；投递可由后续 delivery/orchestration 层继续约束

---

### 2) 中报

**范围：当前只要求主中报。**

也就是：
- MAIN mid report

### SLA
- **必须在 12:30 前生成完成**

### 当前额外约束
- **中报当前暂不要求投递**
- 即：中报要生成，但 delivery 不是当前阶段硬要求

---

### 3) 晚报

**范围：当前按一主三辅理解执行晚报。**

也就是以下 4 份报告：
- MAIN late report
- macro late report
- commodities late report
- ai_tech late report

### SLA
- **晚报不要求过早完成，当前目标时点为 17:30**

### 含义
- 晚报应优先保证收盘后事实更完整、质量更稳
- 因此相较早报，中间留给 final/stable evidence 的收口时间可以更宽

---

## 当前阶段的业务理解

### 一主三辅的报告关系
- **主报告只有 1 份**
- **三辅是单独 3 份独立报告**
- 主报告只吸收三辅的 **提要 / concise summaries**
- 主报告 **不 inline 三辅全文**

### 这意味着
- 早报最终应形成 **4 份可用报告产物**
- 中报当前应形成 **1 份可用主报告产物**
- 晚报最终应形成 **4 份可用报告产物**

---

## 当前主任务队列（按优先级）

以下队列用于指导实现顺序。

### P0：必须优先完成

#### P0-1. 早报一主三辅的 end-to-end 生成闭环
目标：
- 在 09:15 前稳定生成：
  - MAIN early
  - macro early
  - commodities early
  - ai_tech early

要求：
- 使用已冻结 FSJ / report / support-summary 业务语义
- 生成链路可测试、可审计、可评估
- 不因 support 缺失而 silently 假装完成

#### P0-2. 主中报生成闭环
目标：
- 在 12:30 前稳定生成 MAIN mid report

要求：
- 当前阶段以“生成完成”为硬目标
- 投递先不纳入硬要求

#### P0-3. 晚报一主三辅生成闭环
目标：
- 在 17:30 前完成：
  - MAIN late
  - macro late
  - commodities late
  - ai_tech late

要求：
- 优先保证 close/final/stable evidence 完整性
- 如果质量门禁未过，允许 review/hold，不允许伪装成 fully ready

---

### P1：强相关配套项

#### P1-1. MAIN report orchestration
- 早 / 中 / 晚 report generation orchestration
- package / qa / eval / dispatch 串联

#### P1-2. SUPPORT report standalone delivery path
- 三辅各自独立报告的渲染、artifact、review/send readiness

#### P1-3. quality gate / eval / dispatch
- 每个时点是否 ready
- 是否仅 review
- 是否 hold

---

### P2：后续增强项

#### P2-1. 主报告中的三辅提要质量继续增强
#### P2-2. 三辅 LLM-assisted slices 全量升级
#### P2-3. 更完整的 delivery automation

---

## 当前执行原则

### 1. 先保证“按时生成”，再继续增强“怎么发得更好”
当前硬约束先是：
- 09:15
- 12:30
- 17:30

### 2. 不中断 business/data repo 边界
- business canonical 定义在 `ifa-business-layer`
- implementation / runtime / rendering / eval 在 `ifa-data-platform`

### 3. 不把中间产物冒充最终报告
- FSJ ≠ 报告
- assembly ≠ 最终可发报告
- 必须通过 renderer / package / qa 才能称为 ready artifact

---

## 验收口径

以下情况下，才算该时点目标完成：

### 早报完成
- 4 份报告均已生成
- 生成时间不晚于 09:15
- 至少达到当前 phase 的 quality gate 最低要求

### 中报完成
- MAIN mid report 已生成
- 生成时间不晚于 12:30
- 当前阶段允许不投递

### 晚报完成
- 4 份报告均已生成
- 目标时点不晚于 17:30
- 质量门禁与 close/stable evidence 要求满足当前 phase 约束

---

## 当前状态标注

本文档落地后，表示以下内容已被 business layer 正式确认：
- 早报必须是一主三辅，且 09:15 前完成
- 中报当前只要求主中报，且 12:30 前完成
- 晚报允许更稳妥收口，当前目标时点 17:30
- 这些要求应进入主线任务队列，作为后续 subagent 并行推进的硬目标
