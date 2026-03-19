# 贡献指南

## 开发原则

- **协议先于代码**：没有文档说明的功能不进入主干
- **人负责，AI 辅助**：AI 产出默认是候选草稿
- **小步迭代**：一次只推进一个可见切片
- **局部不污染全局**：模块内规则不得覆盖全局 Schema

## 分支规范

```
main          # 稳定主干，只接受 PR 合并
dev           # 集成分支
feat/<name>   # 功能分支
fix/<name>    # 修复分支
docs/<name>   # 文档分支
```

## Commit 规范

格式：`<type>(<scope>): <message>`

| type | 含义 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| docs | 文档变更 |
| refactor | 重构 |
| test | 测试 |
| chore | 构建/依赖/配置 |

示例：
```
feat(scraper): add xianyu hot item crawler
fix(matcher): handle 1688 rate limit retry
docs(schema): add product_score field definition
```

**每次 commit 必须附带文档说明**（见下文），仅有 commit message 不够。

## Commit 文档说明要求

每次实质性提交，必须在 `docs/changes/` 下新增一份说明文件。

文件名格式：`<date>-<slug>.md`

内容至少包含：
- 为什么改
- 改了什么
- 影响了哪些文件或模块
- 没改什么
- 是否涉及 Schema / 命名变更
- 做了哪些验证
- 风险点

可豁免场景：typo、纯格式调整、小范围文档润色。

## 开发前认领规则

以下情况必须先在 `docs/claims/` 提交认领说明再开发：

- 新模块开发
- 跨文件功能
- Schema 变更
- 可能与他人并行冲突的改动

认领说明模板见 [docs/claims/README.md](docs/claims/README.md)。

## PR 要求

PR 描述必须包含：
- 对应的认领说明（如适用）
- 对应的 commit 文档说明路径
- 验证方式与结果
- 是否有 AI 参与（参与了哪个环节）

## 变更类型分离

一个 PR 只做一类变更：

- **协议变更**：Schema、命名、字段类型
- **功能变更**：模块实现、爬虫逻辑、AI 分析
- **数据变更**：样本数据、缓存、配置

## 风险等级

| 等级 | 场景 | AI 参与度 |
|------|------|----------|
| A（低风险）| 文档、测试、小脚本 | 高参与 |
| B（中风险）| 模块内逻辑、数据转换 | AI 辅助，人主导 |
| C（高风险）| Schema 变更、核心架构、跨模块重构 | AI 只辅助 |
