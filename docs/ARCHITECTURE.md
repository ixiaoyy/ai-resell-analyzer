# AI 选品助手 系统架构

## 总体结构

采用「五层流水线」架构，每层职责单一，人工决策节点明确：

```
[抓取层 Scraper]
      ↓
[分析层 Analyzer]
      ↓
[匹配层 Matcher]
      ↓
[文案层 Copywriter]
      ↓
[决策层 Dashboard]  ← 人工审核节点
```

## 模块划分

### 1. Scraper（抓取层）

职责：
- 抓取闲鱼「想要人数」、销量、价格、标题、图片
- 抓取拼多多热销榜商品数据
- 清洗原始数据，输出标准化 `RawProduct` 结构

技术选型：
- `playwright` 处理动态页面
- `requests` + 代理池处理静态接口
- 本地 JSON / SQLite 缓存原始数据

反爬策略：
- 随机 UA、延迟、Cookie 池
- 失败重试 + 降级到缓存

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
- 在 1688 搜索匹配货源
- 计算利润空间（到手价 - 1688货源价 - 运费 - 平台手续费）
- 过滤：无痕发货标识、商家信誉、起订量

输出：`MatchedSupplier` 结构，含利润估算

### 4. Copywriter（文案层）

职责：
- 基于商品特征生成闲鱼风格文案
- 支持多套文案模板（生活化、情感化、实用化）
- 输出标题 + 正文 + 关键词标签

策略：
- 模板引擎 + LLM 润色
- 禁止虚假宣传表述（见合规清单）

### 5. Dashboard（决策看板层）

职责：
- 展示候选商品列表（含热度、利润估算、文案草稿）
- 人工标记：通过 / 跳过 / 加入黑名单
- 维护商家黑名单、品类黑名单
- 统计已上架商品利润数据

技术选型：
- 轻量 Web UI（FastAPI + 简单前端，或 Streamlit）

## 数据流

```
1. Scraper 抓取原始数据 → data/raw/
2. Analyzer 分析 → data/analyzed/
3. Matcher 匹配货源 → data/matched/
4. Copywriter 生成文案 → data/copy/
5. Dashboard 展示候选 → 人工决策
6. 人工确认上架 → data/approved/
7. 结果反馈回分析模型（黑名单、利润记录）
```

## 目录结构

```
ai-picker/
├── scraper/          # 抓取模块
├── analyzer/         # 分析模块
├── matcher/          # 货源匹配模块
├── copywriter/       # 文案生成模块
├── dashboard/        # 决策看板
├── data/
│   ├── raw/          # 原始抓取数据
│   ├── analyzed/     # 分析结果
│   ├── matched/      # 货源匹配结果
│   ├── copy/         # 文案草稿
│   ├── approved/     # 已确认商品
│   └── blacklist/    # 黑名单数据
├── tests/            # 测试
├── docs/             # 文档
│   ├── changes/      # 每次 commit 说明
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
