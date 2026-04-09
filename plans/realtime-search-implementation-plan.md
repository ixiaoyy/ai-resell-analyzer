# 实施清单与验收标准规划

## 1. 目标

在不破坏当前 [`dashboard.py`](../dashboard.py) 审核能力与 [`app/main.py`](../app/main.py) 既有 API 的前提下，分阶段落地“平台关键词搜索 -> 实时抓取 -> 跨平台比价 -> AI 建议 -> 转入审核池”能力。

本规划与以下文档配套：

- 领域模型与数据流：[`plans/realtime-search-domain-plan.md`](./realtime-search-domain-plan.md)
- API 与任务生命周期：[`plans/realtime-search-api-plan.md`](./realtime-search-api-plan.md)
- Dashboard 交互方案：[`plans/realtime-search-dashboard-plan.md`](./realtime-search-dashboard-plan.md)
- 共享任务登记：[`docs/AI_SHARED_TASKLIST.md`](../docs/AI_SHARED_TASKLIST.md)

---

## 2. 分阶段实施策略

建议严格按以下顺序实施：

### Phase A - T009 最小闭环：平台关键词搜索与实时抓取入口

目标：先把当前“静态候选审核页”升级为“可输入关键词并看到抓取结果”的工作台。

范围：
- 在 [`app/schemas.py`](../app/schemas.py) 增加搜索域基础模型
- 在 `app` 层增加轻量搜索任务仓库与任务服务
- 在 [`app/main.py`](../app/main.py) 增加搜索任务 API
- 在 [`dashboard.py`](../dashboard.py) 增加搜索表单、任务状态栏、原始命中结果表、命中详情面板
- 继续保留 [`CandidateBundle`](../app/schemas.py:148) 审核模式

本阶段不做：
- 不做复杂同款归并
- 不做跨平台比价主表
- 不做 AI 建议生成
- 不做候选池转入

### Phase B - T010：跨平台比价工作台

目标：把多平台抓取结果聚合成同款比价视图。

范围：
- 增加归一化标题和轻量归并规则
- 输出 [`ComparisonGroup`](./realtime-search-domain-plan.md)
- 在 [`app/main.py`](../app/main.py) 增加 `/comparisons` 接口
- 在 [`dashboard.py`](../dashboard.py) 增加比价表、差价排序、最高/最低价详情

本阶段不做：
- 不做复杂 AI 模型
- 不做视觉同款识别

### Phase C - T011：搜索结果转候选池

目标：把搜索比价工作台与现有审核闭环打通。

范围：
- 定义 [`CandidateDraft`](./realtime-search-domain-plan.md)
- 设计比价结果到 [`CandidateBundle`](../app/schemas.py:148) 的映射
- 在 [`app/main.py`](../app/main.py) 增加 promote 接口
- 在 [`dashboard.py`](../dashboard.py) 增加“转入审核池”入口

### Phase D - T012：AI 辅助建议

目标：在比价结果基础上输出定价、营销语、图片建议。

范围：
- 在 [`app/ai.py`](../app/ai.py) 新增基于比价组的建议生成器
- 在 API 暴露 `/insights`
- 在工作台展示：
  - 建议售价区间
  - 营销语方向
  - 图片优化建议
  - 风险提示

优先级说明：
- AI 能力后置
- 必须在搜索与比价稳定后再接入

---

## 3. 第一阶段 T009 详细实施清单

## 3.1 后端模型层

需要新增：
- `SearchRequest`
- `SearchSession`
- `SearchHit`
- `SearchSummary`
- `SearchTaskStatus` 或等价状态枚举

落点建议：
- [`app/schemas.py`](../app/schemas.py)

验收标准：
- [ ] 新模型可通过 Pydantic 校验
- [ ] 搜索请求、状态对象、命中对象字段完整
- [ ] 保留与 [`RawProduct`](../app/schemas.py:39) 的兼容关系

## 3.2 搜索任务服务层

需要新增：
- 内存任务仓库
- 任务创建函数
- 任务查询函数
- 结果缓存函数
- 抓取摘要生成函数

推荐新文件：
- `app/search_store.py`
- `app/search_service.py`

验收标准：
- [ ] 能创建唯一 `search_id`
- [ ] 能记录 `pending/running/completed/partial/failed`
- [ ] 能缓存 `SearchHit[]`
- [ ] 能生成结构化 `SearchSummary`

## 3.3 抓取接入层

需要做的事：
- 扩展 `scraper` 支持传入平台关键词
- 不再只依赖固定关键词
- 保留 `backend`、sample fallback、错误分类

