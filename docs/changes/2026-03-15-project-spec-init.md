# 变更说明：项目规范与文档体系初始化

- 日期：2026-03-15
- 模块：docs / 项目根目录
- 改动类型：文档
- 是否涉及 Schema 变更：否（首次定义 Schema）

## 为什么改

项目从零开始，需要在编写任何代码之前建立协作规范，防止 AI 自由发挥和边界失控。

## 改了什么

- `README.md`：项目概述、模块索引、快速开始
- `CONTRIBUTING.md`：分支规范、commit 规范、PR 要求、风险等级
- `docs/ARCHITECTURE.md`：五层流水线架构、模块职责、目录结构、设计原则
- `docs/DATA_SCHEMA.md`：五个核心数据结构定义（RawProduct / AnalyzedProduct / MatchedSupplier / CopyDraft / DecisionRecord）
- `docs/TECH_STACK.md`：技术选型、依赖约定、AI 调用约定
- `docs/AI参与开发协议.md`：AI 参与边界、硬规则、风险等级、禁止行为
- `docs/AI_SHARED_TASKLIST.md`：MVP 阶段 8 个任务登记
- `docs/claims/README.md`：模块认领说明模板与规则
- `docs/changes/README.md`：变更说明目录规则与模板

## 影响的文件或模块

全部为新建文件，无存量代码受影响。

## 没改什么

- 无任何业务代码
- 无任何数据文件

## 验证方式与结果

- 人工审阅所有文档，确认结构完整、无内部矛盾
- Schema 字段定义与架构模块划分一致

## 风险点

- Schema v0.1 是初始版本，后续实现时可能需要补字段，需走变更流程
- TECH_STACK 中 Streamlit 方案适合 MVP，复杂场景需评估升级
