# A股早 / 中 / 晚数据消费合同（Phase 1 / v1）

## 1. 文档目的

这份文档定义 **A股一主三辅在早报 / 中报 / 晚报三个时段应如何消费当前系统已有数据层**。

它不是新的数据采集设计，也不是理想化未来架构，而是把当前已经确认的系统现实，正式收敛成一个 **可实现、可审计、可驱动后续 FSJ / 报告实现** 的消费合同。

本合同重点回答：

- 每个 slot 的主证据层是什么
- 次级 / fallback 证据层是什么
- 新鲜度（freshness）和完整性（completeness）最低要求是什么
- 数据不新鲜或不完整时必须如何降级
- 每个 slot 明确 **不能把什么当主证据**
- 主 Agent 与三个 support Agent 在消费方式上的差异是什么

---

## 2. 适用范围与依赖关系

本合同适用于：

- A股主 Agent 早报 / 中报 / 晚报
- 宏观 support Agent
- 商品 support Agent
- AI科技 support Agent
- 后续 FSJ 装配层
- 后续 report assembly / renderer

上游数据能力边界以 data repo 文档为准：

- `/Users/neoclaw/repos/ifa-data-platform/docs/A_SHARE_REPORT_DATA_CONSUMPTION_AND_EVIDENCE_BOUNDARY_V1.md`
- `/Users/neoclaw/repos/ifa-data-platform/docs/A_SHARE_REPORT_SLOT_DATA_CONTRACT_V1.md`

下游业务合同与 FSJ 文档：

- `/Users/neoclaw/repos/ifa-business-layer/docs/A_SHARE_MAIN_AGENT_DELIVERY_CONTRACT.md`
- `/Users/neoclaw/repos/ifa-business-layer/docs/A_SHARE_SUPPORT_AGENTS_DELIVERY_CONTRACT.md`
- `/Users/neoclaw/repos/ifa-business-layer/docs/A_SHARE_FSJ_AND_EVIDENCE_MAPPING_V1.md`

---

## 3. 统一术语

### 3.1 证据层分层

为便于实现，本合同统一把当前可消费输入分为五层：

1. **high**
   - 盘前竞价 / 盘中 working / event-stream / 盘中派生状态
   - 特点：快，但不稳定；适合早报 / 中报，不适合冒充 final truth

2. **mid**
   - same-day daily-final / post-close 稳定表
   - 特点：晚报主力层

3. **low**
   - 历史文本事实、公告、新闻、研报、问答、日历、稳定 reference objects
   - 特点：解释力和背景价值强，但很多不是 same-day intraday 结构的直接确认层

4. **archive**
   - `archive_v2` 已沉淀 nightly finalized facts
   - 特点：历史真相层、T-1 对照层，不是盘中 final 替身

5. **replay evidence**
   - slot replay / snapshot / 已冻结的 slot 输入证据包
   - 特点：用于复盘、回放、审计、一致性验证；不是默认实时主输入层，但可作为“本 slot 已冻结证据”的优先审计来源

### 3.2 主证据 vs 次证据

- **主证据层**：该 slot 默认应优先消费、用于支撑 section judgment 的层
- **次证据层**：用于补足解释、做交叉验证或在主层不完整时有限补位
- **禁止主用层**：可以存在，但不能作为该 slot 主结论的主证据

### 3.3 新鲜度标签

实现时至少统一出以下标签：

- `fresh`：在该 slot 允许窗口内
- `stale-soft`：略超窗口，允许降级后继续用
- `stale-hard`：超出 slot 可接受上限，不得再支撑主结论
- `unknown`：没有可靠时间戳，不得当主证据

---

## 4. 总体消费原则

### 4.1 早中晚的主次分工

- **早报**：以 `high + low + business seed` 建立可验证预案
- **中报**：以 `high` 验证、修正早报预案，并用 `T-1 mid/archive` 提供背景锚点
- **晚报**：以 `mid + low + T-1 archive` 形成日终主判断

### 4.2 archive 的正式定位

`archive_v2` 当前正式定位为：

- 历史 finalized truth
- T-1 / 多日对照基线
- replay / QA / 审计支撑层

明确不是：

- 早报盘前主证据
- 中报盘中主证据
- 晚报 same-day final 的替代物

### 4.3 replay evidence 的正式定位

`replay evidence` 当前正式定位为：

- 回放某个 slot 当时到底看到了什么
- 在报告 QA / 差异分析 / 用户追问时恢复“当时的证据面”
- 对主报告的一致性做审计

默认不是：

- 直接替代 live fetch 的实时主输入
- 在无 fresh live data 时自动伪装成实时证据

