# 架构文档索引

本目录是架构知识的唯一入口。任何跨模块改动、新增 Provider、修改共享契约之前，先读这里，再读代码。

## 1. 阅读顺序

| 顺序 | 文档 | 回答的问题 | 维护者 |
| --- | --- | --- | --- |
| 1 | [`ARCHITECTURE.md`](../../ARCHITECTURE.md) | 系统边界、六层划分、失败域、演进规则 | `@architecture-team` |
| 2 | [`dependency-rules.md`](dependency-rules.md) | 哪一层可以 import 哪一层，违规如何被拦截 | `@architecture-team` |
| 3 | [`adr/0001-record-architecture-decisions.md`](adr/0001-record-architecture-decisions.md) | 架构决策的格式、位置与生命周期 | `@architecture-team` |
| 4 | [`adr/0002-single-repository-modular-monorepo.md`](adr/0002-single-repository-modular-monorepo.md) | 为什么采用单仓库加每 Agent 一个模块 | `@architecture-team` |

规则类文档必须与代码在同一个 PR 内更新。规则变了而文档没变，等同于规则没有生效。

## 2. 两套体系

本仓库同时承载两套体系，二者不共用目录职责。

| 体系 | 目标 | 主要目录 |
| --- | --- | --- |
| 编码 Agent 工程体系 | 让 Codex、Copilot 等编码 Agent 理解、修改、验证、维护本仓库 | `AGENTS.md`、`ARCHITECTURE.md`、`docs/`、`.agents/`、`.codex/`、`.github/`、`scripts/` |
| 运行时 Agent 应用体系 | 让业务 Agent 作为生产服务运行 | `agents/`、`apps/`、`packages/`、`schemas/`、`evals/`、`infra/`、`tests/` |

判断标准很简单：一个文件如果描述「Agent 该怎么改代码」，它属于编码 Agent 工程体系；如果描述「业务 Agent 在生产里怎么跑」，它属于运行时应用体系。`AGENTS.md` 不是业务 Agent 定义，`agents/<name>/agent.yaml` 也不是编码 Agent 指令。

## 3. 六层速览

依赖方向固定为 `Types -> Config -> Repo -> Service -> Runtime -> UI`。低层不知道高层的存在。

| 层 | 排名 | 职责 | 典型位置 |
| --- | --- | --- | --- |
| `Types` | 0 | 数据形状、Schema、枚举、接口声明。无行为。 | `packages/agent-contracts/src/types.ts` |
| `Config` | 1 | 配置加载、校验、默认值、环境解析。 | `packages/state-store/src/config.ts` |
| `Repo` | 2 | 持久化与外部 I/O，不承载业务规则。 | `packages/state-store/src/repository.ts` |
| `Service` | 3 | 业务规则与编排，Agent 主逻辑所在层。 | `agents/research-agent/src/main.py` |
| `Runtime` | 4 | 进程入口、调度、生命周期、组合根。 | `apps/worker/src/index.ts` |
| `UI` | 5 | 展示与交互，只做呈现与用户动作转发。 | `apps/admin-console/src/index.tsx` |

完整的允许与禁止边，见 [`dependency-rules.md`](dependency-rules.md)。

## 4. 横切能力通过 Provider 接口进入

横切能力不属于任何一层，通过显式接口注入。接口在 `Types` 层声明，实现在平台包内，由 `Runtime` 组合根装配。

| 能力 | Provider 接口 | 实现位置 |
| --- | --- | --- |
| 身份 | `IdentityProvider` | `packages/tool-adapters/src/identity.ts` |
| 外部连接器 | `ConnectorProvider` | `packages/tool-adapters/src/connector.ts` |
| 遥测 | `TelemetryProvider` | `packages/observability/src/provider.ts` |
| 特性开关 | `FeatureFlagProvider` | `packages/policy-engine/src/flags.ts` |
| 模型访问 | `ModelProvider` | `packages/tool-adapters/src/model.ts` |

`Service` 只依赖接口类型，不得直接实例化实现，也不得 import 实现的内部路径。

## 5. 强制约束

意图写在文档里，强制落在自动化里。每条规则都有一个机器检查。

