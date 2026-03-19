# 共享任务列表 AI_SHARED_TASKLIST

> 所有开发者和 AI 协作的任务统一在此登记。中高风险任务开工前必须先提交 `docs/claims/` 认领说明。

## 任务状态说明

| 状态 | 含义 |
|------|------|
| `todo` | 待认领 |
| `claimed` | 已认领，未开始 |
| `in_progress` | 开发中 |
| `review` | 待 Review |
| `done` | 已完成 |
| `blocked` | 阻塞中 |

## 风险等级说明

| 等级 | 含义 |
|------|------|
| A | 低风险，可直接开工 |
| B | 中风险，建议提认领说明 |
| C | 高风险，必须提认领说明 |

---

## MVP 阶段任务

### [T001] 项目规范与文档体系

- 风险：A
- 状态：`done`
- 产出：README / CONTRIBUTING / ARCHITECTURE / DATA_SCHEMA / AI参与开发协议 / TECH_STACK

---

### [T002] Scraper MVP - 闲鱼热销数据抓取

- 风险：B
- 状态：`todo`
- 目标：抓取闲鱼「想要人数」Top100 商品，输出标准 `RawProduct` JSON
- 认领说明：待提交
- 验证：输出文件通过 `RawProduct` schema 校验

---

### [T003] Scraper MVP - 拼多多热销数据抓取

- 风险：B
- 状态：`todo`
- 目标：抓取拼多多热销榜商品，输出标准 `RawProduct` JSON
- 认领说明：待提交
- 验证：输出文件通过 `RawProduct` schema 校验

---

### [T004] Analyzer MVP - 热度趋势规则引擎

- 风险：B
- 状态：`todo`
- 目标：基于规则计算 `product_score` 和 `trend`，输出 `AnalyzedProduct`
- 依赖：T002 或 T003 至少一个完成
- 认领说明：待提交
- 验证：规则可追踪，输出通过 schema 校验

---

### [T005] Matcher MVP - 1688 货源关键词匹配

- 风险：B
- 状态：`todo`
- 目标：基于关键词在 1688 搜索货源，计算利润估算，输出 `MatchedSupplier`
- 依赖：T004
- 认领说明：待提交
- 验证：利润计算公式正确，输出通过 schema 校验

---

### [T006] Copywriter MVP - 文案模板生成

- 风险：A
- 状态：`todo`
- 目标：基于商品特征生成闲鱼风格标题+正文，输出 `CopyDraft`
- 依赖：T004
- 验证：输出通过 schema 校验，模板覆盖至少 3 种风格

---

### [T007] Dashboard MVP - 人工决策看板

- 风险：B
- 状态：`todo`
- 目标：Streamlit 看板，展示候选商品，支持通过/跳过/加黑名单操作
- 依赖：T004 + T005 + T006
- 认领说明：待提交
- 验证：完整跑通 scraper → analyzer → matcher → copywriter → dashboard 链路

---

### [T008] 黑名单与利润记录持久化

- 风险：A
- 状态：`todo`
- 目标：SQLite 存储商家黑名单、品类黑名单、历史利润记录
- 依赖：T007
- 验证：黑名单过滤在 Matcher 中生效

---

## 后续阶段任务（暂缓）

- [ ] 自动调度（apscheduler 定时抓取）
- [ ] 利润模型优化（基于历史数据迭代评分规则）
- [ ] 1688 图片搜索匹配
- [ ] 多账号/多平台管理
