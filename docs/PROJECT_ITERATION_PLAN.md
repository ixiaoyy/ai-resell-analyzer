# 项目开发计划 PROJECT_ITERATION_PLAN

> 基于当前代码与测试现状整理，目标是把项目从“样本驱动 MVP”推进到“真实可用的人工选品作业台 v1”。

## 1. 计划背景

当前项目已经具备以下基础能力：

- 已有完整链路：抓取 → 分析 → 匹配 → 文案 → 看板聚合
- 已有 API 服务与 Streamlit 看板
- 已有 SQLite 决策、黑名单、利润记录
- 已有基础自动化测试，当前测试结果为 `44 passed`

当前项目的真实定位应定义为：

**可本地运行、可人工审核、可演示完整链路的 MVP；但尚未达到稳定生产化选品系统标准。**

---

## 2. 当前现状判断

### 2.1 已真实可用能力

1. [`run_pipeline.py`](../run_pipeline.py) 可完成一次性端到端流水线执行。
2. [`app/main.py`](../app/main.py) 已提供候选列表、摘要、决策保存 API。
3. [`dashboard.py`](../dashboard.py) 已支持筛选、人工审核、写入决策。
4. [`app/storage.py`](../app/storage.py) 已支持 SQLite 持久化。
5. [`tests/`](../tests/) 已覆盖主要 MVP 路径，当前可稳定通过。

### 2.2 当前真实边界

1. 抓取层虽然具备多后端与样本回退机制，但仍未证明真实抓取长期稳定。
2. Analyzer / Matcher / Copywriter 目前主要依赖规则，不具备基于经营反馈的自动优化能力。
3. CLI 聚合看板与 Web/API 看板存在两套装配逻辑，后续维护容易分叉。
4. 决策记录已经落地，但经营反馈链路还不完整。

---

## 3. 当前主要问题

### 3.1 P0：必须优先处理

#### A. 文档与代码现状不一致

- [`README.md`](../README.md) 中 [`scraper/`](../scraper/) 状态仍显示未完成，但实际已有 MVP 实现。
- [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md) 中目录和数据流与代码现状不完全一致。
- [`docs/DATA_SCHEMA.md`](./DATA_SCHEMA.md) 与部分运行实现存在维护分离风险。

#### B. 入口与输出口径不统一

- [`dashboard/__main__.py`](./../dashboard/__main__.py) 用于聚合 JSON 输出。
- [`app/pipeline.py`](../app/pipeline.py) 用于 API / Streamlit 候选装配。
- 两套口径并存，后续需求改动可能出现行为不一致。

#### C. 抓取层可运营性不足

- 缺少真实抓取成功率、失败原因、后端命中情况统计。
- 样本回退虽可用，但缺少显式来源标记。

### 3.2 P1：中优先级问题

#### D. Schema 存在命名冲突告警

- [`CandidateBundle`](../app/schemas.py) 中字段 `copy` 触发 Pydantic warning，存在未来升级风险。

#### E. 规则硬编码较多

- Analyzer、Matcher、Copywriter 关键规则目前直接写在代码中。
- 调参必须改代码，不利于后续业务试错。

#### F. 缺少经营反馈回流

- 当前仅有审核结论。
- 缺少真实成交、退款、复购、售后等后效数据。

### 3.3 P2：后续持续补强

#### G. 测试覆盖仍偏 MVP

虽然 [`tests/test_pipeline.py`](../tests/test_pipeline.py)、[`tests/test_scraper.py`](../tests/test_scraper.py) 等已经覆盖主流程，但仍缺少：

- API 集成测试
- SQLite 存储回归测试
- Dashboard 行为回归测试
- 真实抓取 smoke test

---

## 4. 总体开发目标

下一阶段建议目标：

**从“能跑通的样本 MVP”升级为“可维护、可追踪、可持续迭代的人工选品作业台”。**

具体要求：

- 有统一主流程
- 有统一数据口径
- 有稳定的人工审核闭环
- 有可追踪的抓取来源与规则版本
- 有经营数据回流基础

---

## 5. 迭代路线图

## Phase 1：统一口径与基础稳定性

### 目标

把当前 MVP 从“能运行”提升到“能维护”。

### 任务

1. 统一主流程装配逻辑
   - 让 CLI、API、Dashboard 共用同一套领域装配逻辑
   - 收敛 [`app/pipeline.py`](../app/pipeline.py) 与 [`dashboard/__main__.py`](../dashboard/__main__.py) 的重复职责

2. 统一目录与输出命名
   - 明确 [`data/raw/`](../data/raw/)、[`data/analyzed/`](../data/analyzed/)、[`data/matched/`](../data/matched/)、[`data/copydrafts/`](../data/copydrafts/)、[`data/dashboard/`](../data/dashboard/) 的标准用途
   - 清理代码与文档中的旧路径表述

3. 修正文档偏差
   - 更新 [`README.md`](../README.md)
   - 更新 [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md)
   - 更新 [`docs/DATA_SCHEMA.md`](./DATA_SCHEMA.md)
   - 必要时补充开发规范说明

4. 处理 schema warning
   - 修复 [`app/schemas.py`](../app/schemas.py) 中 `copy` 字段命名冲突问题

