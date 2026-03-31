# 模块认领说明

- 模块名：Analyzer MVP - 热度趋势规则引擎（T004）
- 负责人：AI Assistant
- 改动类型：功能 / 测试 / 文档
- 当前状态：in_progress

## 目标

本次准备完成 [`analyzer/`](analyzer/) 模块的最小可运行版本：读取符合 [`RawProduct`](docs/DATA_SCHEMA.md) 协议的输入 JSON，基于可追踪规则计算 `product_score`、`trend`、`keywords`、`category_label`、`features`、`analyzed_at`，并输出符合 [`AnalyzedProduct`](docs/DATA_SCHEMA.md) 协议的结果文件。

## 计划修改范围

- 会新增或修改以下文件或目录：
- `analyzer/`
- `tests/`
- `examples/`
- `requirements.txt`
- [`README.md`](README.md)
- `docs/changes/`
- `docs/claims/2026-03-19-analyzer-trend-rules.md`

## 明确不改范围

- 不修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 不修改 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 的模块边界定义
- 不实现 [`scraper/`](scraper/)、[`matcher/`](matcher/)、[`copywriter/`](copywriter/)、[`dashboard/`](dashboard/) 业务逻辑
- 不引入 LLM 调用与外部平台抓取逻辑

## 依据的协议文档

- [`README.md`](README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- [`docs/AI参与开发协议.md`](docs/AI参与开发协议.md)
- [`docs/AI_SHARED_TASKLIST.md`](docs/AI_SHARED_TASKLIST.md)

## 预期产出

- Analyzer MVP 代码
- 命令行入口
- 示例输入/输出数据
- 基础测试
- 一份变更说明文档

## 验证方式

- 运行单元测试
- 运行一次 Analyzer CLI 烟雾测试
- 检查输出字段是否满足 [`AnalyzedProduct`](docs/DATA_SCHEMA.md) 既有字段约束

## 风险与备注

- 当前仓库尚未存在 [`scraper/`](scraper/) 产物，本次将补充示例 [`RawProduct`](docs/DATA_SCHEMA.md) 数据用于本地验证
- 评分规则将采用可解释的启发式实现，后续可在不变更 Schema 的前提下迭代优化