但如果进入 **slot freeze / replay mode**，则该 slot 已冻结证据可成为该次重放的主审计输入。

---

## 5. 时段合同总表

| Slot | 主 Agent 主证据层 | 主 Agent 次证据层 | support Agent 主证据偏好 | 禁止作为主证据的层 |
|---|---|---|---|---|
| early | high + low + reference seed | archive(T-1) / replay(last valid slot for audit only) | 宏观偏 low+archive；商品偏 high+low；AI偏 high+low | same-day archive / 仅 seed / 无时间戳 narrative |
| mid | high | T-1 mid / T-1 archive / low latest text | 宏观偏 low；商品偏 high；AI偏 high | T-1 archive 直接冒充盘中已确认结构 |
| late | mid + low | T-1 archive / same-day retained high 仅作补充 | 宏观偏 low+archive；商品偏 mid+low；AI偏 mid+high-retained | 仅凭 working highfreq / 仅凭 archive(T-1) 解释当天 |

---

## 6. Early（早报）数据消费合同

## 6.1 目标

早报的目标不是确认今天已经发生了什么，而是：

- 建立 **候选主线预案**
- 明确 **开盘验证点**
- 明确 **今日最值得盯的方向与失效条件**

因此，早报天然允许 evidence 强度低于晚报，但必须严格控制措辞强度。

## 6.2 主 Agent：早报主证据层

主 Agent 早报默认主证据层：

1. **high layer**
   - open auction / pre-open working snapshots
   - pre-open / overnight event stream
   - 可用的盘前高频派生状态

2. **low layer**
   - `trade_cal_history`
   - 近期 `announcements_history`
   - 近期 `news_history`
   - 近期 `research_reports_history`
   - 近期 `investor_qa_history`（若已可用）

3. **reference / seed**
   - key focus / focus families
   - business seed universe
   - canonical mapping / chain mapping

### 早报主结论允许的典型组合

- `high + seed`：今天优先验证什么主线
- `low + seed`：哪些方向盘前有信息催化，值得升格观察
- `high + low + seed`：某主题具备主线候选资格，但仍待开盘确认

## 6.3 主 Agent：早报次级 / fallback 层

允许作为次级 / fallback：

- **T-1 archive_v2**：
  - 用作昨日主线、昨日结构、跨日延续性的背景基线
  - 不能证明今天已经成立
- **上一有效 slot 的 replay evidence**：
  - 仅用于审计“我们此前看到了什么”
  - 不能自动替代今天盘前 live freshness

## 6.4 早报 freshness 要求

早报主证据 freshness 最低要求：

- 盘前 high layer：必须是 **当日盘前窗口** 内产生或更新
- 近期 low layer：必须能确认是 **仍对今日有效** 的最近信息，而不是陈旧背景
- seed/reference：可不追求当日更新时间，但必须是当前生效版本

实现口径建议：

- high layer 若无当日盘前时间戳 -> 视为 `stale-hard`
- low layer 若只是历史背景但未过期 -> 可作为 `fresh-reference`
- archive(T-1) 默认只能标记为 `historical-reference`

## 6.5 早报 completeness 要求

主 Agent 早报至少满足：

- 有 **1 条主预案 judgment**
- 有 **1 个开盘验证点**
- 有 **1 个失效条件**
- 主结论至少能回溯到：
  - 1 个 high / low 的当期事实锚点
  - 1 个 seed/reference 的观察对象锚点

如果只剩 watchlist 罗列，没有当期事实锚点，视为不完整。

## 6.6 早报 degrade 合同

出现以下情况时必须降级：

### 情况 A：盘前 high layer 不新鲜
- 禁止输出“今日主线大概率已确认”
- 降级为：候选主线 / 开盘观察项 / 风险提示

### 情况 B：low layer 有催化，但 market-side high evidence 缺失
- 允许写“事件驱动候选”
- 不允许写“市场已经选择该方向”

### 情况 C：只剩 seed/reference
- 只能输出 watchlist / 验证清单
- 不得输出正式 thesis judgment

## 6.7 早报明确禁止

早报不得把以下内容当主证据：

- **same-day archive_v2**（当前系统不应假定其存在并 finalized）
- **仅 T-1 archive** 用来证明“今天已成立”
- **仅 key focus / focus list** 用来证明“今天正在发生”
- **没有表级 / 对象级时间锚点的 narrative**

## 6.8 support Agent：早报消费差异

### 宏观 support
主用：`low + archive(T-1)`

- 更强调政策、利率、汇率、流动性、海外背景
- 可以比主 Agent 更依赖 finalized / historical 背景
- 不应假装自己能确认开盘后 A股结构已被验证

### 商品 support
主用：`high + low + reference`

