# iFA Business Repo 现状基线（2026-04-22）

## 1. 这份文档是干什么的

这不是产品蓝图，也不是技术实现计划。

它的目标很简单：**基于当前 `ifa-business-layer` 仓库已经存在的真实内容**，从 business 视角回答：

- 我们现在 business 侧已经有什么
- 还缺什么
- 哪些地方和 iFA 2.0 产品目标已经对齐
- 哪些地方只是底层准备好了，还没形成业务闭环
- 接下来 business 侧最应该优先做什么

参考的产品方向框架：

- iFA 2.0：**一主三辅**
- **早 / 中 / 晚** 节奏化输出
- **briefing + long report** 双层输出
- **A-share / US** 双市场视角
- 面向真正可用的 business/product 闭环，而不只是底层数据或脚本

---

## 2. 先说结论

一句话总结：

**这个 repo 现在更像“business 对象控制面 + 默认关注池配置层”，而不是一个已经成型的 iFA 2.0 business 产品层。**

再直白一点：

- 它已经把“看什么、默认关注什么、归档什么”这件事做成了**可落库、可维护、可测试**的 business 基础层；
- 但它还没有把这些对象真正组织成 **一主三辅、早中晚节奏、briefing + 长报告、A 股 + 美股联动** 的业务产物；
- 所以当前状态可以定义为：
  - **business 底层骨架已有**
  - **业务编排层明显缺失**
  - **产品形态还远未闭环**

---

## 3. 当前 repo 里，business 侧已经有什么

### 3.1 已经有一个清晰的 business object 模型

当前仓库的核心不是“采集”，而是“定义 business 侧要管理的对象”。

从 `README.md`、`docs/BUSINESS_LAYER_DESIGN.md`、`sql/001_business_layer_baseline.sql` 可以确认，这个 repo 当前稳定管理的是三张表：

- `ifa2.focus_lists`
- `ifa2.focus_list_items`
- `ifa2.focus_list_rules`

这意味着 business 侧已经能表达：

- 某个 owner 关心哪些列表
- 列表属于 `key_focus` / `focus` / `archive_targets`
- 列表里有哪些具体对象
- 每个对象属于什么资产类别
- 列表规则是什么（如 target_size、granularity、identity_strategy、sub_buckets）

从 business 角度看，这一步很重要，因为它把“关注池 / 核心池 / 归档池”从口头概念变成了**标准化对象**。

### 3.2 已经有默认 owner 作用域和未来多租户扩展边界

当前 phase-1 的默认 owner 为：

- `owner_type=default`
- `owner_id=default`

同时文档里已经预留未来扩展：

- `customer`
- `account`
- `org`

这说明 repo 现在的设计不是一次性的硬编码脚本，而是按“未来可做客户/账户级定制”的 business control plane 在搭。

### 3.3 已经有 8 个 canonical focus families + 3 个 archive target families

当前默认种子不是空架子，而是有明确 family 设计和数量约束的。

根据 `ifa_business_layer/defaults.py` 和 `tests/test_business_layer_phase1.py`，当前默认层面已经稳定存在：

#### 八个 canonical focus families

- `default_stock_key_focus`（20）
- `default_stock_focus`（80）
- `default_macro_key_focus`（5）
- `default_macro_focus`（10）
- `default_tech_key_focus`（20）
- `default_tech_focus`（50）
- `default_asset_key_focus`（12）
- `default_asset_focus`（20）

#### 三个 archive target families

- `default_archive_targets_minute`（19）
- `default_archive_targets_15min`（36）
- `default_archive_targets_daily`（170）

这说明 business repo 至少已经把“默认覆盖范围”做成了**可验证的初始盘子**，而不是停留在“以后再说”。

### 3.4 已经有明确的 A-share 优先策略

当前 stock family 的规则是清楚的，不是隐含假设。

`README.md`、`docs/BUSINESS_LAYER_FOCUS_FAMILIES_V2.md` 和测试都明确写了：

