# AGENT-1001：工具网关全量上线（已归档）

- 归档状态：completed
- 归档日期：2026-01-28
- 归档说明：本计划已完成并归档。内容作为历史记录保留，不再更新。新任务的元数据格式参考 [`../active/AGENT-1042-improve-retrieval-timeout.md`](../active/AGENT-1042-improve-retrieval-timeout.md)。

## 任务元数据

```yaml
task_id: AGENT-1001
title: 工具网关全量上线
owner_team: platform-team
status: completed
scope:
  paths:
    - packages/policy-engine/src/
    - packages/tool-adapters/src/connector.ts
    - apps/worker/src/
  related_contracts:
    - packages/agent-contracts/src/types.ts
    - schemas/agent-manifest.schema.json
acceptance:
  - 所有 Agent 的工具调用经工具授权网关，不存在绕过路径
  - 策略引擎 fail closed，网关不可用时拒绝调用而不是放行
  - 不可逆动作前存在阻塞式人工审批节点，并记录审批人
  - 灰度期间生产写操作零未授权事件
risk:
  level: high
  production_write: true
validation:
  - python scripts/check-architecture.py
  - python scripts/check-agent-manifests.py
  - python scripts/check-doc-links.py
  - pytest tests/contracts
```

## 1. 背景

在工具网关上线之前，每个 Agent 直接持有外部工具的凭据并自行发起调用。这带来三类问题：

1. 权限分散：授权逻辑散落在各 Agent 内部，无法统一审计。
2. 无法拦截危险动作：删除、发送、支付等不可逆动作缺少统一的人工审批节点。
3. 失败模式不一致：有的 Agent 在权限服务不可用时继续放行，违反最小权限原则。

本任务把工具调用统一收口到工具授权网关，由策略引擎集中判定权限与审批要求。风险等级为 `high`，因为改动涉及所有 Agent 的调用路径，且首次引入生产写操作的审批门禁。

## 2. 范围与影响

| 项目 | 内容 |
| --- | --- |
| 修改路径 | `packages/policy-engine/src/`、`packages/tool-adapters/src/connector.ts`、`apps/worker/src/` |
| 相关契约 | `packages/agent-contracts/src/types.ts`、`schemas/agent-manifest.schema.json` |
| 影响面 | 所有业务 Agent 的工具调用路径 |
| 依赖方向 | 遵守 [`../../architecture/dependency-rules.md`](../../architecture/dependency-rules.md)，网关在组合根装配 |

## 3. 计划步骤与完成情况

| 步骤 | 动作 | 状态 |
| --- | --- | --- |
| S1 | 定义工具授权网关接口，落在 `Types` 层 | [x] 完成 |
| S2 | 在策略引擎实现判定逻辑，默认 fail closed | [x] 完成 |
| S3 | 在组合根装配网关，所有 Agent 调用经此路径 | [x] 完成 |
| S4 | 增加不可逆动作的阻塞式人工审批节点 | [x] 完成 |
| S5 | 灰度：先只读工具，再写工具，最后不可逆工具 | [x] 完成 |
| S6 | 补契约测试与安全评测 | [x] 完成 |
| S7 | 更新安全与依赖规则文档 | [x] 完成 |

## 4. 决策日志

| 日期 | 决策 | 备选方案 | 理由 |
| --- | --- | --- | --- |
| 2025-12-08 | 网关默认 fail closed | fail open | 权限服务不可用时放行等于取消授权，违反最小权限 |
| 2025-12-10 | 审批节点为阻塞式，不采用事后通知 | 异步通知 + 事后审计 | 不可逆动作事后无法补救，必须事前阻塞 |
| 2025-12-12 | 网关在 `Runtime` 组合根装配，`Service` 只依赖接口 | 各 Agent 自行实例化 | 避免绕过策略与遥测装配 |
| 2025-12-15 | 审批人身份写入 trace 与审计日志 | 只写日志 | trace 可按 run 关联，便于回溯完整调用链 |
| 2025-12-18 | 灰度按工具风险分层推进 | 一次性全量切换 | 高风险动作需要更小的爆炸半径 |

## 5. 结果

验收标准逐条达成，灰度期间未出现未授权生产写事件。

| 验收标准 | 结果 | 证据 |
| --- | --- | --- |
| 所有工具调用经网关 | 达成 | `pytest tests/contracts` 通过 |
| 策略引擎 fail closed | 达成 | 故障注入测试：网关不可用时调用被拒绝 |
| 不可逆动作前有审批节点 | 达成 | 端到端测试覆盖审批阻塞与放行 |
| 灰度期间零未授权事件 | 达成 | 灰度看板无未授权写事件 |

## 6. 遗留与后续

1. 网关判定延迟在极端负载下接近预算上限，已登记到 [`../tech-debt-tracker.md`](../tech-debt-tracker.md)。
2. 审批节点的用户提示文案尚未与 [`../../product-specs/index.md`](../../product-specs/index.md) 的引导规格对齐，作为后续任务处理。
3. 网关决策缓存策略未实现，当前每次调用都实时判定。

## 7. 参考

| 文档 | 关系 |
| --- | --- |
| [`../../PLANS.md`](../../PLANS.md) | 计划的生命周期与归档规则 |
| [`../../SECURITY.md`](../../SECURITY.md) | 审批关卡与密钥处理的正式要求 |
| [`../../RELIABILITY.md`](../../RELIABILITY.md) | 网关的 SLO 与错误预算 |
| [`../../QUALITY_SCORE.md`](../../QUALITY_SCORE.md) | 交付后的质量评分 |
| [`../../architecture/adr/0002-single-repository-modular-monorepo.md`](../../architecture/adr/0002-single-repository-modular-monorepo.md) | 模块化单体的决策背景 |
| [`../../../scripts/check-architecture.py`](../../../scripts/check-architecture.py) | 依赖方向检查 |
| [`../../../AGENTS.md`](../../../AGENTS.md) | 任务工作流与验证要求 |
