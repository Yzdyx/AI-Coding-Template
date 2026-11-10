# 依赖规则

本文档定义本仓库的依赖方向、允许与禁止的边，以及这些规则如何被自动检查。规则以 [`ARCHITECTURE.md`](../../ARCHITECTURE.md) 第 3 节为准，本文档是它的完整展开。

## 1. 目的与适用范围

| 项目 | 说明 |
| --- | --- |
| 目的 | 让依赖方向可预测、可检查、可自动化拒绝 |
| 适用范围 | `apps/`、`packages/`、`agents/`、`schemas/`、`tests/` 下的全部业务代码 |
| 不适用 | `scripts/`、`tooling/`、`.agents/`、`.codex/`、`.github/`、`docs/`、`infra/`。这些是工具与交付资产，不参与运行时分层 |
| 裁决方式 | 文档解释规则，`scripts/check-architecture.py` 判定违规。二者冲突时以检查脚本为准，并立即修文档 |

## 2. 六层定义

层级顺序就是允许的依赖方向：`Types -> Config -> Repo -> Service -> Runtime -> UI`。

| 层 | 排名 | 职责 | 允许包含 | 禁止包含 | 典型位置 |
| --- | --- | --- | --- | --- | --- |
| `Types` | 0 | 数据形状、Schema、枚举、接口声明 | 类型别名、interface、枚举、常量枚举、类型守卫的纯函数签名 | 任何 I/O、网络调用、日志、状态变更、依赖注入 | `packages/agent-contracts/src/types.ts` |
| `Config` | 1 | 配置加载、校验、默认值、环境解析 | 配置读取、Schema 校验、默认值合并、环境变量解析 | 业务规则、持久化写入、对外请求 | `packages/state-store/src/config.ts` |
| `Repo` | 2 | 持久化与外部 I/O | 数据库访问、对象存储、外部 HTTP 客户端、序列化 | 业务分支逻辑、跨聚合编排 | `packages/state-store/src/repository.ts` |
| `Service` | 3 | 业务规则与编排 | 用例、策略、工作流、Agent 主逻辑、工具实现 | 进程入口、HTTP 路由注册、定时器注册 | `agents/research-agent/src/main.py` |
| `Runtime` | 4 | 进程入口、调度、生命周期、组合根 | 入口函数、依赖装配、信号处理、健康检查、任务调度 | 业务规则、直接 SQL | `apps/worker/src/index.ts` |
| `UI` | 5 | 展示与交互 | 组件、样式、表单、路由、状态展示 | 直接数据访问、授权判断逻辑、密钥与令牌处理 | `apps/admin-console/src/index.tsx` |

层与目录不是一对一关系。一个包内部可以同时有 `Types` 与 `Repo` 层文件（例如 `packages/state-store/`），只要文件之间的 import 方向合法。

## 3. 依赖方向矩阵

行是导入方，列是被导入方。`✔` 允许，`✘` 禁止。

| 导入方 \ 被导入方 | `Types` | `Config` | `Repo` | `Service` | `Runtime` | `UI` |
| --- | --- | --- | --- | --- | --- | --- |
| `Types` | ✔ | ✘ | ✘ | ✘ | ✘ | ✘ |
| `Config` | ✔ | ✔ | ✘ | ✘ | ✘ | ✘ |
| `Repo` | ✔ | ✔ | ✔ | ✘ | ✘ | ✘ |
| `Service` | ✔ | ✔ | ✔ | ✔ | ✘ | ✘ |
| `Runtime` | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ |
| `UI` | ✔ | ✘ | ✘ | ✘ | ✔ | ✔ |

两条特殊规则，容易记错：

1. `Types` 是唯一允许同层引用的层。`Types` 之间可以互相引用（例如一个契约包的接口类型引用另一个契约包的类型），但不得引用任何更高层。这对应 `ARCHITECTURE.md` 中「`Types` 不依赖平台内任何其他层」的表述。
2. `UI` 只允许依赖 `Types`、`Runtime`、`UI`。虽然排名上 `UI` 高于 `Service`，但 `UI` 不得直接 import `Service`、`Repo`、`Config`。界面需要的每个能力都必须由 `Runtime` 以显式接口暴露。

## 4. 允许与禁止的边

