# AI 选品助手（ai-picker）

> 利用信息差 + AI 分析，从闲鱼/拼多多热销数据中识别潜力商品，在 1688 匹配低成本货源，辅助生成文案，支持人工决策倒卖链路。

## 项目定位

- **目标**：半自动化"抓取 → AI分析 → 货源匹配 → 文案生成"选品流程
- **阶段**：MVP 优先，人工决策为主，逐步模块化
- **原则**：AI 辅助，人工确认；小步迭代，不做全自动

## 核心模块

| 模块 | 职责 |
|------|------|
| `scraper/` | 抓取闲鱼/拼多多热销数据，支持多后端、来源标记、错误分类与样本回退 |
| `analyzer/` | 规则化分析热度趋势、商品特征与潜力评分 |
| `matcher/` | 1688 货源关键词匹配、利润估算与黑名单过滤 |
| `copywriter/` | 生成闲鱼风格文案草稿 |
| `dashboard/` | CLI 聚合输出与人工决策看板数据装配 |
| `app/` | 统一候选装配、API、AI 资产与存储层 |
| `data/` | 本地数据缓存、阶段产物与 SQLite 数据库 |

## 快速开始

```bash
# Windows 下建议显式使用 Python 3.12
py -3.12 -m pip install -r requirements.txt

# 若默认 PyPI 连接较慢，可切换清华镜像
py -3.12 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动当前 API 服务
py -3.12 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 健康检查
py -3.12 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"

# 启动 Streamlit 看板
py -3.12 -m streamlit run dashboard.py

# 使用示例数据运行完整流水线
py -3.12 run_pipeline.py --platform all --count 5

# 使用示例数据运行 Analyzer MVP
py -3.12 -m analyzer --input examples/raw_products.sample.json

# 基于 Analyzer 输出运行 Matcher MVP
py -3.12 -m matcher --input data/analyzed/raw_products.sample_analyzed.json

# 基于 Analyzer 输出运行 Copywriter MVP
py -3.12 -m copywriter --input data/analyzed/raw_products.sample_analyzed.json

# 聚合 Analyzer / Matcher / Copywriter 输出，生成 Dashboard 审核数据
py -3.12 -m dashboard --analyzed data/analyzed/raw_products.sample_analyzed.json --matched data/matched/raw_products.sample_analyzed_matched.json --copydrafts data/copydrafts/raw_products.sample_analyzed_copydrafts.json

# 真实抓取 smoke test（默认跳过，需显式开启）
set RUN_REAL_SCRAPER_SMOKE=1 && python -m pytest tests/test_scraper_smoke.py -q
```

## 文档索引

- [系统架构](docs/ARCHITECTURE.md)
- [技术栈](docs/TECH_STACK.md)
- [数据协议](docs/DATA_SCHEMA.md)
- [AI 参与开发协议](docs/AI参与开发协议.md)
- [贡献指南](CONTRIBUTING.md)

## 项目状态

- [x] 项目规范与文档体系
- [x] scraper 模块 MVP
- [x] analyzer 模块 MVP
- [x] matcher 模块 MVP
- [x] copywriter 模块 MVP
- [x] dashboard 看板 MVP
- [x] SQLite 决策 / 黑名单 / 利润记录持久化
- [x] FastAPI 候选列表 / 汇总 / 决策接口
- [x] CLI / API / Dashboard 共用统一候选装配逻辑
- [x] Scraper 来源标记、错误分类、统计摘要与 smoke test 入口