- 盘前商品链条映射可以进入主证据
- 但若缺少 A股映射对象或链条 reference，只能做观察项

### AI科技 support
主用：`high + low`

- 更依赖题材热度、最新事件、龙头链条候选
- 盘前高频若不足，只能给“候选主线资格”，不能给“主线已成立”

---

## 7. Mid（中报）数据消费合同

## 7.1 目标

中报的目标是：

- 判断盘前预案是否被验证
- 判断结构是在强化、扩散、分歧还是转弱
- 为午后继续跟踪提供优先级

因此，中报的核心是 **working high layer 的结构判断**。

## 7.2 主 Agent：中报主证据层

主 Agent 中报默认主证据层：

1. **high layer**
   - `highfreq_stock_1m_working`
   - `highfreq_sector_breadth_working`
   - `highfreq_sector_heat_working`
   - `highfreq_leader_candidate_working`
   - `highfreq_intraday_signal_state_working`
   - `highfreq_event_stream_working`

这是当前系统下，中报唯一可以承担“盘中结构是否改变”的主证据层。

## 7.3 主 Agent：中报次级 / fallback 层

允许作为次级 / fallback：

- **T-1 mid daily-final / archive_v2**
  - 用来做昨日结构对照
  - 不可替代 same-day intraday 结构判断
- **low latest text**
  - 用来解释新事件、公告、消息面变化
  - 不能替代盘中 market-state
- **当前 slot replay evidence**（如果已冻结）
  - 用于审计/复现，不是默认 live 主输入替身

## 7.4 中报 freshness 要求

- high layer 必须是 **盘中窗口内可接受延迟** 的 working 数据
- 若 high 主表时间戳不可得、过老或明显断档，视为 `stale-hard`
- low latest text 若比盘中 market 变化慢，可作为辅助解释，但不能提高主结论力度

## 7.5 中报 completeness 要求

主 Agent 中报至少满足：

- 回答“盘前预案是否成立”
- 至少有 2 条盘中结构 facts
- 至少有 1 条盘中结构 signal
- 至少给出 1 个午后继续验证点

如果没有盘中结构事实，只靠盘前文字延续，视为不完整。

## 7.6 中报 degrade 合同

### 情况 A：高频主层轻微延迟（stale-soft）
- 可以保留“倾向 / 初步 / 盘中暂见”措辞
- 必须显式标注 freshness 风险

### 情况 B：高频主层明显断档（stale-hard）
- 禁止输出“强化 / 分歧 / 转强”这类强盘中结论
- 降级为：
  - 盘前预案跟踪中
  - 午后观察项
  - 当前证据不足，等待更新

### 情况 C：只剩 T-1 archive / low text
- 只能做背景提醒
- 不得装配成正式盘中主结论

## 7.7 中报明确禁止

中报不得把以下内容当主证据：

- **T-1 archive_v2** 直接当作今日盘中结构事实
- **低频文本事件** 直接当作盘面已验证
- **上一 slot replay** 冒充当前 live state
- **仅 leader/watchlist 名单** 推导整个盘中主线已成立

## 7.8 support Agent：中报消费差异

当前 Phase 1 不要求三个 support Agent 做完整独立中报，但若参与中报支撑，消费方式应不同：

### 宏观 support
- 只做背景是否变化的修正
- 主用 `low latest text + stable macro background`
- 不替主 Agent 做盘中结构判断

### 商品 support
- 可较多消费 `high`，尤其盘中商品链条变化
- 但必须通过 A股链条映射后再进入 support judgment

### AI科技 support
- 可较多消费 `high`，尤其题材热度、领涨候选、扩散状态
- 但若 breadth / leader / signal-state 不完整，应主动降级为“观察中”

---

## 8. Late（晚报）数据消费合同

## 8.1 目标

晚报的目标是：

- 形成当日可复盘主判断
- 给出结构归因
- 沉淀次日早报输入

因此，晚报必须从 `working-first` 切换到 `daily-final-first`。

## 8.2 主 Agent：晚报主证据层

主 Agent 晚报默认主证据层：

1. **mid layer / same-day daily-final**
   - `equity_daily_bar_history`
   - `etf_daily_bar_history`
   - `dragon_tiger_list_history`
   - `limit_up_detail_history`
   - `limit_up_down_status_history`
   - `sector_performance_history`
   - `northbound_flow_history`
   - 其他已验证可稳定用于盘后的 same-day stable tables

2. **low layer**
   - `announcements_history`
   - `news_history`
   - `research_reports_history`
   - `investor_qa_history`
   - 其他可追溯的盘后文本 / 事件事实

这两层共同构成晚报主证据核心。

## 8.3 主 Agent：晚报次级 / fallback 层