| 边 | 判定 | 理由 |
| --- | --- | --- |
| `Types -> Types` | 允许 | 类型组合，无运行时耦合 |
| `Config -> Types` | 允许 | 配置形状来自类型定义 |
| `Repo -> Types` | 允许 | 持久化对象形状来自类型定义 |
| `Repo -> Config` | 允许 | 数据源地址与超时来自配置 |
| `Service -> Types` | 允许 | 业务规则使用契约类型 |
| `Service -> Config` | 允许 | 业务规则读取配置与开关默认值 |
| `Service -> Repo` | 允许 | 业务规则通过仓储读写状态 |
| `Service -> Service` | 允许 | 同层编排，禁止形成环 |
| `Runtime -> Service` | 允许 | 入口驱动用例 |
| `Runtime -> Repo` | 允许 | 组合根装配仓储实现 |
| `Runtime -> Config` | 允许 | 入口负责加载与校验配置 |
| `UI -> Runtime` | 允许 | 界面通过运行时暴露的接口取数据与发命令 |
| `UI -> Types` | 允许 | 展示契约类型 |
| `UI -> UI` | 允许 | 组件组合 |
| `Types -> Config` | 禁止 | 类型层不得读取配置，否则无法被任何层安全复用 |
| `Types -> Repo` | 禁止 | 类型层不得触发 I/O |
| `Types -> Service` | 禁止 | 反向依赖，破坏可替换性 |
| `Config -> Repo` | 禁止 | 配置加载不得读写业务数据 |
| `Config -> Service` | 禁止 | 反向依赖 |
| `Repo -> Service` | 禁止 | 仓储不得调用业务规则，否则业务逻辑被下沉 |
| `Repo -> Runtime` | 禁止 | 反向依赖 |
| `Service -> Runtime` | 禁止 | 业务规则不得依赖进程入口，否则无法单测与复用 |
| `Service -> UI` | 禁止 | 反向依赖 |
| `UI -> Service` | 禁止 | 界面直连业务层会绕过 `Runtime` 的授权与审计装配 |
| `UI -> Repo` | 禁止 | 界面直连数据层会绕过业务规则与租户隔离 |
| `UI -> Config` | 禁止 | 界面不得读取配置，配置由 `Runtime` 注入 |
| 任意层 -> 其他包的 `src/` 内部路径 | 禁止 | 内部实现不属于契约，外部耦合会让重构变成破坏性变更 |
| 任意层 -> 其他包的 `internal/` 或未在公开入口导出的符号 | 禁止 | 同上 |
| `Service` -> Provider 实现 | 禁止 | 必须依赖接口类型，实现由组合根注入 |
| 组合根之外的 Provider 实例化 | 禁止 | 绕过策略与遥测装配 |
| 任何环状依赖 | 禁止 | 循环依赖使层序失效，构建与测试无法切分 |

## 5. Provider 接口规则

横切能力不通过层进入，而通过显式接口注入。

| 能力 | 接口 | 实现位置 | 组合根 |
| --- | --- | --- | --- |
| 身份 | `IdentityProvider` | `packages/tool-adapters/src/identity.ts` | `apps/agent-api/src/index.ts`、`apps/worker/src/index.ts` |
| 外部连接器 | `ConnectorProvider` | `packages/tool-adapters/src/connector.ts` | `apps/worker/src/index.ts` |
| 遥测 | `TelemetryProvider` | `packages/observability/src/provider.ts` | `apps/agent-api/src/index.ts`、`apps/worker/src/index.ts` |
| 特性开关 | `FeatureFlagProvider` | `packages/policy-engine/src/flags.ts` | `apps/agent-api/src/index.ts`、`apps/worker/src/index.ts` |
| 模型访问 | `ModelProvider` | `packages/tool-adapters/src/model.ts` | `apps/worker/src/index.ts` |

规则：

1. 接口形状在 `Types` 层声明，实现在平台包内，装配只发生在 `Runtime` 层（组合根）。唯一例外：参考实现所属包自己的公开工厂函数（`packages/tool-adapters/src/index.ts` 的 `createModelProvider` 等）构造 `Reference*` 实现供组合根调用，业务代码不得直接调用这些构造函数。
2. `Service` 与 `Repo` 只接收接口实例作为参数，不 import 实现文件。
3. 需要新增横切能力时，先加接口，再加实现，最后在组合根装配。不得把能力直接写进 `Service`。
4. 测试可以使用内存实现替换 Provider，替换只发生在测试代码内。
5. Provider 的失败语义必须显式声明：策略引擎与授权相关 Provider 必须 fail closed。

## 6. 包边界

1. 跨包访问只走公开入口：TypeScript 包以 `package.json` 的 `exports` 为准，Python 包以 `__init__.py` 的公开符号为准。
2. 共享契约位于 `packages/agent-contracts/`，由 `@architecture-team` 评审。破坏性变更需要 ADR。
3. JSON Schema 位于 `schemas/`，是跨语言契约的唯一事实来源。生成类型，不要手写重复形状。
4. 生产者与消费者都必须容忍新增字段：只读取已知字段，未知字段保留。
5. 禁止通过相对路径跨包引用（例如 `../../other-package/src/x`）。跨包引用必须使用包名。

## 7. 自动化强制

检查脚本：[`scripts/check-architecture.py`](../../scripts/check-architecture.py)。

执行方式：

```bash
python scripts/check-architecture.py
```

脚本行为：

1. 遍历 `apps/`、`packages/`、`agents/` 下的源文件，按路径映射到六层。
2. 解析 import：TypeScript 的 `import ... from '<specifier>'` 与 Python 的 `import`、`from ... import`。
3. 把 import 目标解析为仓库内路径或包名，计算「导入层 -> 被导入层」这条边。
4. 按第 3、4 节的矩阵与规则表判定，命中违规则输出一行。
5. 输出格式为 `相对路径:行号  <规则编号>  <说明>`，末尾给出违规总数与受影响文件数。
6. 退出码：`0` 无违规，`1` 存在违规，`2` 脚本自身错误（例如路径缺失、解析失败）。

