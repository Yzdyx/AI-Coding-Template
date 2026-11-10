# 执行计划

本文档定义执行计划（execution plan）的写法、元数据格式、进度跟踪与归档规则。执行计划是任务从「需求」到「验证证据」的载体，也是编码 Agent 与人类工程师协作的共同上下文。

## 1. 什么时候写执行计划

| 情形 | 是否需要计划 | 说明 |
| --- | --- | --- |
| 跨模块改动 | 需要 | 涉及多个模块或共享契约时必须先写 |
| 单个模块内的局部改动 | 可选 | 改动小且可独立验证时，写在 PR 描述即可 |
| 修改共享契约 | 需要 | 见 [`architecture/index.md`](architecture/index.md) 的变更流程 |
| 新增或删除 Provider | 需要 | 通常还需要 ADR |
| 运维、发布、迁移 | 需要 | 与 [`RELIABILITY.md`](RELIABILITY.md) 联动 |
| 纯文档或格式调整 | 不需要 | 直接提 PR |

判断标准：如果一个改动需要多步、跨多人、或有不可逆风险，就写计划。计划是给未来的自己和协作者看的，不是给流程看的。

## 2. 元数据格式

每个执行计划以一段 YAML 元数据块开头。这是任务元数据的规范格式，完整示例见 [`exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](exec-plans/active/AGENT-1042-improve-retrieval-timeout.md)，[`../AGENTS.md`](../AGENTS.md) 的任务工作流指向该文件作为参考。

```yaml
task_id: AGENT-NNNN
title: 一句话描述任务目标
owner_team: 负责团队句柄
status: draft | active | blocked | completed
scope:
  paths:
    - 允许改动的路径，一行一条
  related_contracts:
    - 受影响或被读取的共享契约
acceptance:
  - 可判定通过或失败的验收条目
risk:
  level: low | medium | high
  production_write: true | false
validation:
  - 完成后必须运行的检查命令
```

字段说明：

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| `task_id` | 是 | 唯一编号，格式 `AGENT-NNNN`，永不复用 |
| `title` | 是 | 任务目标，一句话 |
| `owner_team` | 是 | 负责团队句柄，与 [`../CODEOWNERS`](../CODEOWNERS) 一致 |
| `status` | 是 | 计划状态，取值见第 3 节 |
| `scope.paths` | 是 | 允许改动的路径，越界即违规 |
| `scope.related_contracts` | 是 | 受影响或只读引用的共享契约 |
| `acceptance` | 是 | 验收条目列表，每条可判定 |
| `risk.level` | 是 | 风险等级，判定见 [`PRODUCT_SENSE.md`](PRODUCT_SENSE.md) |
| `risk.production_write` | 是 | 是否写入生产，`true` 时必须有审批节点 |
| `validation` | 是 | 完成后必须运行的检查命令列表 |

`scope.paths` 是硬边界。改动超出声明路径时，停止并拆成新任务，不扩大当前任务范围。

## 3. 状态与生命周期

| 状态 | 含义 | 允许的转移 |
| --- | --- | --- |
| `draft` | 起草中，未开始实施 | → `active` |
| `active` | 实施中 | → `blocked`、→ `completed` |
| `blocked` | 被外部依赖或决策阻塞 | → `active` |
| `completed` | 完成并归档 | 终态 |

生命周期：

1. **创建**：计划写入 `docs/exec-plans/active/`，状态为 `draft` 或 `active`。
2. **实施**：按计划步骤推进，更新进度复选框与决策日志。
3. **阻塞**：遇到外部依赖时状态改为 `blocked`，写明阻塞原因与解除条件。
4. **验证**：运行 `validation` 中的全部命令，把真实输出附在 PR 描述中。未运行的检查必须说明原因。
5. **归档**：完成后状态改为 `completed`，文件移动到 `docs/exec-plans/completed/`，遗留项登记到 [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md)。

已归档计划不修改。确需更正时，新建计划并在其中说明。

## 4. 章节骨架

复制下面的骨架作为新计划的起点。

```markdown
# AGENT-NNNN：任务标题

## 任务元数据
[上面的 YAML 块]

## 1. 背景
[当前问题，用事实描述。]

## 2. 范围与影响
[修改路径、相关契约、不修改的内容、依赖方向。]

## 3. 计划步骤
[表格：步骤、动作、产出、状态。]

## 4. 决策日志
[表格：日期、决策、备选方案、理由、影响。]

## 5. 假设与风险
[表格：类型、内容、应对。]

## 6. 验证
[必须运行的检查命令与验收标准逐条核对。]

## 7. 归档
[完成后如何归档与登记遗留项。]
```

## 5. 决策日志

决策日志记录「为什么这样做」，而不是「做了什么」。每条决策写明备选方案与理由，避免同一个问题被反复讨论。

规则：

1. 每条决策一行，包含日期、决策、备选方案、理由、影响。
2. 偏离设计信念或依赖规则时，必须写明退出条件。
3. 决策日志只增不改。决策被推翻时，追加一行说明推翻原因，不删除旧行。

## 6. 进度跟踪

1. 计划步骤用复选框 `[ ]` 与 `[x]` 标记，状态实时更新。
2. 进度更新随代码提交一起进行，不单独攒到最后。
3. 完成定义：所有 `acceptance` 条目满足，所有 `validation` 命令实际运行且有输出。
4. 不得把未运行的检查标记为完成。

## 7. 归档规则

| 步骤 | 动作 |
| --- | --- |
| 1 | 确认 `acceptance` 全部满足，`validation` 全部运行 |
| 2 | 状态改为 `completed` |
| 3 | 文件移动到 `docs/exec-plans/completed/` |
| 4 | 遗留项登记到 [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) |
| 5 | 在 PR 描述中给出归档后的路径与验证证据 |

参考已归档示例：[`exec-plans/completed/AGENT-1001-tool-gateway-rollout.md`](exec-plans/completed/AGENT-1001-tool-gateway-rollout.md)。

## 8. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | 当前活跃计划，元数据格式的规范示例 |
| [`exec-plans/completed/AGENT-1001-tool-gateway-rollout.md`](exec-plans/completed/AGENT-1001-tool-gateway-rollout.md) | 已归档计划示例 |
| [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) | 遗留项与债务登记 |
| [`PRODUCT_SENSE.md`](PRODUCT_SENSE.md) | 风险分级判定 |
| [`DESIGN.md`](DESIGN.md) | 设计原则，计划需与之相容 |
| [`QUALITY_SCORE.md`](QUALITY_SCORE.md) | 验证标准与质量评分 |
| [`architecture/index.md`](architecture/index.md) | 跨模块改动的架构流程 |
| [`../AGENTS.md`](../AGENTS.md) | 任务工作流与验证要求 |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | 系统边界 |
| [`../.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) | PR 中需附的验证证据 |