- 当前 stock seed 依赖 `ifa2.stock_basic_current`
- 当前 repo / schema 里没有同等维护契约的 US/HK stock universe
- 因此 **phase 1 的股票 focus 只支持 A-share**
- 这被视为“当前真实边界”，不是忘了做

所以，从 business truth 来看：

- **A 股覆盖是已落地的**
- **美股股票覆盖在当前 business repo 里还没形成正式对象层**

### 3.5 已经有 macro / tech / asset 三类补充视角

这个 repo 不只是股票名单仓库。

它已经把业务对象拆成了：

- stock
- macro
- tech
- asset

其中：

- `macro` 里已有中美宏观指标（如 CN_CPI、US_CPI、US_NFP、US_FED_FUNDS 等）
- `tech` 是主题化股票子集
- `asset` 是跨资产的 rolling canonical contracts（如 `AU0`、`CU0`、`SC0`、`M0`、`TA0`）

这件事和 iFA 2.0 的“一主三辅”思路是**方向上相通的**：

- “主线”不可能只靠单一股票池
- 宏观 / 科技主题 / 大类资产，本身就是支持主判断的重要辅助手

虽然 repo 里还没有直接写成“一主三辅”的产品语言，但底层对象形态已经在往这个方向靠。

### 3.6 已经有稳定的 seed / CLI / schema init / CRUD / batch 操作能力

`scripts/focus_cli.py` 已经支持：

- `init-schema`
- `seed-default`
- `list-lists`
- `list-items`
- `add-list`
- `delete-list`
- `add-item`
- `delete-item`
- `bulk-upsert`
- `bulk-delete`

这代表当前 repo 已经不是“文档层 business 想法”，而是已经具备：

- 可初始化
- 可重建
- 可查看
- 可人工维护
- 可批量修改

从 business 运营角度，这意味着默认盘子已经有“维护入口”。

### 3.7 已经有测试，且核心 focus baseline 基本可验证

我实际跑了仓库测试：

```bash
/Users/neoclaw/repos/ifa-data-platform/.venv/bin/python -m pytest tests/test_business_layer_phase1.py tests/unit/llm tests/integration/llm -q
```

结果：

- **7 个测试通过**
- **1 个测试失败**

通过的部分说明：

- schema init / default seed / CRUD / batch 操作这条主链路基本是通的
- 默认 list 数量、条目数量、规则字段这些关键 truth 是可测的

失败的部分是一个 LLM integration smoke test，失败原因不是业务逻辑本身，而是测试环境里没有设置 `PYTHONPATH`，导致：

- `ModuleNotFoundError: No module named 'ifa_business_layer'`

这反过来也说明：

- **focus business baseline 这一层相对扎实**
- **LLM utility 的测试接线还不够收口**

### 3.8 已经有一个可复用的 LLM utility 底座，但它仍是工具层

repo 中已经存在：

- `scripts/ifa_llm_cli.py`
- `ifa_business_layer/llm/*`
- `config/llm/*`
- `README_llm_utility.md`
- `docs/LLM_LIVE_VALIDATION_MATRIX.md`

这说明 business repo 已经开始为未来的：

- fact extraction
- narrative generation
- report generation
- structured JSON generation

准备统一 LLM gateway。

而且 live validation matrix 也证明：

- 某些 provider / adapter 组合已经测通过
- 不是停留在纯 spec

但当前它仍然是**通用 LLM 工具层**，不是产品化的“早报/中报/晚报生产线”。

---

## 4. 和 iFA 2.0 产品目标已经对齐的地方

### 4.1 “一主三辅”的底层对象拆分方向，已经部分对齐

虽然 repo 里没有直接产出“一主三辅”页面或报告，但底层对象已经不是单池，而是多维度：

- stock
- macro
- tech
- asset

这至少说明当前 business layer 已经接受一个事实：

**产品主判断需要多个支持视角，不是只有股票池。**

这和 iFA 2.0 想要的主线判断 + 支持模块是兼容的。

### 4.2 “briefing / long report”所需的关注对象底座，已经部分具备

不管是 briefing 还是长报告，第一步都得先明确：