5. 补齐基础测试
   - 为 [`app/storage.py`](../app/storage.py) 增加测试
   - 为 [`app/main.py`](../app/main.py) 增加 API 测试

### 验收标准

- CLI / API / Dashboard 使用一致的数据装配口径
- 文档与代码目录一致
- 无已知 schema warning
- 测试覆盖存储与 API 基础流程

---

## Phase 2：增强 Scraper 可观测性

### 目标

让抓取层从“有实现”升级为“可监控、可回退、可分析”。

### 任务

1. 增加抓取来源标记
   - 区分 browser / proxy / text / sample

2. 统一抓取错误分类
   - 区分超时、解析失败、页面结构异常、无结果、代理失败

3. 增加抓取日志和统计
   - 成功数
   - 失败数
   - 回退次数
   - 各后端命中情况

4. 增加缓存策略说明
   - 明确何时读缓存、何时强制刷新

5. 增加真实抓取 smoke test
   - 默认不阻塞本地测试
   - 用于人工验证真实抓取链路

### 验收标准

- 能区分真实数据与样本数据
- 能分析抓取失败原因
- 能统计各抓取后端表现

---

## Phase 3：规则系统配置化

### 目标

降低调参成本，提高规则可追踪性。

### 任务

1. 抽离 Analyzer 规则配置
   - 如品类映射、关键词、评分参数

2. 抽离 Matcher 规则配置
   - 如利润率、运费、平台费率、起订量策略

3. 抽离 Copywriter 规则配置
   - 如标题前缀、模板文案、标签生成策略

4. 增加规则版本号
   - 输出结果附带规则版本信息

5. 增加规则回归样本
   - 防止调参破坏现有结果

### 验收标准

- 常见调优不需要直接改 Python 代码
- 每次结果都能追溯规则版本

---

## Phase 4：完善审核闭环与经营反馈

### 目标

让看板从展示工具升级为实际作业台。

### 任务

1. 扩展决策记录
   - 审核人
   - 渠道
   - 上架状态
   - 二次复核状态

2. 扩展利润记录
   - 预估利润
   - 真实利润
   - 成交时间

3. 增加经营反馈字段
   - 成交价
   - 退款情况
   - 售后备注
   - 是否复购

4. 增加历史视图
   - 已审核列表
   - 黑名单管理
   - 利润统计

5. 补历史查询接口
   - 为看板统计和复盘提供支撑

### 验收标准

- 单个商品从候选到审核到后效可追踪
- 可以基于历史数据复盘规则有效性

---

## Phase 5：形成数据驱动优化闭环

### 目标

从“规则可运行”升级为“规则可持续优化”。

### 任务

1. 将审核结果回流 Analyzer
2. 将真实利润与经营结果回流评分模型
3. 建立高通过率、高利润、低退款统计视图
4. 逐步引入可选 LLM 增强，而不是主流程依赖
5. 建立规则版本对比机制

### 验收标准

- 每次规则升级都有数据依据
- 项目具备持续优化能力

---

## 6. 优先级安排

### 本周必须完成

1. 统一主流程装配逻辑
2. 修正文档偏差
3. 补齐存储/API 测试
4. 修复 schema warning

### 下一阶段优先完成

5. 增强抓取可观测性
6. 为抓取结果增加来源标记
7. 统一抓取失败分类

### 中期推进

8. 规则配置化
9. Dashboard 历史审核能力
10. 经营反馈回流

---

## 7. 与现有任务列表的关系

当前 [`docs/AI_SHARED_TASKLIST.md`](./AI_SHARED_TASKLIST.md) 主要记录 MVP 初始任务，已经不完全反映当前项目状态。

建议后续将本计划拆分为新的阶段任务，例如：

- T101：统一主流程与输出口径
- T102：修正文档与目录规范
- T103：补存储与 API 测试
- T104：修复 schema warning
- T105：增强 Scraper 可观测性
- T106：规则配置化
- T107：审核闭环与经营反馈升级

---

## 8. 实现检查清单

- [ ] 明确唯一主入口与领域装配边界
- [ ] 统一数据输出目录与命名规则
- [ ] 同步修正 [`README.md`](../README.md)
- [ ] 同步修正 [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md)
- [ ] 同步修正 [`docs/DATA_SCHEMA.md`](./DATA_SCHEMA.md)
- [ ] 为 [`app/storage.py`](../app/storage.py) 增加测试
- [ ] 为 [`app/main.py`](../app/main.py) 增加 API 测试
- [ ] 修复 [`app/schemas.py`](../app/schemas.py) 中命名冲突告警
- [ ] 为抓取增加来源标记、日志、错误分类
- [ ] 抽离 Analyzer / Matcher / Copywriter 规则配置
- [ ] 补充 Dashboard 历史复盘能力

---

## 9. 结论

当前项目已经具备继续产品化的基础。最现实的下一步不是盲目增加更复杂 AI，而是先把主流程、文档口径、抓取可观测性、人工审核闭环做扎实。完成这些以后，再进入规则配置化和经营数据回流，才能让项目从 demo 走向真实可用。