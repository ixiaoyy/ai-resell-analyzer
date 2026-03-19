# AI 选品助手（ai-picker）

> 利用信息差 + AI 分析，从闲鱼/拼多多热销数据中识别潜力商品，在 1688 匹配低成本货源，辅助生成文案，支持人工决策倒卖链路。

## 项目定位

- **目标**：半自动化"抓取 → AI分析 → 货源匹配 → 文案生成"选品流程
- **阶段**：MVP 优先，人工决策为主，逐步模块化
- **原则**：AI 辅助，人工确认；小步迭代，不做全自动

## 核心模块

| 模块 | 职责 |
|------|------|
| `scraper/` | 抓取闲鱼/拼多多热销数据 |
| `analyzer/` | AI 分析热度趋势、商品特征 |
| `matcher/` | 1688 货源关键词/图文匹配与比价 |
| `copywriter/` | 生成闲鱼风格文案 |
| `dashboard/` | 人工决策看板（Web UI） |
| `data/` | 本地数据缓存与商品库 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 抓取热销数据（示例）
python -m scraper --platform xianyu --limit 100

# 分析并匹配货源
python -m analyzer --input data/raw/xianyu_latest.json

# 启动决策看板
python -m dashboard
```

## 文档索引

- [系统架构](docs/ARCHITECTURE.md)
- [技术栈](docs/TECH_STACK.md)
- [数据协议](docs/DATA_SCHEMA.md)
- [AI 参与开发协议](docs/AI参与开发协议.md)
- [贡献指南](CONTRIBUTING.md)

## 项目状态

- [x] 项目规范与文档体系
- [ ] scraper 模块 MVP
- [ ] analyzer 模块 MVP
- [ ] matcher 模块 MVP
- [ ] copywriter 模块 MVP
- [ ] dashboard 看板 MVP
