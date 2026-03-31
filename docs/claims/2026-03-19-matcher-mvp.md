# 模块认领说明

- 模块名：Matcher MVP - 1688 货源关键词匹配（T005）
- 负责人：AI Assistant
- 改动类型：功能 / 测试 / 文档
- 当前状态：in_progress

## 目标

本次准备完成 [`matcher/`](matcher/) 模块的最小可运行版本：读取符合 `AnalyzedProduct` 协议的输入 JSON，基于关键词构造候选货源匹配结果，计算利润估算，输出符合 `MatchedSupplier` 协议的结果文件。

## 计划修改范围

- 会新增或修改以下文件或目录：
- `matcher/`
- `tests/`
- `examples/`
- [`README.md`](README.md)
- `docs/changes/`
- `docs/claims/2026-03-19-matcher-mvp.md`

## 明确不改范围

- 不修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 不修改 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 的模块边界定义
- 不实现真实 1688 抓取、图片检索、代理池、登录态与反爬逻辑
- 不实现 [`scraper/`](scraper/)、[`copywriter/`](copywriter/)、[`dashboard/`](dashboard/) 业务逻辑

## 依据的协议文档

- [`README.md`](README.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- [`docs/AI参与开发协议.md`](docs/AI参与开发协议.md)
- [`docs/AI_SHARED_TASKLIST.md`](docs/AI_SHARED_TASKLIST.md)

## 预期产出

- Matcher MVP 代码
- 命令行入口
- 示例输入/输出数据
- 基础测试
- 一份变更说明文档

## 验证方式

- 运行单元测试
- 运行一次 Matcher CLI 烟雾测试
- 检查输出字段是否满足 `MatchedSupplier` 既有字段约束

## 风险与备注

- 当前仅实现本地规则匹配骨架与利润估算，不连接真实 1688 数据源
- 货源候选将通过关键词模板和启发式生成，后续可替换为真实搜索层实现
