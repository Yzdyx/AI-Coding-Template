# 质量评分

本文档定义各领域的质量评分规则与当前评分。评分回答「现在质量如何、缺口在哪」。评分不是考核，而是排优先级的依据；低分领域优先获得修复资源。

## 1. 评分规则

采用 0–4 五级制。每一级有明确的可观察标准，禁止主观给分。

| 分数 | 等级 | 判定标准 |
| --- | --- | --- |
| 4 | Excellent | 有自动化检查覆盖，近一个季度无回归；边界有测试保护 |
| 3 | Good | 有自动化检查覆盖，偶发小问题能快速定位并修复 |
| 2 | Fair | 部分检查覆盖，存在已知缺口，缺口已登记到 [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) |
| 1 | Poor | 缺少检查，问题靠人工发现；存在未登记的风险 |
| 0 | Absent | 无检查、无测试、无登记；质量不可观测 |

给分依据必须指向可验证的证据：检查脚本、测试目录、评测集或文档。没有证据的领域不得高于 1。

## 2. 各领域评分

| 领域 | 覆盖范围 | 当前分 | 目标分 | 主要证据 |
| --- | --- | --- | --- | --- |
| 架构 | 层级依赖、包边界、Provider 装配 | 3 | 4 | [`../scripts/check-architecture.py`](../scripts/check-architecture.py) |
| 契约 | 共享契约兼容性 | 3 | 4 | `tests/contracts/`、[`../schemas/agent-manifest.schema.json`](../schemas/agent-manifest.schema.json) |
| Agent 定义 | `agent.yaml` 合法性 | 3 | 4 | [`../scripts/check-agent-manifests.py`](../scripts/check-agent-manifests.py) |
| 前端 | 组件、可访问性、状态管理 | 2 | 3 | 前端集成测试、[`FRONTEND.md`](FRONTEND.md) 评审清单 |
| 评测 | 回归与安全评测覆盖 | 3 | 4 | [`../evals/regression/smoke.yaml`](../evals/regression/smoke.yaml)、[`../evals/safety/prompt-injection.yaml`](../evals/safety/prompt-injection.yaml)、[`../evals/baselines/baseline-2026-01.json`](../evals/baselines/baseline-2026-01.json) |
| 安全 | 授权、审批、密钥、输入信任 | 3 | 4 | [`SECURITY.md`](SECURITY.md)、[`../infra/policies/agent-policy.yaml`](../infra/policies/agent-policy.yaml) |
| 可靠性 | SLO、错误预算、恢复 | 3 | 4 | [`RELIABILITY.md`](RELIABILITY.md) |
| 可观测性 | trace、日志、定位能力 | 2 | 3 | `packages/observability/`、端到端 trace |
| 文档 | 索引、链接、与代码同步 | 4 | 4 | [`../scripts/check-doc-links.py`](../scripts/check-doc-links.py) |
| 数据与状态 | 持久化、checkpoint、保留策略 | 2 | 3 | `packages/state-store/`、[`../ARCHITECTURE.md`](../ARCHITECTURE.md) 第 7 节 |

当前平均分约为 2.8，目标为 3.5。低于目标的领域在下一季度获得优先修复排期。

## 3. 评分如何更新

1. 每季度评审一次，由 `@quality-team` 主持，各领域负责人提供证据。
2. 分数变化必须附证据。升级需要展示新增的检查或测试；降级需要说明出现了哪类问题。
3. 分数低于目标时，缺口登记到 [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md)，并给出目标季度。
4. 安全与可靠性领域分数低于 3 时，视为阻断项，优先于新功能。
5. 评分结果与 [`RELIABILITY.md`](RELIABILITY.md) 的错误预算一起用于发布决策。

## 4. 检查与证据的对应

| 检查 | 覆盖领域 | 命令 |
| --- | --- | --- |
| 架构检查 | 架构 | `python scripts/check-architecture.py` |
| 清单检查 | Agent 定义 | `python scripts/check-agent-manifests.py` |
| 链接检查 | 文档 | `python scripts/check-doc-links.py` |
| 契约测试 | 契约 | `pytest tests/contracts` |
| 回归评测 | 评测 | 运行 [`../evals/regression/smoke.yaml`](../evals/regression/smoke.yaml) |
| 安全评测 | 安全、评测 | 运行 [`../evals/safety/prompt-injection.yaml`](../evals/safety/prompt-injection.yaml) |

## 5. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) | 质量标准的来源信念 |
| [`DESIGN.md`](DESIGN.md) | 设计评审标准 |
| [`PLANS.md`](PLANS.md) | 验证标准如何写入执行计划 |
| [`RELIABILITY.md`](RELIABILITY.md) | 可靠性与错误预算 |
| [`SECURITY.md`](SECURITY.md) | 安全要求 |
| [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) | 缺口与债务登记 |
| [`product-specs/index.md`](product-specs/index.md) | 交付规格与验收标准 |
| [`architecture/index.md`](architecture/index.md) | 架构约束与检查 |
