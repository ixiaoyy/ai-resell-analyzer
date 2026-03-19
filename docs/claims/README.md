# 模块认领说明模板

## 目标

`docs/claims/` 用于记录「开工前认领说明」。

作用：
- 防止多人重复开发同一模块
- 提前声明修改边界
- 让协作者和 AI 知道当前任务上下文

## 什么时候必须提交

必须提交认领说明再开始开发：

- 新模块开发（scraper / analyzer / matcher / copywriter / dashboard）
- 跨文件功能开发
- Schema 变更（`docs/DATA_SCHEMA.md`）
- 可能与他人并行冲突的改动

可豁免：

- typo 修复
- 纯格式调整
- 小范围文档润色
- 极小测试修正

## 文件命名

格式：`<date>-<module-slug>.md`

示例：
- `2026-03-15-scraper-xianyu-v1.md`
- `2026-03-15-schema-add-product-score.md`
- `2026-03-15-analyzer-trend-rules.md`

## 认领说明模板

复制以下模板新建你的认领说明：

```md
# 模块认领说明

- 模块名：
- 负责人：
- 改动类型：协议 / 功能 / 数据 / 工具 / 文档 / 测试
- 当前状态：planned / in_progress / blocked / done

## 目标

本次准备完成什么：

## 计划修改范围

- 会改哪些文件或目录：

## 明确不改范围

- 哪些文件、模块或协议边界不在本次范围内：

## 依据的协议文档

- README.md
- CONTRIBUTING.md
- docs/DATA_SCHEMA.md
- 其他：

## 预期产出

- 代码 / 文档 / 配置 / 测试 / 示例数据：

## 验证方式

- 计划执行哪些验证（lint / test / smoke test / schema validate）：

## 风险与备注

- 可能的冲突点、依赖和阻塞项：
```

## 注意

认领说明是「开工前声明」，**不能替代每次 commit 的变更文档**。

正确顺序：

1. 先提交认领说明
2. 再开始开发
3. 每次 commit 在 `docs/changes/` 补说明
4. 提 PR 时引用认领说明和 commit 说明
