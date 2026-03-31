# 模块认领说明

- 模块名：scraper
- 负责人：AI（Claude Sonnet 4.6）辅助，人工审核
- 改动类型：功能
- 当前状态：in_progress

## 目标

实现 scraper 模块 MVP：生成符合 `RawProduct` Schema 的静态模拟数据，跑通完整流水线链路。与 analyzer / matcher / copywriter MVP 保持一致策略——规则驱动，不做真实网络抓取。

## 计划修改范围

- 新建 `scraper/__main__.py`
- 新建 `tests/test_scraper.py`
- 新建 `docs/changes/2026-03-20-scraper-mvp.md`
- 新增示例输出数据 `data/raw/` 目录（运行时自动创建）

## 明确不改范围

- `docs/DATA_SCHEMA.md`（不变更 Schema）
- `analyzer/`、`matcher/`、`copywriter/`、`dashboard/` 任何文件
- `examples/raw_products.sample.json`（不修改现有样本）
- `README.md` 的项目状态标记（由人工确认后更新）

## 依据的协议文档

- README.md
- CONTRIBUTING.md
- docs/DATA_SCHEMA.md
- docs/ARCHITECTURE.md

## 预期产出

- `scraper/__main__.py`：`ProductScraper` 类，支持 `--platform`（xianyu/pinduoduo/all）、`--count`、`--output` 参数，输出标准 `RawProduct` JSON
- `tests/test_scraper.py`：覆盖字段完整性、平台枚举、数量参数、输出路径
- `docs/changes/2026-03-20-scraper-mvp.md`：变更说明

## 验证方式

- `python -m pytest tests/test_scraper.py`
- `python -m scraper --platform all --count 3 --output data/raw/test_output.json` smoke test
- 人工检查输出 JSON 是否符合 DATA_SCHEMA RawProduct 字段定义

## 风险与备注

- MVP 不做真实抓取（无 playwright/requests 依赖），与其他已完成 MVP 模式一致
- 真实抓取留给后续迭代
- 平台字段枚举严格遵守 `xianyu` / `pinduoduo`，不自创
