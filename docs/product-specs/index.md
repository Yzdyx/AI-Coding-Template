# 产品规格索引

本目录保存产品功能规格与验收标准。规格回答「要交付什么、如何验收」，不回答「怎么实现」。任务拆解与实现计划见 [`../PLANS.md`](../PLANS.md)；产品决策方式与风险分级见 [`../PRODUCT_SENSE.md`](../PRODUCT_SENSE.md)。

## 1. 规格清单

| 规格编号 | 名称 | 规格文档 | 负责人 | 状态 | 目标版本 |
| --- | --- | --- | --- | --- | --- |
| SPEC-0001 | 新用户引导 | [`new-user-onboarding.md`](new-user-onboarding.md) | `@product-team` | Active | 2026.1 |
| SPEC-0002 | 工具授权网关 | [`../exec-plans/completed/AGENT-1001-tool-gateway-rollout.md`](../exec-plans/completed/AGENT-1001-tool-gateway-rollout.md) | `@platform-team` | Shipped | 2026.0 |
| SPEC-0003 | 检索超时与降级 | [`../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | `@research-platform` | Active | 2026.1 |

状态取值：`Draft`（起草中）、`Active`（开发中，验收标准已冻结）、`Shipped`（已上线）、`Deprecated`（已废弃）。已交付的规格用执行计划文档承载验收证据，不再单独维护规格正文。

## 2. 规格与执行计划的分工

| 类型 | 位置 | 回答的问题 | 生命周期 |
| --- | --- | --- | --- |
| 产品规格 | `docs/product-specs/` | 要交付什么、验收标准是什么、成功指标是什么 | 需求冻结到交付完成 |
| 执行计划 | [`../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | 这次任务怎么拆、怎么做、做到哪 | 任务创建到归档 |
| 质量评分 | [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) | 交付后各领域质量如何 | 持续维护 |

一个规格可以对应多个执行计划。规格冻结后不再改动验收标准；确需变更时，走 [`../PRODUCT_SENSE.md`](../PRODUCT_SENSE.md) 的决策流程，并记录变更原因。

## 3. 规格文档模板

新增规格时复制下面的骨架。占位符用方括号标出，提交前必须全部替换为真实内容。

```markdown
# [规格名称]

- 规格编号：[SPEC-NNNN]
- 状态：[Draft | Active | Shipped | Deprecated]
- 负责人：[团队句柄]
- 目标版本：[YYYY.N]
- 相关文档：[相对链接列表]

## 问题

[用户或业务当前遇到的真实问题，用事实描述，不写解决方案。]

## 目标

[本次要达成的可度量结果，一条一条列出。]

## 非目标

[明确排除的范围，防止范围蔓延。]

## 用户流程

[从触发到结束的完整路径，标明关键决策点与失败分支。]

## 验收标准

[可被测试或检查的条目，每条都能判定通过或失败。]

## 成功指标

[上线后观察的量化指标与目标值。]

## 发布方式

[灰度策略、回滚条件、监控项。]
```

## 4. 验收标准如何被检查

规格里的验收标准不能停留在文字。每条标准都应指向一种可执行的验证方式。

| 标准类型 | 检查方式 | 证据位置 |
| --- | --- | --- |
| 功能行为 | 单元测试与集成测试 | `agents/<agent>/tests/`、`tests/end-to-end/` |
| 接口契约 | 契约测试 | [`../../tests/contracts/`](../../tests/contracts/) |
| 架构约束 | 架构检查 | [`../../scripts/check-architecture.py`](../../scripts/check-architecture.py) |
| 安全行为 | 安全评测集 | [`../../evals/safety/prompt-injection.yaml`](../../evals/safety/prompt-injection.yaml) |
| 回归质量 | 回归评测 | [`../../evals/regression/smoke.yaml`](../../evals/regression/smoke.yaml) |

## 5. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`../PRODUCT_SENSE.md`](../PRODUCT_SENSE.md) | 产品决策方式与风险分级，决定规格是否值得做 |
| [`../design-docs/index.md`](../design-docs/index.md) | 设计意图，约束规格的技术可行性 |
| [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) | 交付后的质量评分 |
| [`../PLANS.md`](../PLANS.md) | 规格如何转化为执行计划 |
| [`../../README.md`](../../README.md) | 仓库总览与上手步骤 |