- 看哪些对象
- 哪些是 key focus
- 哪些是 broader focus
- 哪些要做历史归档

这件事当前 repo 已经做了，而且结构还算清楚。

也就是说，**报告的对象输入层已经开始成型**。

### 4.3 A-share 方向已经明确且可执行

产品如果要先把 A-share 做稳，现在这个 repo 是支持的：

- A 股 stock focus 有默认池
- tech focus 本质上也是 A 股科技主题池
- macro / asset 也能为 A 股判断提供背景和验证

所以如果产品阶段先以 A-share 为主，这个 repo 的现状是能承接的。

### 4.4 业务对象和数据采集运行时做了边界隔离，这对后续产品化是对的

`docs/BUSINESS_LAYER_DESIGN.md` 很明确：

- 这里是 business-control plane
- 不是 collection runtime

这个边界很重要，因为未来如果要做：

- 客户化版本
- 不同用户关注池
- 不同市场版本
- 不同报告策略

business 层必须独立，不然产品变更会被 runtime 绑死。

这个架构方向是对的。

---

## 5. 还没对齐、或者明显缺的是什么

这里是最关键部分。

### 5.1 还没有 “一主三辅” 的正式 business 编排模型

当前 repo 里有 stock / macro / tech / asset，但并没有正式定义：

- 谁是“主”
- 哪三块是“辅”
- 主辅之间如何汇总、优先级如何表达
- 最终 briefing / long report 怎么引用这些层

换句话说，现在有的是**对象池**，没有的是**产品级叙事结构**。

如果按照 iFA 2.0 目标，business repo 后面至少还需要一种正式表达：

- main thesis / main market view
- support-1 / support-2 / support-3
- 每个 support 对应哪些 focus families / metrics / evidence

这层现在 repo 里还没有。

### 5.2 还没有“早 / 中 / 晚” cadence 的 business 产物定义

当前 repo 虽然有：

- `key_focus`
- `focus`
- `archive_targets`
- frequency granularity（minute / 15min / daily）

但这些仍然偏底层。

它还没有真正定义：

- 早报看什么
- 盘中简报看什么
- 晚报看什么
- 哪些内容是 brief 版
- 哪些内容进入 long report
- 同一对象在不同时间段是否要不同权重或不同结构

所以当前 repo 对 cadence 的支撑还停留在：

- **数据/对象粒度隐含支持了节奏分层**
- **但没有产品层 schedule + template + output contract**

### 5.3 还没有 briefing 和 long report 的业务模板/契约

repo 目前没有看到成熟的 business-facing 文档来定义：

- briefing 输出字段
- long report 输出章节
- 每个章节绑定哪些对象池
- 结论、证据、风险提示的标准格式

LLM utility 只是“以后可调用模型”的基础设施，不等于已经有报告产品。

所以这一块现在仍然缺：

- report schema
- report template
- report assembly logic
- report acceptance criteria

### 5.4 US 股票业务范围还没有真正进入当前默认 business 层

产品目标里有 A-share / US scope。

但从 repo 真实情况看：

- 宏观对象里有 US 指标
- 但 **股票 focus family 只有 A-share**
- tech family 也是 A-share 科技股子集
- 没有 US stock key_focus / focus
- 没有 US tech / US watchlist 的默认 business family

所以现在的真实状态不是“A 股 + 美股双市场已成型”，而是：

- **A 股股票侧已成型**
- **美股目前只体现在少量宏观变量层**
- **美股业务对象层尚未成立**

### 5.5 还没有把 archive targets 和最终业务输出闭环起来

当前 repo 有三个 archive target families，这代表“要存哪些历史”的 business 意图已经表达出来了。

但 repo 里看不到：

- 这些 archive target 如何服务 briefing
- 如何服务 long report
- 如何沉淀成可回看、可复盘、可解释的产品资产

所以现在 archive target 更像“底层准备好了的目标集”，还不是“业务闭环的一部分”。

### 5.6 还没有客户/账户级配置真正跑起来

虽然 owner model 已经预留：

- customer
- account
- org

