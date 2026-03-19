# Matcher MVP 变更说明

## 为什么改

在 [`analyzer/__main__.py`](analyzer/__main__.py) 已可输出 `AnalyzedProduct` 的基础上，需要继续打通任务 [`T005`](docs/AI_SHARED_TASKLIST.md) 的最小链路，提供一个本地可运行的 [`matcher/`](matcher/) MVP 骨架，用于验证关键词匹配、利润估算与 `MatchedSupplier` 输出流程。

## 改了什么

- 新增 [`matcher/__main__.py`](matcher/__main__.py)，提供 Matcher MVP 的命令行入口与本地规则匹配逻辑
- 新增 [`tests/test_matcher.py`](tests/test_matcher.py) 覆盖家居与数码类商品的匹配行为
- 新增认领文档 [`docs/claims/2026-03-19-matcher-mvp.md`](docs/claims/2026-03-19-matcher-mvp.md)
- 更新 [`README.md`](README.md) 的快速开始与项目状态，加入 Matcher 命令示例与测试命令

## 影响了哪些文件或模块

- [`matcher/`](matcher/)
- [`tests/test_matcher.py`](tests/test_matcher.py)
- [`README.md`](README.md)
- [`docs/claims/2026-03-19-matcher-mvp.md`](docs/claims/2026-03-19-matcher-mvp.md)

## 没改什么

- 未修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 未实现真实 1688 搜索、抓取、图搜、代理池、登录态与反爬逻辑
- 未实现 [`copywriter/`](copywriter/) 与 [`dashboard/`](dashboard/) 模块

## 是否涉及 Schema / 命名变更

- 不涉及 Schema 变更
- 不涉及全局命名变更

## 做了哪些验证

- 运行 [`python -m pytest tests/test_analyzer.py tests/test_matcher.py`](tests/test_matcher.py:1)，结果 `4 passed`
- 运行 [`python -m matcher --input data/analyzed/raw_products.sample_analyzed.json`](matcher/__main__.py:1)，成功生成 [`data/matched/raw_products.sample_analyzed_matched.json`](data/matched/raw_products.sample_analyzed_matched.json)

## 风险点

- 当前货源匹配为启发式本地生成，仅用于 MVP 骨架验证，不代表真实 1688 搜索结果
- 利润估算中的货源价、运费、起订量与评分为规则推断值，后续需要接入真实供应商数据进行替换与校准
