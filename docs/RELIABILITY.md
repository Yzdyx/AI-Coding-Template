# 可靠性

本文档定义平台的可靠性目标、错误预算、恢复目标与 checkpoint 策略。它回答「多可靠算够、超出预算怎么办、故障后如何恢复」。运维流程与运行手册见 `docs/operations/`，安全要求见 [`SECURITY.md`](SECURITY.md)。

## 1. 服务与 SLO

| 服务 | 指标 | 目标（SLO） | 测量窗口 | 数据来源 |
| --- | --- | --- | --- | --- |
| `apps/agent-api` | 可用性 | 99.9% | 30 天滚动 | 请求成功率 |
| `apps/agent-api` | 延迟 p95 | ≤ 400ms（不含模型调用） | 30 天滚动 | 服务端计时 |
| `apps/worker` | run 成功率 | ≥ 99% | 30 天滚动 | run 终态统计 |
| `apps/worker` | run 恢复率 | ≥ 99%（崩溃后可续跑） | 30 天滚动 | checkpoint 命中率 |
| 工具网关 | 判定延迟 p95 | ≤ 50ms | 30 天滚动 | 网关计时 |
| 工具网关 | 可用性 | 99.95% | 30 天滚动 | 判定成功率 |
| 检索步骤 | 延迟 p95 | ≤ 800ms | 30 天滚动 | 检索埋点 |
| 管理控制台 | 可用性 | 99.5% | 30 天滚动 | 前端与接口成功率 |

SLO 是内部目标，不是对外承诺。任何 SLO 调整需评审并更新本表。

## 2. 错误预算

错误预算 = 100% − SLO。以 `apps/agent-api` 为例，30 天窗口内可用性 99.9% 对应约 43 分钟不可用预算。

| 预算消耗 | 触发动作 |
| --- | --- |
| < 50% | 正常发布 |
| 50% – 75% | 提高发布谨慎度：更小的灰度批次，更长的观察期 |
| 75% – 100% | 冻结非关键发布，优先修复可靠性问题 |
| 预算耗尽 | 冻结全部功能发布，只允许可靠性修复；需要 `@sre-team` 批准才能解冻 |

预算规则：

1. 可靠性修复优先于新功能，直到预算回到 50% 以下消耗。
2. 因不可逆生产写入导致的事故，按 [`SECURITY.md`](SECURITY.md) 走事故路径，不占用常规预算判定。
3. 预算消耗与 [`QUALITY_SCORE.md`](QUALITY_SCORE.md) 的可靠性评分联动。

## 3. 恢复目标

| 目标 | 定义 | 取值 | 说明 |
| --- | --- | --- | --- |
| RTO | 故障到恢复服务的最长时间 | 30 分钟 | 关键服务 |
| RPO | 可容忍的数据丢失窗口 | 5 分钟 | 状态存储与 checkpoint |
| MTTD | 故障到发现的最长时间 | 5 分钟 | 依赖监控与告警 |
| MTTR | 发现到恢复的平均时长 | 30 分钟 | 依赖运行手册 |

恢复依赖三个能力，缺一不可：

1. 可回滚：每个模块独立发布与回滚，见 [`../ARCHITECTURE.md`](../ARCHITECTURE.md) 第 5 节。
2. 可定位：端到端 trace 覆盖模型、工具与工作流，失败可定位到具体步骤。
3. 可续跑：checkpoint 使失败 run 从断点恢复，而不是从头重跑。

## 4. Checkpoint 策略

Checkpoint 让失败的 run 从断点恢复。它不是事务，无法回滚已经产生的外部副作用。

| 项目 | 策略 |
| --- | --- |
| 持久化位置 | 由 `state-store` Provider 提供，生产环境使用外部持久化 |
| 保存时机 | 每个工具调用前后、每个工作流节点边界 |
| 保留窗口 | run 完成后按保留策略保留，见 [`../ARCHITECTURE.md`](../ARCHITECTURE.md) 第 7 节 |
| 恢复语义 | 从最近一次成功 checkpoint 续跑 |
| 副作用处理 | 工具调用必须幂等；不可逆动作使用幂等键或补偿动作 |

规则：

1. checkpoint 保存失败时，run 不得继续执行不可逆动作。
2. 恢复时不得重复已确认完成的外部副作用；使用幂等键保证重放安全。
3. checkpoint 不得包含明文密钥或凭据，见 [`SECURITY.md`](SECURITY.md)。
4. 恢复行为必须写入 trace，便于事后核对是否发生重复副作用。

## 5. 发布与回滚

1. 分阶段发布：内部 → 灰度 → 全量，每阶段有观察窗口。
2. 回滚条件在上线前确定，写入执行计划，见 [`PLANS.md`](PLANS.md)。
3. 回滚以模块为单位，单个 Agent 的回滚不影响其他 Agent。
4. 生产写入类改动必须有人工审批节点，见 [`SECURITY.md`](SECURITY.md)。

## 6. 监控与告警

| 对象 | 指标 | 告警条件 |
| --- | --- | --- |
| 可用性 | 请求成功率 | 低于 SLO 时告警 |
| 延迟 | p95、p99 | 接近预算上限时告警 |
| 错误预算 | 剩余比例 | 消耗超过 75% 时告警 |
| 工具网关 | 判定失败率 | 出现 fail closed 拒绝激增时告警 |
| checkpoint | 命中率与失败率 | 恢复失败率上升时告警 |

告警必须可操作：每条告警指向一个运行手册条目或一个明确的下一步动作。无对应手册的告警要么补手册，要么删除。

## 7. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`QUALITY_SCORE.md`](QUALITY_SCORE.md) | 可靠性领域质量评分 |
| [`SECURITY.md`](SECURITY.md) | 安全与事故路径 |
| [`PLANS.md`](PLANS.md) | 回滚条件如何写入执行计划 |
| [`exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | 检索超时与降级相关 SLO 的计划 |
| [`operations/index.md`](operations/index.md) | 运行手册、值班与事故复盘 |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | 失败域、状态与 checkpoint 架构 |
| [`../infra/policies/agent-policy.yaml`](../infra/policies/agent-policy.yaml) | 运行时策略与限额 |
| [`../evals/baselines/baseline-2026-01.json`](../evals/baselines/baseline-2026-01.json) | 质量基线，用于判断回归 |
