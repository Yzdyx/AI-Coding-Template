# 设计原则与评审标准

本文档定义平台的设计原则，以及设计评审的判定标准。它回答「一个设计好不好，怎么判断」。设计信念与理由见 [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md)，系统结构见 [`architecture/index.md`](architecture/index.md)。设计意图与系统结构必须彼此一致；二者冲突时，先在设计评审中解决，再改代码。

## 1. 适用范围

| 项目 | 说明 |
| --- | --- |
| 适用 | 跨模块改动、新增模块或 Provider、修改共享契约、改变分层、新增对外接口、前端交互与信息架构 |
| 不适用 | 局部实现细节、命名、格式、测试组织、不影响其他模块的重构 |
| 裁决 | 原则解释设计取向，[`../scripts/check-architecture.py`](../scripts/check-architecture.py) 与契约测试判定硬约束 |
| 评审者 | 一般设计由 `@architecture-team` 评审；涉及安全边界由 [`SECURITY.md`](SECURITY.md) 补充要求 |

## 2. 设计原则

| 编号 | 原则 | 含义 | 违反的典型信号 |
| --- | --- | --- | --- |
| P1 | 单一职责 | 一个模块、包或层只承担一类职责 | 一个文件同时做校验、持久化与展示 |
| P2 | 显式优于隐式 | 依赖、配置、失败语义都显式声明 | 靠约定或魔法字符串决定行为 |
| P3 | 边界可检查 | 每个重要边界都有机器检查 | 规则只写在文档里，没有检查 |
| P4 | 失败可定位 | 失败能通过 trace 与日志定位到具体步骤 | 出错只有一句通用错误 |
| P5 | 可替换 | 外部能力通过 Provider 接口注入 | `Service` 直接 `new` 具体实现 |
| P6 | 最小改动 | 用最小改动满足任务，不搭车重构 | 借修 bug 做全仓库重命名 |
| P7 | 可回滚 | 每个改动都有回滚路径 | 发布后无法恢复上一版本 |
| P8 | 默认安全 | 生产写入与破坏性操作默认关闭 | 危险动作默认开启，靠人记得关 |

原则之间存在张力时，优先级为：安全（P8）> 可定位与可回滚（P4、P7）> 边界与可替换（P3、P5）> 其余。当 P8 与其他原则冲突，先满足 P8。

## 3. 设计评审标准

评审时逐条核对。任何一条为「否」都需要解释，并在 [`PLANS.md`](PLANS.md) 描述的决策日志中记录取舍。

| 编号 | 检查项 | 通过标准 |
| --- | --- | --- |
| C1 | 职责是否单一 | 每个新增单元只有一类职责，名称能准确描述它 |
| C2 | 依赖方向是否合法 | 遵守 [`architecture/dependency-rules.md`](architecture/dependency-rules.md)，无越层与跨包深层引用 |
| C3 | 是否复用了既有模块 | 没有为已有职责新建平行模块 |
| C4 | 边界是否有检查 | 新增强制边界同时新增检查，见 [`architecture/index.md`](architecture/index.md) 第 5 节 |
| C5 | 契约变更是否兼容 | 破坏性变更需 ADR 与全消费者同步；否则只做新增可选字段 |
| C6 | 失败是否可定位 | 关键路径有 trace，错误可分类 |
| C7 | 是否可回滚 | 改动有明确回滚方式与回滚触发条件 |
| C8 | 是否默认安全 | 生产写入与破坏性操作默认关闭，需显式开启 |
| C9 | 是否最小改动 | 改动限制在任务声明的 `scope.paths` 内 |
| C10 | 文档是否同步 | 设计、结构、规则文档在同一 PR 内更新 |

## 4. 评审流程

1. 作者在 PR 中说明：改了什么、为什么、影响哪些契约、如何验证。
2. 评审者按第 3 节清单逐项核对，指出不满足项与建议。
3. 命中以下情形时，先写 ADR 再实施：破坏性契约变更、新增或删除 Provider、新增顶层目录、改变分层、把模块提升为独立服务。
4. 涉及安全边界、授权、密钥或数据分类的改动，由 `@security-team` 会签，见 [`SECURITY.md`](SECURITY.md)。
5. 涉及前端交互与信息架构的改动，同时满足 [`FRONTEND.md`](FRONTEND.md) 的约定。
6. 评审通过后合并；[`../scripts/check-doc-links.py`](../scripts/check-doc-links.py) 与 [`../scripts/check-architecture.py`](../scripts/check-architecture.py) 必须在 CI 中通过。

## 5. 设计原则的落地检查

原则不是口号，每条都对应一种可观察的证据。

| 原则 | 落地证据 | 位置 |
| --- | --- | --- |
| P1 单一职责 | 模块布局一致，名称与职责匹配 | `agents/<name>/`、`packages/<name>/` |
| P2 显式优于隐式 | 配置项与 Provider 接口显式声明 | [`architecture/dependency-rules.md`](architecture/dependency-rules.md) |
| P3 边界可检查 | 仓库级检查脚本 | [`../scripts/check-architecture.py`](../scripts/check-architecture.py) |
| P4 失败可定位 | 端到端 trace | `packages/observability/` |
| P5 可替换 | 组合根装配 Provider | `apps/*/src/index.ts` |
| P6 最小改动 | 任务元数据 `scope.paths` | [`PLANS.md`](PLANS.md) |
| P7 可回滚 | 按模块独立发布与回滚 | `.github/workflows/release.yml` |
| P8 默认安全 | 审批节点与默认关闭 | [`SECURITY.md`](SECURITY.md) |

## 6. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`design-docs/index.md`](design-docs/index.md) | 设计文档索引 |
| [`design-docs/core-beliefs.md`](design-docs/core-beliefs.md) | 设计信念，本文档原则的来源 |
| [`architecture/index.md`](architecture/index.md) | 系统结构，与本文档原则互相约束 |
| [`FRONTEND.md`](FRONTEND.md) | 前端设计约定 |
| [`PRODUCT_SENSE.md`](PRODUCT_SENSE.md) | 产品决策与风险分级 |
| [`PLANS.md`](PLANS.md) | 决策日志与执行计划格式 |
| [`QUALITY_SCORE.md`](QUALITY_SCORE.md) | 各领域质量评分 |
| [`RELIABILITY.md`](RELIABILITY.md) | 可靠性目标 |
| [`SECURITY.md`](SECURITY.md) | 安全要求与审批关卡 |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | 系统边界与分层 |
| [`../AGENTS.md`](../AGENTS.md) | 编码 Agent 的仓库导航 |
