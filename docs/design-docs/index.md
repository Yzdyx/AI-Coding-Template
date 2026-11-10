# 设计文档索引

本目录保存**设计意图与工程信念**，回答「为什么这样设计」。它不描述系统当前的实现细节；系统边界、分层与依赖方向以 [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) 为准，产品需求以 [`../product-specs/index.md`](../product-specs/index.md) 为准。

## 1. 设计文档清单

| 文档 | 回答的问题 | 状态 | 维护者 |
| --- | --- | --- | --- |
| [`core-beliefs.md`](core-beliefs.md) | 平台的六条核心设计信念及其理由 | Stable | `@architecture-team` |
| [`../DESIGN.md`](../DESIGN.md) | 设计原则与设计评审标准 | Stable | `@architecture-team` |
| [`../FRONTEND.md`](../FRONTEND.md) | 前端约定、设计 token、可访问性、状态管理 | Active | `@app-team` |
| [`../PLANS.md`](../PLANS.md) | 执行计划的写法、元数据格式与生命周期 | Stable | `@platform-team` |
| [`../PRODUCT_SENSE.md`](../PRODUCT_SENSE.md) | 产品决策方式与风险分级 | Stable | `@product-team` |
| [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) | 各领域质量评分与评分规则 | Active | `@quality-team` |

状态取值：`Draft`（起草中，可大幅变动）、`Active`（正在使用，随实践更新）、`Stable`（稳定，变更需设计评审）、`Deprecated`（已废弃，保留供追溯）。

## 2. 阅读顺序

不同角色只需要加载自己需要的部分。这是「渐进式上下文加载」信念的直接应用。

| 顺序 | 读者 | 建议阅读 |
| --- | --- | --- |
| 1 | 所有人 | [`core-beliefs.md`](core-beliefs.md)，先理解信念，再理解规则 |
| 2 | 修改代码的人 | [`../DESIGN.md`](../DESIGN.md)、[`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) |
| 3 | 前端开发 | [`../FRONTEND.md`](../FRONTEND.md) |
| 4 | 任务负责人 | [`../PLANS.md`](../PLANS.md)、[`../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) |
| 5 | 产品与需求方 | [`../PRODUCT_SENSE.md`](../PRODUCT_SENSE.md)、[`../product-specs/index.md`](../product-specs/index.md) |

## 3. 设计文档与规则文档的分工

| 类型 | 位置 | 回答的问题 | 变更方式 |
| --- | --- | --- | --- |
| 设计意图 | `docs/design-docs/`、[`../DESIGN.md`](../DESIGN.md) | 为什么这样设计 | 设计评审 |
| 系统结构 | [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)、[`../architecture/index.md`](../architecture/index.md) | 系统由什么组成、依赖指向哪 | 架构评审，必要时写 ADR |
| 产品需求 | [`../product-specs/index.md`](../product-specs/index.md) | 要交付什么、如何验收 | 随需求版本更新 |
| 执行计划 | [`../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md`](../exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | 这次任务怎么做、做到哪 | 任务推进时更新，结束后归档 |
| 质量与风险 | [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md)、[`../RELIABILITY.md`](../RELIABILITY.md)、[`../SECURITY.md`](../SECURITY.md) | 现在质量如何、边界在哪 | 质量与安全评审 |

设计意图与系统结构必须彼此一致。如果一条设计信念要求某种结构，而 [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) 没有体现，二者之一必须修改，且在同一次评审中完成。

## 4. 维护规则

1. 设计文档与代码在同一个 PR 内更新。设计变了而文档没变，等同于设计没有生效。
2. 设计文档只写结论与理由，不写具体实现。实现细节属于代码与 [`../exec-plans/tech-debt-tracker.md`](../exec-plans/tech-debt-tracker.md)。
3. 每条设计信念必须可被检验。无法判断「是否违反」的表述不写进设计文档。
4. 新增设计文档时，在本页登记状态与维护者；废弃文档时保留条目并标记 `Deprecated`，不直接删除。
5. 文档相对链接由 [`../../scripts/check-doc-links.py`](../../scripts/check-doc-links.py) 校验，禁止悬空链接。

## 5. 相关入口

| 入口 | 用途 |
| --- | --- |
| [`../../AGENTS.md`](../../AGENTS.md) | 编码 Agent 的仓库导航与基本约束 |
| [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) | 系统边界、六层划分、失败域 |
| [`../architecture/dependency-rules.md`](../architecture/dependency-rules.md) | 允许与禁止的依赖边 |
| [`../product-specs/index.md`](../product-specs/index.md) | 产品规格索引 |
| [`../PLANS.md`](../PLANS.md) | 执行计划的生命周期 |
