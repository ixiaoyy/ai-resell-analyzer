# AI 选品助手 系统架构

## 总体结构

采用“统一候选装配 + 多入口复用”的五层流水线架构。领域产物先沉淀为标准 Schema，再由统一装配层同时服务 CLI、API 与 Streamlit：

```
[抓取层 Scraper]
      ↓
[分析层 Analyzer]
      ↓
[匹配层 Matcher]
      ↓
[文案层 Copywriter]
      ↓
[装配层 app.pipeline]
      ├─→ [CLI Dashboard Aggregator]
      ├─→ [FastAPI app.main]
      └─→ [Streamlit dashboard.py]  ← 人工审核节点
```

## 模块划分

### 1. Scraper（抓取层）

职责：
- 抓取闲鱼「想要人数」与拼多多销量、价格、标题、图片等原始信号
- 统一输出标准化 `RawProduct` 结构
- 输出 `data_source` / `backend_used` / `source_detail` / `fetch_error_category` 等可观测性字段
- 在真实抓取不可用时回退到样本数据，保障链路可演示

技术选型：
- `playwright` 处理动态页面
- 文本解析后端与代理/浏览器后端组合降级
- 本地 JSON 缓存原始数据

当前实现特征：
- 支持 `auto` / `browser` / `proxy` / `text` 多后端模式
- 支持样本回退、来源标记、错误分类与抓取摘要输出
- 提供默认跳过的真实抓取 smoke test 入口，便于人工验证链路

### 2. Analyzer（分析层）

职责：
- 计算热度趋势（「想要」增速、销量曲线）
- 提取商品特征（品类、材质、颜色、风格关键词）
- 评估潜力评分 `product_score`
- 过滤已竞争饱和商品

策略：
- 第一版以规则引擎为主
- 可选 LLM 辅助语义分析
- 所有评分规则可追踪、可解释

### 3. Matcher（货源匹配层）

职责：
- 从 Analyzer 输出中提取搜索关键词
- 为候选商品匹配 1688 货源
- 计算利润空间（售价 - 货源价 - 运费 - 平台手续费）
- 结合黑名单、无痕发货、商家信誉、起订量做筛选

输出：`MatchedSupplier` 结构，含利润估算

### 4. Copywriter（文案层）

职责：
- 基于商品特征生成闲鱼风格文案
- 支持多套文案模板（生活化、情感化、实用化）
- 输出标题 + 正文 + 关键词标签

策略：
- 模板引擎 + LLM 润色
- 禁止虚假宣传表述（见合规清单）

### 5. Assembly + Dashboard（装配与决策层）

职责：
- 由 `app.pipeline` 统一装配 `CandidateBundle`
- 复用同一套候选数据到 FastAPI、Streamlit 与 CLI 聚合输出
- 展示候选商品列表（含热度、利润估算、文案草稿、AI 资产）
- 人工标记：通过 / 跳过 / 加入黑名单
- 维护商家黑名单、品类黑名单与利润记录

技术选型：
- `FastAPI` 提供候选列表、汇总与决策接口
- `Streamlit` 提供人工审核工作台
- `dashboard/__main__.py` 提供 JSON 聚合导出

## 数据流

```
1. Scraper 抓取原始数据 → data/raw/
2. Analyzer 分析 → data/analyzed/
3. Matcher 匹配货源 → data/matched/
4. Copywriter 生成文案 → data/copydrafts/
5. app.pipeline 统一装配候选 + AI 资产
6. Dashboard / API 读取候选 → 人工决策
7. 决策、黑名单、利润记录 → data/app.db
8. CLI 聚合输出 → data/dashboard/ 或 data/pipeline_run/
```

## 目录结构

```
ai-picker/
├── scraper/          # 抓取模块
├── analyzer/         # 分析模块
├── matcher/          # 货源匹配模块
├── copywriter/       # 文案生成模块
├── dashboard/        # CLI 聚合入口
├── app/              # 统一装配、API、AI 资产、存储层
├── data/
│   ├── raw/          # 原始抓取数据
│   ├── analyzed/     # 分析结果
│   ├── matched/      # 货源匹配结果
│   ├── copydrafts/   # 文案草稿
│   ├── dashboard/    # CLI 聚合输出
│   ├── pipeline_run/ # 一次完整流水线运行输出
│   └── app.db        # SQLite 决策、黑名单、利润记录
├── tests/            # 自动化测试
├── docs/             # 文档
│   ├── changes/      # 变更记录
│   └── claims/       # 模块认领说明
├── examples/         # 示例数据
├── README.md
└── CONTRIBUTING.md
```

## 设计原则

### 人工节点优先

全流程最终由人工在 Dashboard 确认，禁止全自动上架。

### Schema 优先

各层之间通过统一数据结构传递，不允许跨层直接读取原始数据。

### 小步闭环

MVP 阶段：每个模块先做最小可运行版本，跑通完整链路，再逐步增强。

### 可追踪性

每条商品决策（通过/跳过/黑名单）必须有记录，支持后续分析利润模型。
