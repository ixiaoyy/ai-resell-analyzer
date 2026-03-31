# 技术栈 TECH_STACK

## 语言

- **Python 3.11+**：所有后端模块
- **HTML/JS**：Dashboard 前端（优先 Streamlit，复杂时升级 FastAPI + Vue）

## 核心依赖

| 用途 | 库 |
|------|----|
| 动态页面抓取 | `playwright` |
| HTTP 请求 | `requests` / `httpx` |
| 数据建模与验证 | `pydantic` |
| 本地存储 | `sqlite3`（标准库）/ JSON 文件 |
| AI 分析（可选）| `openai` / `anthropic` SDK |
| 看板 UI | `streamlit`（MVP）|
| 任务调度 | `apscheduler`（后期） |
| 测试 | `pytest` |
| 代码格式 | `ruff` |

## 数据存储策略

- MVP 阶段：本地 JSON 文件 + SQLite
- 生产阶段：按需升级为 PostgreSQL 或云存储
- 黑名单、利润记录：SQLite 持久化

## 反爬策略约定

- 代理池配置统一在 `scraper/config.py`，不允许散落各文件
- UA 列表统一维护，不允许硬编码单个 UA
- 请求延迟参数化，默认 2-5s 随机

## AI 调用约定

- 所有 LLM 调用统一通过 `analyzer/llm_client.py` 入口
- 禁止在业务逻辑中直接初始化 SDK 客户端
- API Key 通过环境变量注入，禁止写入代码或提交到仓库
- 调用失败必须有降级策略（回退到规则引擎）

## 环境管理

- Windows 本地开发建议显式使用 `py -3.12`，避免落到系统默认的 Python 2.7
- 使用 `venv` 或 `uv` 管理虚拟环境
- 依赖锁定：`requirements.txt`（精确版本）
- 环境变量：`.env` 文件（`.gitignore` 中排除）
- 若默认 PyPI 网络不稳定，可临时使用清华镜像：`py -3.12 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 不引入的技术（MVP 阶段）

- Docker（本地开发不需要）
- 消息队列（任务量不大）
- 向量数据库（暂不需要）
- 全自动上架 API（合规风险，人工节点优先）
