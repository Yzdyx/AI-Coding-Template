# 运维文档索引

本目录保存**运行时如何被运维**：服务目标、值班、运行手册与事故复盘。它回答「线上出问题时怎么做」，不回答「为什么这样设计」（那是 [`../design-docs/index.md`](../design-docs/index.md)）或「系统由什么组成」（那是 [`../architecture/index.md`](../architecture/index.md)）。

## 1. 文档清单

| 文档 | 回答的问题 | 状态 | 维护者 |
| --- | --- | --- | --- |
| [`runbooks/agent-api-degradation.md`](runbooks/agent-api-degradation.md) | agent-api 延迟或错误率升高时怎么处置 | Active | `@sre-team` |
| [`runbooks/rollback.md`](runbooks/rollback.md) | 如何回滚到上一个已验证版本 | Active | `@sre-team` |
| [`incident-reviews/2026-01-15-tool-gateway-outage.md`](incident-reviews/2026-01-15-tool-gateway-outage.md) | 工具网关中断的原因、影响与整改项 | Reviewed | `@sre-team` |

状态取值：`Draft`、`Active`、`Stable`、`Deprecated`。事故复盘一经评审不再修改，后续结论写进新的复盘或整改项。

## 2. 服务目标

服务级别目标以 [`../RELIABILITY.md`](../RELIABILITY.md) 为准。本目录只记录达到目标的操作步骤，不重复定义阈值。

| 能力 | 目标 | 违反时的入口 |
| --- | --- | --- |
| agent-api 可用性 | 见 [`../RELIABILITY.md`](../RELIABILITY.md) | [`runbooks/agent-api-degradation.md`](runbooks/agent-api-degradation.md) |
| 长任务恢复 | 见 [`../RELIABILITY.md`](../RELIABILITY.md) | [`runbooks/rollback.md`](runbooks/rollback.md) |
| 发布与回滚 | 见 [`../../.agents/skills/deploy/SKILL.md`](../../.agents/skills/deploy/SKILL.md) | [`runbooks/rollback.md`](runbooks/rollback.md) |

## 3. 运行手册写法

1. 每份手册以一个可观测信号开头：指标、日志字段或告警名。
2. 步骤必须是可执行的命令或可点击的操作，不写「检查一下」。
3. 每一步写明预期结果。结果不符时给出下一步分支。
4. 写明停止条件与升级路径。
5. 手册与代码在同一个 PR 内更新。手册过期等同于没有手册。

## 4. 事故复盘写法

| 章节 | 内容 |
| --- | --- |
| 影响 | 受影响的能力、时间窗、受影响的任务数量 |
| 时间线 | 以 UTC 时间戳记录发现、定位、缓解、恢复 |
| 根因 | 直接原因与系统性原因分开写 |
| 整改项 | 每条含负责人、期限与验证方式 |
| 证据 | trace、指标面板、日志查询链接 |

## 5. 相关入口

| 入口 | 用途 |
| --- | --- |
| [`../RELIABILITY.md`](../RELIABILITY.md) | 可靠性目标与失败域 |
| [`../SECURITY.md`](../SECURITY.md) | 安全事件的处理要求 |
| [`../security/threat-model.md`](../security/threat-model.md) | 威胁模型与信任边界 |
| [`../../.agents/skills/deploy/checklist.md`](../../.agents/skills/deploy/checklist.md) | 发布检查清单 |
| [`../generated/db-schema.md`](../generated/db-schema.md) | 状态层真实结构，用于故障定位 |