示例输出：

```text
packages/state-store/src/repository.ts:14   DEP-001   Repo -> Service 越层依赖 (import '../service/run-manager')
agents/support-agent/src/main.py:22         DEP-004  Service 直接实例化 PostgresStateStore，绕过 Provider 注入
apps/admin-console/src/runs-table.tsx:8     DEP-002  UI 直接 import Service，必须经 Runtime 暴露接口
violations=3 affected_files=3
```

规则编号：

| 编号 | 规则 | 典型修复 |
| --- | --- | --- |
| `DEP-001` | 层级方向违规：低层依赖高层 | 把被依赖能力下沉到低层，或反转依赖 |
| `DEP-002` | `UI` 越层依赖 `Service`、`Repo`、`Config` | 由 `Runtime` 暴露接口，`UI` 只调用该接口 |
| `DEP-003` | 跨包深层导入或相对路径跨包引用 | 改用包名与公开入口 |
| `DEP-004` | 绕过 Provider 直接实例化实现 | 改为注入接口，装配移到组合根；所属包的 `create*` 工厂函数内允许构造自己的 `Reference*` 实现 |
| `DEP-005` | 环状依赖 | 抽出共享形状到 `Types`，或引入中间接口 |
| `DEP-006` | `Types` 层出现行为或 I/O | 行为移到 `Service`，形状留在 `Types`（注释中的词不算，检查前先剥离注释） |
| `DEP-007` | 在组合根之外创建 Provider 实例 | 实例化移到 `apps/*/src/index.ts`；参考实现所属包的公开工厂函数除外 |
| `DEP-008` | 使用了未声明的工作区依赖 | 在对应 `package.json` 或依赖清单中声明 |

豁免策略：

1. 没有行内豁免注释。不得用注释关闭单条规则。
2. 需要长期偏离规则时，写 ADR 说明原因、范围与退出条件，然后修改检查脚本与本文档。
3. 临时性偏离使用执行计划记录，必须包含清理期限，并写入 [`../exec-plans/tech-debt-tracker.md`](../exec-plans/tech-debt-tracker.md)。

## 8. 违规处理流程

| 步骤 | 动作 |
| --- | --- |
| 1 | 在 CI 或本地看到 `DEP-xxx` 输出，先确认不是自己引入的（`git log -L` 或 `git blame` 定位） |
| 2 | 是自己的改动：按上表修复，不修改检查脚本 |
| 3 | 是历史遗留：在 PR 描述中声明，登记到技术债跟踪表，不要扩大范围 |
| 4 | 认为规则本身有问题：提 ADR，附上具体场景、替代方案与影响面 |
| 5 | 修复后重跑三项检查，把真实输出附在 PR 里 |

## 9. 与其他检查的关系

| 检查 | 覆盖 | 与依赖规则的关系 |
| --- | --- | --- |
| [`scripts/check-architecture.py`](../../scripts/check-architecture.py) | 层级方向、包边界、Provider 装配 | 本文档的直接执行者 |
| [`scripts/check-agent-manifests.py`](../../scripts/check-agent-manifests.py) | `agent.yaml` 是否符合 [`agent-manifest.schema.json`](../../schemas/agent-manifest.schema.json) | 保证每个 Agent 模块声明了模型、工具、限额与所有者 |
| [`scripts/check-doc-links.py`](../../scripts/check-doc-links.py) | 文档相对链接与索引 | 保证规则文档本身可达 |
| `tests/contracts/` | 公开接口兼容性 | 保证跨包依赖在运行时也成立 |
| [`.github/workflows/pull-request.yml`](../../.github/workflows/pull-request.yml) | 格式、静态检查、上述脚本 | 违规在合并前被拒绝 |

## 10. 常见问题

**问：一个包内部既放类型又放仓储，会不会违反分层？**

不会。分层按文件判定，不按目录判定。只要 `repository.ts` 不 import `service` 层文件，就是合法的。

**问：`Service` 需要另一个 `Service` 的能力，可以 import 吗？**

可以，但必须无环。如果两个 `Service` 互相需要，说明边界画错了，把共享部分下沉到 `Repo` 或抽成新的 `Service`。

**问：`UI` 需要直接读一个列表，为什么不能直接调 `Repo`？**

因为 `Repo` 不知道租户隔离、字段脱敏、审计与配额。这些装配在 `Runtime` 的组合根里。绕过它等于绕过授权与审计。

**问：新增一个横切能力（例如审计导出），应该放在哪一层？**

先声明接口（`Types` 层），再在平台包内实现（`Repo` 或 `Service` 层，取决于是否含业务规则），最后在 `Runtime` 组合根装配。如果它需要跨团队复用，按第 5 节登记为新的 Provider 接口，并写 ADR。