允许作为次级 / fallback：

- **T-1 archive_v2**
  - 用于跨日对照、延续性判断、历史定位
- **same-day retained high layer**
  - 可用于补充盘中演变细节
  - 不能替代 daily-final 做日终最终结构结论
- **late slot replay evidence**
  - 用于 QA / 审计 / 重放一致性

## 8.4 晚报 freshness 要求

- 主体表必须已进入 **盘后可稳定消费窗口**
- 如果 same-day daily-final 主表尚未 ready，必须降低报告完成等级
- low layer 的事件/文本事实应以当日收盘前后最近可追溯版本为准

## 8.5 晚报 completeness 要求

主 Agent 晚报至少满足：

- 有 1 条日终主 judgment
- 有 2 条以上结构 signal
- 有 3 条以上 facts，其中至少：
  - 1 条来自 same-day daily-final / stable market table
  - 1 条来自文本 / 事件 / 公告层或稳定背景层
- 有 1 条可沉淀到次日早报的 next-step / watch-item

如果 same-day stable market table 为空，原则上不能宣称“完整晚报”。

## 8.6 晚报 degrade 合同

### 情况 A：部分 daily-final 主表未 ready
- 降级为“晚间初版 / provisional close note”
- 明确列出缺失面
- 保留次日补完入口

### 情况 B：only low text + archive 对照存在
- 只允许写背景与解释框架
- 不允许写强日终结构结论

### 情况 C：same-day high 很丰富，但 mid stable 不足
- 可以描述盘中演变
- 不得把 high working 直接冒充日终 final structure

## 8.7 晚报明确禁止

晚报不得把以下内容当主证据：

- **仅 highfreq working** 直接推出日终正式结论
- **仅 T-1 archive_v2** 解释 same-day 结构
- **仅 narrative 文本** 替代 same-day market final facts

## 8.8 support Agent：晚报消费差异

### 宏观 support
主用：`low + archive(T-1)`

- 更适合回答“今天宏观到底是不是驱动 / 放大器 / 背景”
- 不需要自己重建股票结构层

### 商品 support
主用：`mid + low`，必要时辅 `same-day retained high`

- 应回答哪些商品链条真的解释了 A股相关方向
- 不应只凭隔夜商品变化解释全天 A股

### AI科技 support
主用：`mid + retained high + low`

- 晚报时可以更明确地区分主线 / 支线 / 噪音
- 但若 sector/breadth/final price support 不足，仍不得过满

---

## 9. FSJ 实现映射要求

为了驱动后续实现，slot 消费合同必须落到 FSJ 装配规则：

### Early
- Fact 允许来自 `high/low/seed`
- Signal 多为 `candidate / setup / precondition / risk`
- Judgment 多为 `watch_item / conditional thesis`

### Mid
- Fact 必须以 `high` 为主
- Signal 多为 `confirmation / divergence / weakening / strengthening`
- Judgment 多为 `intraday thesis / adjust / risk`

### Late
- Fact 必须以 `mid/low` 为主
- Signal 多为 `confirmed structure / attribution / continuation`
- Judgment 多为 `thesis / support / next_step`

---

## 10. 主 Agent 与 support Agent 的核心差异总结

### 10.1 主 Agent
- 负责形成全市场主判断
- 必须对“哪条主线最重要”做排序
- 对主结论的证据要求最高

### 10.2 support Agent
- 负责局部域内的专业 support / adjust / counter
- 可以更窄、更压缩、更偏专业证据
- 不承担全市场主线排序责任

### 10.3 实现差异要求

因此在同一 slot：

- **主 Agent** 必须先确认“是否足以形成主结论”
- **support Agent** 可以在更窄范围内给出局部 support，但仍要遵守自身域内 freshness / completeness 约束
- 不允许 support Agent 用更弱证据替代主 Agent 本应持有的主证据层

---

## 11. 可执行验收口径

后续实现只要满足以下检查项，就可判定符合本合同：

1. 每个 slot 的 section 都能标明 `source_layer`
2. 每个 judgment 都能说明使用的是主证据还是次证据
3. 当 freshness/completeness 不达标时，输出等级会自动降级
4. archive 与 replay 不会被误当成 same-day live final
5. support Agent 的输入消费路径与主 Agent 有明确差异，而不是简单共享一套无差别 prompt

---

## 12. 本阶段不承诺内容

本合同明确 **不承诺** 以下未来能力已经存在：

- 全量高成熟度盘中 support 自动流
- 全 slot 完整 freeze/replay 自动编排
- same-day archive_v2 作为晚报主证据
- 靠单一 narrative layer 自动生成高可信主结论

这份合同只约束 **当前真实可实现的消费方式**。
