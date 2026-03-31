# Dashboard MVP 变更说明

## 为什么改

在 [`analyzer/__main__.py`](analyzer/__main__.py)、[`matcher/__main__.py`](matcher/__main__.py) 与 [`copywriter/__main__.py`](copywriter/__main__.py) 已可分别产出 `AnalyzedProduct`、`MatchedSupplier` 与 `CopyDraft` 的基础上，需要继续打通任务 [`T007`](docs/AI_SHARED_TASKLIST.md) 的最小链路，提供一个本地可运行的 [`dashboard/`](dashboard/) MVP 聚合骨架，用于验证候选商品汇总、审核优先级判断与 `DecisionRecord`-ready 输出流程。

## 改了什么

- 新增 [`dashboard/__main__.py`](dashboard/__main__.py)，提供 Dashboard MVP 的命令行入口与本地聚合逻辑
- 新增 [`tests/test_dashboard.py`](tests/test_dashboard.py) 覆盖候选行生成与缺失依赖时报错行为
- 新增认领文档 [`docs/claims/2026-03-19-dashboard-mvp.md`](docs/claims/2026-03-19-dashboard-mvp.md)
- 后续将更新 [`README.md`](README.md) 的快速开始与项目状态，加入 Dashboard 命令示例与测试命令

## 影响了哪些文件或模块

- [`dashboard/`](dashboard/)
- [`tests/test_dashboard.py`](tests/test_dashboard.py)
- [`docs/claims/2026-03-19-dashboard-mvp.md`](docs/claims/2026-03-19-dashboard-mvp.md)
- [`docs/changes/2026-03-19-dashboard-mvp.md`](docs/changes/2026-03-19-dashboard-mvp.md)
- [`README.md`](README.md)

## 没改什么

- 未修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 未引入真实 Streamlit / FastAPI Web UI
- 未实现数据库持久化、黑名单管理与正式 `DecisionRecord` 落库

## 是否涉及 Schema / 命名变更

- 不涉及 Schema 变更
- 不涉及全局命名变更

## 做了哪些验证

- 已新增 [`tests/test_dashboard.py`](tests/test_dashboard.py) 用于验证 Dashboard 聚合输出
- 后续将运行 [`python -m pytest tests/test_analyzer.py tests/test_matcher.py tests/test_copywriter.py tests/test_dashboard.py`](tests/test_dashboard.py:1)
- 后续将运行 [`python -m dashboard --analyzed data/analyzed/raw_products.sample_analyzed.json --matched data/matched/raw_products.sample_analyzed_matched.json --copydrafts data/copydrafts/raw_products.sample_analyzed_copydrafts.json`](dashboard/__main__.py:157)

## 风险点

- 当前 Dashboard 仅为 JSON 聚合层，不包含真实人工操作页面
- 当前推荐优先级与审核建议为启发式规则，后续需要结合真实人工决策数据继续优化
