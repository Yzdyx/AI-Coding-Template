# 数据库结构（生成文件）

> **本文件是结构模板，当前由人工维护。**
> 生成器：`python tooling/task-runner/generate_db_schema.py`（尚未实现，见 [`../../tooling/task-runner/README.md`](../../tooling/task-runner/README.md)）
> 生成来源：`packages/state-store/` 的迁移目录
> 一致性校验：[`../../scripts/check-doc-links.py`](../../scripts/check-doc-links.py) 只校验链接；内容一致性由 CI 的生成步骤比对。

## 1. 表清单

| 表 | 用途 | 写入方 | 保留策略 |
| --- | --- | --- | --- |
| `agent_runs` | 单次 Agent 运行的元数据与状态 | `apps/worker` | 见 [`../RELIABILITY.md`](../RELIABILITY.md) |
| `run_steps` | 每次步骤的输入输出摘要与耗时 | `apps/worker` | 同 `agent_runs` |
| `checkpoints` | 可恢复的执行状态快照 | `packages/state-store` | 运行结束后按策略清理 |
| `tool_calls` | 工具调用记录，含幂等键与风险级别 | 工具网关 | 审计保留期 |
| `approvals` | 人工审批记录，含审批人与理由 | `apps/agent-api` | 审计保留期 |
| `policy_decisions` | 策略判定记录 | `packages/policy-engine` | 审计保留期 |

## 2. 关键列

### agent_runs

| 列 | 类型 | 说明 |
| --- | --- | --- |
| `run_id` | uuid | 主键 |
| `agent` | text | 对应 `agents/<name>/agent.yaml` 的 `name` |
| `manifest_version` | text | 运行时使用的清单版本 |
| `prompt_hash` | text | 提示词内容哈希 |
| `status` | text | `running`、`awaiting_approval`、`degraded`、`succeeded`、`failed`、`cancelled` |
| `degraded` | boolean | 是否存在降级步骤 |
| `trace_id` | text | 端到端链路标识 |
| `created_at` | timestamptz | 创建时间 |

### tool_calls

| 列 | 类型 | 说明 |
| --- | --- | --- |
| `idempotency_key` | text | 唯一约束。重复调用返回首次结果 |
| `risk` | text | `low`、`medium`、`high` |
| `approved_by` | text | 高风险调用为必填 |

## 3. 约束

1. `tool_calls.idempotency_key` 建立唯一索引。这是重复副作用的主要防线。
2. `agent_runs.manifest_version` 与 `agent_runs.prompt_hash` 同时存在，用于复现一次运行。
3. 删除租户数据时必须同时覆盖主表、索引与备份策略。

## 4. 变更流程

1. 修改迁移，不修改本文件。
2. 在同一个 PR 内重新生成本文件。
3. 破坏性迁移需要 ADR 与回滚方案，见 [`../../.agents/skills/deploy/checklist.md`](../../.agents/skills/deploy/checklist.md)。
