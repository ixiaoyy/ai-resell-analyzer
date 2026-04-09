# 数据协议 DATA_SCHEMA v0.3

## 总览

各模块之间通过以下标准数据结构传递，禁止跨层直接消费原始数据。

---

## RawProduct（Scraper 输出）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 平台商品 ID |
| `platform` | enum | ✅ | `xianyu` / `pinduoduo` |
| `platform_code` | string | ❌ | 统一平台编码，默认与 `platform` 一致 |
| `platform_role` | string | ✅ | 平台角色，当前 demand/supply 使用 demand |
| `title` | string | ✅ | 原始标题 |
| `price` | float | ✅ | 售价（元） |
| `want_count` | int | ❌ | 闲鱼「想要人数」 |
| `sales_count` | int | ❌ | 销量（拼多多） |
| `image_url` | string | ❌ | 主图 URL |
| `category` | string | ❌ | 平台分类标签 |
| `fetched_at` | string | ✅ | ISO8601 抓取时间 |
| `raw_tags` | string[] | ❌ | 原始标签列表 |
| `data_source` | string | ✅ | 数据来源，如 `real` / `sample` / `dashboard` |
| `backend_used` | string | ❌ | 实际抓取或组装所用后端，如 `browser` / `proxy` / `text` / `sample` |
| `source_detail` | string | ❌ | 来源细节，如 `sample:all` 或具体抓取前缀/查询上下文 |
| `fetch_error_category` | string | ❌ | 抓取失败分类；真实抓取成功时为 `null`，样本回退时可记录如 `timeout` / `http_error` / `empty_result` |

---

## AnalyzedProduct（Analyzer 输出）

继承 `RawProduct` 所有字段，新增：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_score` | float | ✅ | 潜力评分 0-100 |
| `trend` | enum | ✅ | `rising` / `stable` / `declining` |
| `keywords` | string[] | ✅ | 提取的搜索关键词 |
| `category_label` | string | ✅ | 标准化品类标签 |
| `features` | object | ❌ | 商品特征（颜色/材质/风格） |
| `analyzed_at` | string | ✅ | ISO8601 分析时间 |
| `skip_reason` | string | ❌ | 被过滤时的原因 |

### features 结构

```json
{
  "color": "string | null",
  "material": "string | null",
  "style": "string | null"
}
```

### trend 枚举说明

| 值 | 含义 |
|----|------|
| `rising` | 热度上升，近期增速超阈值 |
| `stable` | 热度平稳 |
| `declining` | 热度下降 |

---

## MatchedSupplier（Matcher 输出）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_id` | string | ✅ | 关联 `AnalyzedProduct.id` |
| `supplier_id` | string | ✅ | 1688 商家 ID |
| `supplier_name` | string | ✅ | 商家名称 |
| `source_price` | float | ✅ | 1688 货源价（元） |
| `moq` | int | ✅ | 最小起订量 |
| `shipping_cost` | float | ✅ | 预估运费（元） |
| `profit_est` | float | ✅ | 预估利润 = 售价 - 货源价 - 运费 - 手续费 |
| `plain_package` | bool | ✅ | 是否支持无痕发货 |
| `supplier_rating` | float | ❌ | 商家评分 0-5 |
| `matched_at` | string | ✅ | ISO8601 匹配时间 |

---

## CopyDraft（Copywriter 输出）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_id` | string | ✅ | 关联商品 ID |
| `title` | string | ✅ | 文案标题（≤30字） |
| `body` | string | ✅ | 正文（闲鱼风格） |
| `tags` | string[] | ✅ | 关键词标签（≤5个） |
| `template_id` | string | ✅ | 使用的文案模板 ID |
| `generated_at` | string | ✅ | ISO8601 生成时间 |

---

## CandidateBundle（统一候选装配输出）

由 [`app/pipeline.py`](../app/pipeline.py) 统一装配，供 [`app/main.py`](../app/main.py)、[`dashboard.py`](../dashboard.py) 与 [`dashboard/__main__.py`](../dashboard/__main__.py) 复用。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product` | `AnalyzedProduct` | ✅ | 候选商品主体 |
| `supplier` | `MatchedSupplier \| null` | ❌ | 匹配到的货源 |
| `copy_draft` | `CopyDraft \| null` | ❌ | 文案草稿 |
| `decision` | `DecisionRecord \| null` | ❌ | 已保存的人工决策 |
| `ai_recommendation` | object \| null | ❌ | AI 平台建议与机会评分 |
| `listing_copy_asset` | object \| null | ❌ | AI 销售文案资产 |
| `image_asset` | object \| null | ❌ | AI 配图提示资产 |

---

## DecisionRecord（Dashboard 人工决策）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_id` | string | ✅ | 关联商品 ID |
| `decision` | enum | ✅ | `approved` / `skipped` / `blacklisted` |
| `reason` | string | ❌ | 决策备注 |
| `decided_by` | string | ✅ | 操作人 |
| `decided_at` | string | ✅ | ISO8601 决策时间 |

---

## 存储与输出目录约定

- [`data/raw/`](../data/raw/)：抓取阶段原始 JSON
- [`data/analyzed/`](../data/analyzed/)：分析结果 JSON
- [`data/matched/`](../data/matched/)：货源匹配结果 JSON
- [`data/copydrafts/`](../data/copydrafts/)：文案草稿 JSON
- [`data/dashboard/`](../data/dashboard/)：CLI 聚合后的 Dashboard JSON
- [`data/pipeline_run/`](../data/pipeline_run/)：单次完整流水线运行的阶段输出
- [`data/app.db`](../data/app.db)：SQLite 决策、黑名单、利润记录

---

## 协议变更规则

- 任何字段新增、删除、类型变更、枚举值变更均视为 Schema 变更
- Schema 变更必须：单独提 PR + 提前提交认领说明 + 更新本文档
- AI 不得擅自修改本文档
- 版本升级格式：`DATA_SCHEMA v0.x`，在文件头部更新版本号
- 当前版本补充了抓取可观测性字段、统一装配输出与目录口径说明