但当前真实落地仍然是：

- `default/default`

所以从产品层看：

- 多租户边界有了
- 但个性化业务配置还没进入实际可用阶段

这意味着 repo 还没有真正进入“面向客户产品配置”的阶段，仍然是默认盘子的阶段。

### 5.7 LLM utility 已有，但没有接成真正的业务流水线

LLM utility 是一个值得保留的底层件，但当前状态仍然是：

- 有 CLI
- 有 config
- 有 provider/model 验证
- 有单元测试

但没有看到真正落地的业务流程，例如：

- 基于 morning materials 自动生成 morning briefing
- 基于 midday signals 自动生成 intraday note
- 基于 end-of-day evidence 自动生成 long report
- 输出与 focus families、cadence、模板强绑定

所以它现在更像“模型接入底座”，不是“报告业务引擎”。

---

## 6. 哪些地方只是底层准备好了，还没形成业务闭环

这一段专门给 Yunpeng 看：哪些东西“看上去像做了很多”，但 business 上还不能误判为“产品已经有了”。

### 6.1 focus families 已经有了，但还不是产品栏目

当前 focus family 很清楚，但它们还只是：

- 关注池
- 对象池
- 归档池

还不是：

- 主线栏目
- 支撑栏目
- briefing 模块
- 长报告章节

**结论：对象准备好了，产品表达还没搭起来。**

### 6.2 archive target 已经有了，但还不是复盘闭环

有 archive target，不等于已有：

- 复盘框架
- 归因框架
- 信号有效性回看
- 日/周/月表现评估

**结论：存什么已经定义了，但为什么存、存完怎么用，业务层还没接起来。**

### 6.3 LLM utility 已经有了，但还不是稳定报告引擎

有 LLM CLI，不等于有：

- report workflow
- output contract
- versioned prompt system
-质量验收机制
- 早中晚稳定生产能力

**结论：模型工具层有了，报告产品层没有。**

### 6.4 owner model 有了，但还不是客户化产品

现在只是 schema 设计兼容未来多租户，不代表已经做出：

- 客户级 watchlist
- 客户级 report 模板
- 客户级市场偏好
- 客户级权限/配置界面

**结论：架构上预留了，产品上还未启用。**

---

## 7. 用 iFA 2.0 的视角看，当前 repo 的真实定位

如果一定要给这个 repo 在 iFA 2.0 里定位，我会这样定义：

### 它现在已经是：

- **business object registry**
- **default focus universe manager**
- **archive target intent layer**
- **future LLM workflow 的基础工具层**

### 它现在还不是：

- iFA 2.0 的主产品编排层
- 一主三辅决策框架本身
- 早中晚报告系统
- briefing + long report 生产系统
- A 股 / 美股统一业务视图

这个判断很重要，因为它决定后续工作不要跑偏。

后面最该做的不是继续堆更多底层“列表”，而是把这些列表真正接入产品结构。

---

## 8. 接下来 business 侧最该做的几件事（优先级排序）

### P0：先把“一主三辅”的 business contract 明确下来

这是最高优先级。

建议在这个 repo 里先补一个明确文档，定义：

- 一主三辅分别是什么
- 每一块对应哪些 focus family / 证据来源 / 输出职责
- 主辅之间的升级与冲突规则
- briefing 和 long report 如何映射到主辅结构

如果这一步不做，后面任何报告系统都只能是“拼素材”，不会是产品。

### P1：把“早 / 中 / 晚”节奏正式写成业务层对象或模板契约

当前 cadence 只是产品要求，还不是 repo 里的 business truth。

建议明确至少三个层次：

- 早：开盘前定位、重点关注、主要风险、主辅框架预设
- 中：盘中变化、偏离、信号更新、是否修正主判断
- 晚：日内归因、结论沉淀、次日准备

这一步不一定马上写代码，但至少要把：

- 每个时段输入什么
- 输出什么
- 用哪些 focus families
- 产物给谁看

写成正式 business 约束。

### P2：定义 briefing + long report 的标准输出结构

