# Copywriter MVP 变更说明

## 为什么改

在 [`analyzer/__main__.py`](analyzer/__main__.py) 已可输出 `AnalyzedProduct`、[`matcher/__main__.py`](matcher/__main__.py) 已可完成 `MatchedSupplier` MVP 的基础上，需要继续打通任务 [`T006`](docs/AI_SHARED_TASKLIST.md) 的最小链路，提供一个本地可运行的 [`copywriter/`](copywriter/) MVP 骨架，用于验证标题生成、正文模板与 `CopyDraft` 输出流程。

## 改了什么

- 新增 [`copywriter/__main__.py`](copywriter/__main__.py)，提供 Copywriter MVP 的命令行入口与本地模板生成逻辑
- 新增 [`tests/test_copywriter.py`](tests/test_copywriter.py) 覆盖上升趋势与低热度商品的文案生成行为
- 新增认领文档 [`docs/claims/2026-03-19-copywriter-mvp.md`](docs/claims/2026-03-19-copywriter-mvp.md)
- 后续将更新 [`README.md`](README.md) 的快速开始与项目状态，加入 Copywriter 命令示例与测试命令

## 影响了哪些文件或模块

- [`copywriter/`](copywriter/)
- [`tests/test_copywriter.py`](tests/test_copywriter.py)
- [`docs/claims/2026-03-19-copywriter-mvp.md`](docs/claims/2026-03-19-copywriter-mvp.md)
- [`docs/changes/2026-03-19-copywriter-mvp.md`](docs/changes/2026-03-19-copywriter-mvp.md)
- [`README.md`](README.md)

## 没改什么

- 未修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 未引入 LLM、外部发布平台或自动上架逻辑
- 未实现 [`scraper/`](scraper/)、[`dashboard/`](dashboard/) 模块

## 是否涉及 Schema / 命名变更

- 不涉及 Schema 变更
- 不涉及全局命名变更

## 做了哪些验证

- 已新增 [`tests/test_copywriter.py`](tests/test_copywriter.py) 用于验证 `CopyDraft` 关键字段
- 后续将运行 [`python -m pytest tests/test_analyzer.py tests/test_matcher.py tests/test_copywriter.py`](tests/test_copywriter.py:1)
- 后续将运行 [`python -m copywriter --input data/analyzed/raw_products.sample_analyzed.json`](copywriter/__main__.py:1)

## 风险点

- 当前文案为确定性模板生成，仅用于 MVP 骨架验证，不代表真实闲鱼发布效果
- 标题长度截断、标签提取与文风策略仍较简单，后续需要结合真实转化数据继续优化
