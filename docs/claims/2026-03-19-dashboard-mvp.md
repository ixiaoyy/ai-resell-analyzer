# 模块认领说明

- 模块名：Dashboard MVP - 人工决策看板（T007）
- 负责人：AI Assistant
- 改动类型：功能 / 测试 / 文档
- 当前状态：in_progress

## 目标

本次准备完成 [`dashboard/`](dashboard/) 模块的最小可运行版本：聚合符合 `AnalyzedProduct`、`MatchedSupplier` 与 `CopyDraft` 协议的输入 JSON，生成用于人工审核的候选列表，并附带 `DecisionRecord` 所需的决策字段骨架。

## 计划修改范围

- 会新增或修改以下文件或目录：
- [`dashboard/`](dashboard/)
- [`tests/`](tests/)
- [`README.md`](README.md)
- [`docs/changes/`](docs/changes/)
- [`docs/claims/2026-03-19-dashboard-mvp.md`](docs/claims/2026-03-19-dashboard-mvp.md)

## 明确不改范围

- 不修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 不修改 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 的模块边界定义
- 不实现真实 Web UI、数据库持久化、黑名单存储与权限系统
- 不实现 [`scraper/`](scraper/) 业务逻辑

## 依据的协议文档

- [`README.md`](README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- [`docs/AI参与开发协议.md`](docs/AI参与开发协议.md)
- [`docs/AI_SHARED_TASKLIST.md`](docs/AI_SHARED_TASKLIST.md)

## 预期产出

- Dashboard MVP 聚合代码
- 命令行入口
- 基础测试
- 一份变更说明文档

## 验证方式

- 运行单元测试
- 运行一次 Dashboard CLI 烟雾测试
- 检查输出是否包含人工决策所需字段骨架

## 风险与备注

- 当前仅实现 JSON 聚合层，不提供真实 Streamlit 或 FastAPI 页面
- 当前输出为 `DecisionRecord`-ready 的审核行，不直接写入正式 `DecisionRecord` 结果文件
