# Analyzer MVP 变更说明

## 为什么改

项目当前仅有协议与架构文档，缺少首个可运行代码模块。根据任务 [`T004`](docs/AI_SHARED_TASKLIST.md) 需要先落地一个最小版 [`analyzer/`](analyzer/) 规则引擎，验证从 [`RawProduct`](docs/DATA_SCHEMA.md) 到 `AnalyzedProduct` 的分析链路。

## 改了什么

- 新增 [`analyzer/__main__.py`](analyzer/__main__.py)，提供 Analyzer MVP 的命令行入口与规则分析逻辑
- 新增 [`examples/raw_products.sample.json`](examples/raw_products.sample.json) 作为本地烟雾测试输入样例
- 新增 [`tests/test_analyzer.py`](tests/test_analyzer.py) 覆盖高热度与低信号商品的基础行为
- 新增 [`requirements.txt`](requirements.txt) 记录当前测试依赖
- 新增认领文档 [`docs/claims/2026-03-19-analyzer-trend-rules.md`](docs/claims/2026-03-19-analyzer-trend-rules.md)

## 影响了哪些文件或模块

- [`analyzer/`](analyzer/)
- [`tests/`](tests/)
- [`examples/`](examples/)
- [`requirements.txt`](requirements.txt)
- [`docs/claims/`](docs/claims/)

## 没改什么

- 未修改 [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)
- 未实现 [`scraper/`](scraper/)、[`matcher/`](matcher/)、[`copywriter/`](copywriter/)、[`dashboard/`](dashboard/) 模块
- 未引入 LLM、数据库、外部抓取或 Web UI

## 是否涉及 Schema / 命名变更

- 不涉及 Schema 变更
- 不涉及全局命名变更

## 做了哪些验证

- 运行 [`python -m pytest tests/test_analyzer.py`](tests/test_analyzer.py:1)，结果 `2 passed`

## 风险点

- 当前评分与分类逻辑为启发式规则，仅用于 MVP 验证
- 类别与特征提取基于关键词，后续需要结合真实抓取样本进一步校准