| 约束 | 检查 | 位置 |
| --- | --- | --- |
| 层级依赖方向 | 架构检查 | [`scripts/check-architecture.py`](../../scripts/check-architecture.py) |
| Agent 清单合法性 | 清单检查 | [`scripts/check-agent-manifests.py`](../../scripts/check-agent-manifests.py) |
| 文档链接与索引 | 链接检查 | [`scripts/check-doc-links.py`](../../scripts/check-doc-links.py) |
| 公开接口兼容性 | 契约测试 | `tests/contracts/` |
| 工具输入输出形状 | JSON Schema | `schemas/tool-contracts/` |
| 代码格式与静态检查 | CI 工作流 | [`.github/workflows/pull-request.yml`](../../.github/workflows/pull-request.yml) |

规则没有检查就是建议。新增一条必须遵守的架构规则时，同时提交对应的检查改动。

## 6. 运行时 Agent 架构

每个业务 Agent 是一个隔离模块，内部布局一致。

```text
agents/<agent-name>/
├── AGENTS.md          # 该模块的编码 Agent 指令
├── agent.yaml         # 清单：身份、模型、工具、限额、所有者
├── src/               # Service 层实现
├── prompts/           # 版本化提示词
├── tools/             # 该 Agent 专有工具实现
├── workflows/         # 编排图，仅在有编排时存在
└── tests/             # 单元、集成、评测、安全测试
```

每个 Agent 必须满足六项运行时要求：持久化状态与 checkpoint、工具调用幂等、工具授权网关、人工审批节点、端到端链路追踪、版本回滚。逐项说明见 [`ARCHITECTURE.md`](../../ARCHITECTURE.md) 第 5 节。

## 7. 架构决策记录

| ADR | 标题 | 状态 |
| --- | --- | --- |
| [ADR-0001](adr/0001-record-architecture-decisions.md) | 记录架构决策 | Accepted |
| [ADR-0002](adr/0002-single-repository-modular-monorepo.md) | 单仓库与模块化单体 | Accepted |

需要写 ADR 的场景：修改共享契约的破坏性变更、新增或删除 Provider 接口、新增顶层目录、引入新的外部依赖类别、把模块提升为独立服务、变更层级划分。

## 8. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`../design-docs/index.md`](../design-docs/index.md) | 设计意图与信念，解释「为什么这样设计」 |
| [`../design-docs/core-beliefs.md`](../design-docs/core-beliefs.md) | 工程信念，架构规则的来源 |
| [`../product-specs/index.md`](../product-specs/index.md) | 产品规格，架构需要满足的需求 |
| [`../security/security-architecture.md`](../security/security-architecture.md) | 身份、授权、密钥、审计的架构细节 |
| [`../security/threat-model.md`](../security/threat-model.md) | 威胁模型，与本文档的信任边界保持一致 |
| [`../operations/index.md`](../operations/index.md) | 运行时运维、SLO、值班与运行手册 |
| [`../references/README.md`](../references/README.md) | 外部参考资料的清单、来源与校验状态 |
| [`../generated/db-schema.md`](../generated/db-schema.md) | 由迁移生成的数据库结构，反映状态层真实形状 |
| [`../../README.md`](../../README.md) | 仓库总览与上手步骤 |

## 9. 变更流程

1. 判断变更类型：局部实现、跨模块改动、架构级改动。
2. 跨模块改动先写执行计划，放在 `docs/exec-plans/active/`，格式参考 [`AGENT-1042`](../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md)。
3. 架构级改动先写 ADR，状态为 `Proposed`，评审通过后改为 `Accepted`。
4. 代码、文档、检查脚本在同一个 PR 内一起提交。
5. 运行 `python scripts/check-architecture.py`、`python scripts/check-agent-manifests.py`、`python scripts/check-doc-links.py`，把真实输出附在 PR 描述里。

## 10. 常见误用

| 误用 | 后果 | 正确做法 |
| --- | --- | --- |
| 在 `UI` 里直接调用 `Repo` 查询数据 | 绕过业务规则与授权检查 | 通过 `Runtime` 暴露的接口调用 `Service` |
| 在 `Service` 里 `new` 一个具体 Provider | 测试不可替换，权限策略被绕过 | 由 `Runtime` 注入接口实例 |
| 从另一个包深层 import `src/` 内部文件 | 内部实现被外部耦合，重构即破坏 | 只 import 该包的公开入口 |
| 把业务流程写进 `Types` | 层职责混乱，无法单独测试 | 行为放 `Service`，形状放 `Types` |
| 为每个 Agent 建一个顶层目录 | 仓库根膨胀，责任分散 | Agent 放 `agents/`，应用放 `apps/` |