建议不要先做“自由发挥式报告”，而是先定义 schema。

至少要先定：

- briefing 的固定字段
- long report 的固定章节
- 每段内容的对象来源
- 结论 / 证据 / 风险 的标准位置

这样后续 LLM utility 才有地方接，不然工具再强也会输出漂。

### P3：补齐 US business object layer，而不是只停留在宏观变量

如果产品目标明确包含 A-share / US，那么当前 repo 最大的方向性缺口之一就是：

- 没有 US stock focus family
- 没有 US tech / US leaders / US watchlist 默认对象层

所以应该先决定：

- US 默认覆盖范围怎么定义
- 是 broad watchlist 还是行业/主题层
- 与 A 股是否共用一套主辅结构

这是从“产品说双市场”走向“repo 真正双市场”的关键一步。

### P4：把 archive targets 接到复盘/报告闭环里

建议后续不要把 archive target 只当成“给数据层看的名单”。

应该明确：

- 哪些 archive target 支撑 briefing 的历史对照
- 哪些支撑晚报复盘
- 哪些支撑 long report 的阶段性比较
- 哪些支持下一轮 focus 调整

否则 archive 仍然只是底层存储意图，不是产品资产。

### P5：把 LLM utility 从工具层接到“业务流水线样板”上

不是现在就做大全套，而是先做一个最小可用样板，例如：

- 一个 morning briefing sample flow
- 一个 evening long-report sample flow

要求是：

- 输入来自当前 focus families / macro / asset 等真实对象
- 输出遵循固定模板
- 能明确看到 business layer 到 report layer 的连接关系

这样才能验证 repo 现在这层设计到底够不够支撑产品。

---

## 9. 当前状态的务实判断

如果今天要对外或对内说一句最准确的话，我建议这样表述：

**ifa-business-layer 现在已经把默认 business 关注对象、归档目标和维护入口做成了可验证的控制层；但它还没有进入 iFA 2.0 的产品编排阶段，尤其还缺一主三辅的正式业务模型、早中晚节奏契约、briefing/long-report 输出模板，以及 US 股票业务对象层。**

这句话基本既不夸大，也不保守。

---

## 10. 这份基线所依据的 repo truth

本次判断主要基于以下真实文件/代码：

- `README.md`
- `docs/BUSINESS_LAYER_DESIGN.md`
- `docs/BUSINESS_LAYER_FOCUS_FAMILIES_V2.md`
- `docs/MIGRATION_BASELINE.md`
- `sql/001_business_layer_baseline.sql`
- `ifa_business_layer/defaults.py`
- `ifa_business_layer/schema.py`
- `ifa_business_layer/repository.py`
- `scripts/focus_cli.py`
- `scripts/ifa_llm_cli.py`
- `README_llm_utility.md`
- `docs/LLM_LIVE_VALIDATION_MATRIX.md`
- `tests/test_business_layer_phase1.py`
- `tests/unit/llm/*`
- `tests/integration/llm/test_llm_cli_smoke.py`

以及一次直接测试结果：

- `7 passed, 1 failed`
- 失败点：`tests/integration/llm/test_llm_cli_smoke.py`
- 失败原因：测试环境未注入 `PYTHONPATH`，先触发 `ModuleNotFoundError`，因此没有走到预期的 `JMR_API_KEY` 报错

---

## 11. 最后一段：给 Yunpeng 的业务判断

如果接下来是先做 business repo，而不是立刻开大 implementation batch，那么最正确的动作不是“继续加一些列表”，而是：

1. **先把产品结构写清楚**：一主三辅到底怎么落到 business object
2. **再把 cadence 写清楚**：早 / 中 / 晚分别消费什么对象、输出什么
3. **再把报告契约写清楚**：briefing 和 long report 具体结构是什么
4. **再补 US scope**：不然双市场只是目标，不是系统 reality
5. **最后才是把 LLM / report workflow 接上去**

也就是说：

**这个 repo 现在已经适合做“产品前的业务基线定稿”，但还不适合被误认为“iFA 2.0 business 产品已经成型”。**
