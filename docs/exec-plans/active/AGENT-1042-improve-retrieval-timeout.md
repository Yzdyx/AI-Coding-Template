# AGENT-1042：改进检索超时与降级行为

本文件是任务元数据格式的**规范示例**。[`../../../AGENTS.md`](../../../AGENTS.md) 的任务工作流指向本文件作为元数据格式参考。新增执行计划时，复制下面的元数据块与章节骨架，替换为真实内容。

## 任务元数据

```yaml
task_id: AGENT-1042
title: 改进检索超时与降级行为
owner_team: research-platform
status: active
scope:
  paths:
    - agents/research-agent/src/
    - agents/research-agent/tools/
    - packages/tool-adapters/src/model.ts
  related_contracts:
    - packages/agent-contracts/src/types.ts
    - schemas/tool-contracts/search.schema.json
acceptance:
  - 检索在 p95 800ms 内返回，超时则触发降级而不是阻塞整条工作流
  - 超时与降级事件写入 trace，可按 run_id 在 observability 中查询
  - search 工具契约保持向后兼容，新增字段为可选
  - 单元测试与集成测试覆盖超时、降级、恢复三条路径
risk:
  level: medium
  production_write: false
validation:
  - python scripts/check-architecture.py
  - python scripts/check-agent-manifests.py
  - python scripts/check-doc-links.py
  - python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
```

## 1. 背景

`research-agent` 的检索步骤当前没有超时上限。当上游检索工具变慢时，整条工作流会被阻塞，直到工具返回或整个 run 超时。结果是：

1. 单个慢检索拖垮整个 run，占用 worker 槽位。
2. 用户看到的是长时间无输出，而不是可解释的降级结果。
3. 超时后重试会重复执行已经完成的步骤，因为缺少降级标记。

本任务为检索增加超时与降级路径，使工作流在检索变慢时仍能给出可用结果，并把超时事件暴露给观测系统。风险等级为 `medium`：改动集中在单个 Agent 模块与工具适配层，不写入生产系统，不改变共享契约的既有字段语义。

## 2. 范围与影响

| 项目 | 内容 |
| --- | --- |
| 修改路径 | `agents/research-agent/src/`、`agents/research-agent/tools/`、`packages/tool-adapters/src/model.ts` |
| 相关契约 | `packages/agent-contracts/src/types.ts`（只读，若需改字段先提架构评审）、`schemas/tool-contracts/search.schema.json`（新增可选字段） |
| 不修改 | 其他 Agent、其他平台包、`schemas/` 中的其他契约 |
| 依赖方向 | 遵守 [`../../architecture/dependency-rules.md`](../../architecture/dependency-rules.md)，`Service` 只依赖 `Repo` 与 `Config` |

契约变更规则：本任务只允许对 `search.schema.json` 做**向后兼容**的字段新增。任何破坏性变更必须停下，报告给 `@architecture-team`，不在本任务内实施。

## 3. 计划步骤

| 步骤 | 动作 | 产出 | 状态 |
| --- | --- | --- | --- |
| S1 | 在检索调用点引入超时参数，默认值来自 `Config` 层 | 配置项与读取逻辑 | [x] 已完成 |
| S2 | 定义降级结果形状，写入 `search.schema.json` 作为可选字段 | Schema 变更 | [x] 已完成 |
| S3 | 实现超时触发降级的路径，返回部分结果并标记 | Service 层实现 | [x] 已完成 |
| S4 | 把超时与降级事件接入 trace | 观测埋点 | [ ] 进行中 |
| S5 | 补充单元测试：超时、降级、恢复三条路径 | 测试用例 | [ ] 未开始 |
| S6 | 补充集成测试：慢上游下的端到端行为 | 集成测试 | [ ] 未开始 |
| S7 | 运行三项仓库检查并附真实输出 | 验证证据 | [ ] 未开始 |
| S8 | 更新 [`../../RELIABILITY.md`](../../RELIABILITY.md) 的超时相关 SLO 描述 | 文档 | [ ] 未开始 |

## 4. 决策日志

| 日期 | 决策 | 备选方案 | 理由 | 影响 |
| --- | --- | --- | --- | --- |
| 2026-02-03 | 超时默认值取 800ms，可配置 | 固定 500ms / 固定 2s | 500ms 对慢网络误伤，2s 使降级失去意义；800ms 覆盖 p95 且可控 | 需在 `Config` 层暴露配置项 |
| 2026-02-04 | 超时后降级返回部分结果并显式标记，而不是报错 | 直接抛异常 / 静默返回空 | 报错让用户失去已有信息，静默返回空不可诊断；标记后调用方与观测都能感知 | `search.schema.json` 新增可选字段 `degraded` |
| 2026-02-05 | 不修改共享契约的既有字段 | 改变现有字段语义 | 改变语义是破坏性变更，需要 ADR 与全消费者同步 | 契约变更限定为新增可选字段 |
| 2026-02-06 | 降级事件走现有观测通道，不新增 Provider | 新增降级专用 Provider | 现有 `TelemetryProvider` 已能承载事件，新增 Provider 违反「不为未用能力建结构」 | 无新增接口 |

## 5. 假设与风险

| 类型 | 内容 | 应对 |
| --- | --- | --- |
| 假设 | 上游检索工具在超时后不会产生副作用 | 检索为只读操作，无写入风险 |
| 假设 | 800ms 覆盖当前 p95 | 上线后观察实际分布，必要时调整默认值 |
| 风险 | 降级结果被下游误当成完整结果 | 显式 `degraded` 标记 + 下游校验 |
| 风险 | 超时值在不同环境表现不同 | 默认值可配置，按环境覆盖 |

## 6. 验证

完成后必须实际运行下列检查，并把命令与真实输出附在 PR 描述中。未运行的检查必须显式说明原因。

```bash
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
```

验收标准逐条核对，任何一条未满足都不得声明完成。相关质量与可靠性上下文见 [`../../QUALITY_SCORE.md`](../../QUALITY_SCORE.md) 与 [`../../RELIABILITY.md`](../../RELIABILITY.md)，安全约束见 [`../../SECURITY.md`](../../SECURITY.md)。

## 7. 归档

任务完成后：状态改为 `completed`，本文件移动到 `docs/exec-plans/completed/`，在 [`../tech-debt-tracker.md`](../tech-debt-tracker.md) 中登记遗留项，并在 [`../completed/AGENT-1001-tool-gateway-rollout.md`](../completed/AGENT-1001-tool-gateway-rollout.md) 同级的归档目录中保留完整记录。归档流程见 [`../../PLANS.md`](../../PLANS.md)。