优先策略：
- 第一版优先扩展 [`scraper.fetchers.build_platform_query()`](../scraper/fetchers.py:272) 所依赖的查询生成逻辑
- 让调用侧能够覆盖默认关键词

验收标准：
- [ ] 用户输入的关键词可传入抓取层
- [ ] 返回结果中能保留 `query`
- [ ] 真实抓取失败时仍可带 fallback 信息

## 3.4 API 层

第一阶段只实现：
- `POST /api/search`
- `GET /api/search/{search_id}`
- `GET /api/search/{search_id}/hits`

落点：
- [`app/main.py`](../app/main.py)

验收标准：
- [ ] 可创建搜索任务
- [ ] 可查询任务状态
- [ ] 可读取命中结果列表
- [ ] 错误响应可区分 `not_found` 和任务失败

## 3.5 Dashboard 页面层

第一阶段只实现：
- 搜索模式与审核模式切换
- 搜索表单
- 状态栏
- 原始命中结果表
- 命中详情面板

落点：
- [`dashboard.py`](../dashboard.py)

验收标准：
- [ ] 页面可输入关键词并发起搜索
- [ ] 页面可显示任务状态和抓取摘要
- [ ] 页面可显示结果平台、价格、商家、来源、后端、错误分类、链接
- [ ] 页面可查看单条命中的详情
- [ ] 现有审核模式仍可正常使用

## 3.6 测试层

第一阶段建议补充：
- 搜索 API 测试
- 搜索服务单元测试
- Dashboard 最小交互验证
- 关键词抓取参数透传测试

建议文件：
- `tests/test_search_api.py`
- `tests/test_search_service.py`
- 适量补充到 [`tests/test_scraper.py`](../tests/test_scraper.py)

验收标准：
- [ ] 新增 API 有测试覆盖
- [ ] 状态流转有测试覆盖
- [ ] 关键词透传有测试覆盖
- [ ] 不破坏现有 [`tests/test_main_api.py`](../tests/test_main_api.py) 与 [`tests/test_dashboard.py`](../tests/test_dashboard.py)

---

## 4. 风险与约束

### 4.1 最大风险

1. 真实抓取超时和不稳定
2. Streamlit 自动刷新导致页面状态抖动
3. 同步执行搜索时响应时间过长
4. 现有审核页与新搜索页逻辑耦合过深

### 4.2 控制策略

- 第一阶段先以内存任务仓库实现
- 真实抓取失败允许 fallback，但必须可观测
- 新搜索工作台与旧审核工作台逻辑分函数拆开
- 比价和 AI 均后置，避免第一阶段过重

---

## 5. 每阶段验收门槛

### Phase A 完成门槛
- [ ] 可以输入平台关键词发起搜索
- [ ] 可以看到任务状态与抓取统计
- [ ] 可以看到标准化命中结果
- [ ] 可以查看链接、商家、来源、后端、错误分类
- [ ] 审核模式不回退、不损坏

### Phase B 完成门槛
- [ ] 可以查看同款归并结果
- [ ] 可以看到最高价、最低价、差价、差价率
- [ ] 可以按差价与销量排序

### Phase C 完成门槛
- [ ] 可以把比价结果转入审核池
- [ ] 可以继续用现有审批与存储链路完成决策

### Phase D 完成门槛
- [ ] 可以为比价组生成结构化 AI 建议
- [ ] 页面可展示价格、营销语、图片建议和风险提示

---

## 6. 推荐实施顺序

推荐严格按以下顺序编码：

1. [`app/schemas.py`](../app/schemas.py)
2. `app/search_store.py`
3. `app/search_service.py`
4. [`app/main.py`](../app/main.py)
5. [`tests/test_search_service.py`](../tests/test_pipeline.py)
6. [`tests/test_search_api.py`](../tests/test_main_api.py)
7. [`dashboard.py`](../dashboard.py)
8. 页面手动验证

说明：
- 先把域模型和服务层稳定下来
- 再接 API
- 最后接页面
- 避免先做前端后补后端导致重复返工

---

## 7. 实现检查清单

- [ ] 为 [`T009`](../docs/AI_SHARED_TASKLIST.md) 补齐 schema、service、api、dashboard 最小闭环
- [ ] 保持现有审核域接口兼容
- [ ] 为新增能力补测试
- [ ] 手动验证搜索工作台可用
- [ ] 文档同步更新到 [`README.md`](../README.md) 与 [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)

---

## 8. 结论

当前最合理的实施起点是：

先切到 [`code`](../dashboard.py) 模式，只实现 [`T009`](../docs/AI_SHARED_TASKLIST.md) 的最小闭环，不在第一轮混入跨平台比价和 AI 生成。
