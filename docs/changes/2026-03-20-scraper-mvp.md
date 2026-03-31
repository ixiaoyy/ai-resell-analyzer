# 变更说明：scraper 模块 MVP

## 为什么改

scraper 是流水线第一层，其他模块（analyzer、matcher、copywriter、dashboard）均已完成 MVP，唯独 scraper 缺失，导致项目链路不完整。本次实现最小可运行版本，补齐流水线入口。

## 改了什么

- 新建 `scraper/__main__.py`：实现 `ProductScraper` 类，支持 `--platform`（xianyu / pinduoduo / all）、`--count`、`--output` 参数，输出符合 `DATA_SCHEMA RawProduct` 定义的 JSON 文件
- 新建 `tests/test_scraper.py`：8 个测试用例，覆盖字段完整性、平台过滤、数量限制、参数校验、Schema 合规
- 新建 `docs/claims/2026-03-20-scraper-mvp.md`：开工前认领说明
- 新建 `docs/changes/2026-03-20-scraper-mvp.md`：本文件

## 影响了哪些文件或模块

- `scraper/`（新增）
- `tests/test_scraper.py`（新增）
- `docs/claims/`、`docs/changes/`（新增文档）

## 没改什么

- `docs/DATA_SCHEMA.md`（Schema 未变更）
- `analyzer/`、`matcher/`、`copywriter/`、`dashboard/`（其他模块未触碰）
- `examples/raw_products.sample.json`（现有样本数据未修改）
- `README.md`（状态标记由人工确认后更新）
- `requirements.txt`（MVP 无新依赖，仅用标准库）

## 是否涉及 Schema / 命名变更

否。输出字段严格遵守 `DATA_SCHEMA.md` 中 `RawProduct` 定义，未新增、删除或修改任何字段。

## 做了哪些验证

- `python -m pytest tests/test_scraper.py` 全部通过
- `python -m scraper --platform all --count 3` smoke test，输出 JSON 人工检查符合 Schema

## 风险点

- MVP 使用静态 mock 数据，不做真实网络抓取（与其他模块 MVP 策略一致）
- 真实抓取（playwright / requests / 代理池）留给后续迭代
- mock 数据 ID 与 `examples/raw_products.sample.json` 不重叠（样本用 xy-1xxx/pdd-2xxx，本模块用 xy-3xxx/pdd-4xxx）
