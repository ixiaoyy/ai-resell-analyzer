# 模块认领说明

- 模块名：Copywriter MVP - 文案模板生成（T006）
- 负责人：AI Assistant
- 改动类型：功能 / 测试 / 文档
- 当前状态：in_progress

## 目标

本次准备完成 [`copywriter/`](copywriter/) 模块的最小可运行版本：读取符合 `AnalyzedProduct` 协议的输入 JSON，基于商品特征与趋势信号生成闲鱼风格标题、正文与标签，输出符合 `CopyDraft` 协议的结果文件。

## 计划修改范围

- 会新增或修改以下文件或目录：
- [`copywriter/`](copywriter/)
- [`tests/`](tests/)
- [`README.md`](README.md)
- [`docs/changes/`](docs/changes/)
- [`docs/claims/2026-03-19-copywriter-mvp.md`](docs/claims/2026-03-19-copywriter-mvp.md)

## 明确不改范围

- 不修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 不修改 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 的模块边界定义
- 不实现 LLM 调用、外部平台发布、自动上架与审核规避逻辑
- 不实现 [`scraper/`](scraper/)、[`matcher/`](matcher/)、[`dashboard/`](dashboard/) 业务逻辑

## 依据的协议文档

- [`README.md`](README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- [`docs/AI参与开发协议.md`](docs/AI参与开发协议.md)
- [`docs/AI_SHARED_TASKLIST.md`](docs/AI_SHARED_TASKLIST.md)

## 预期产出

- Copywriter MVP 代码
- 命令行入口
- 示例输出数据
- 基础测试
- 一份变更说明文档

## 验证方式

- 运行单元测试
- 运行一次 Copywriter CLI 烟雾测试
- 检查输出字段是否满足 `CopyDraft` 既有字段约束

## 风险与备注

- 当前仅实现基于规则的模板生成，不接入真实 LLM
- 文案风格以可验证、可重复为主，后续可替换为更丰富的模板与模型生成策略
