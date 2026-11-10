# 技术债跟踪表

本表登记已知但暂不修复的技术债。登记不等于接受现状：每条债务都有负责人、目标季度与清理状态。债务不是抱怨清单，而是有截止日期的待办。

## 1. 债务清单

| 编号 | 领域 | 影响 | 负责人 | 目标季度 | 状态 |
| --- | --- | --- | --- | --- | --- |
| TD-001 | 工具网关 | 判定延迟在极端负载下接近 SLO 预算上限 | `@platform-team` | 2026-Q2 | Open |
| TD-002 | 检索降级 | 降级结果的下游校验尚未在全部消费者落地 | `@research-platform` | 2026-Q2 | In Progress |
| TD-003 | 文档 | `docs/references/` 外部资料缺少版本校验时间戳 | `@architecture-team` | 2026-Q3 | Open |
| TD-004 | 评测 | 回归数据集覆盖缺少多语言输入样本 | `@quality-team` | 2026-Q2 | Open |
| TD-005 | 状态存储 | 本地开发使用内存实现，与生产行为存在差异 | `@platform-team` | 2026-Q3 | Open |
| TD-006 | 前端 | 控制台表格在超大数据量下缺少虚拟滚动 | `@app-team` | 2026-Q3 | Open |
| TD-007 | 依赖规则 | 少数历史文件存在跨包相对引用，尚未迁移到公开入口 | `@architecture-team` | 2026-Q2 | In Progress |
| TD-008 | 观测 | trace 采样率固定，缺少按 run 重要性动态调整 | `@sre-team` | 2026-Q4 | Open |

状态取值：`Open`（已登记，未开始）、`In Progress`（修复中）、`Blocked`（被外部依赖阻塞）、`Done`（已修复，等待归档）、`Won't Fix`（明确不修复，需给出理由）。

## 2. 登记规则

1. 发现债务时，由发现者在评审或 PR 中登记，写明领域、影响与负责人，不允许只留一句口头说明。
2. 每条债务必须有目标季度。无法给出季度说明还没想清楚，应继续拆分。
3. 债务影响 SLO、安全或契约时，优先级高于普通债务，且必须在本季度内处理。
4. 修复债务同样走小步变更：一个债务一个 PR，附验证证据。
5. 债务修复后状态改为 `Done`，并在下一个季度回顾时移出活跃表，保留在历史记录中。

## 3. 优先级判定

| 影响类型 | 处理时限 | 说明 |
| --- | --- | --- |
| 安全或授权 | 立即 | 涉及密钥、权限绕过、数据泄漏，见 [`../SECURITY.md`](../SECURITY.md) |
| SLO 或可靠性 | 本季度 | 影响错误预算，见 [`../RELIABILITY.md`](../RELIABILITY.md) |
| 共享契约 | 本季度 | 影响多个消费者，见 [`../architecture/dependency-rules.md`](../architecture/dependency-rules.md) |
| 质量与评测 | 下季度 | 影响回归发现能力，见 [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) |
| 开发体验 | 下季度或按需 | 影响效率但不影响正确性 |

## 4. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`../PLANS.md`](../PLANS.md) | 债务如何转化为执行计划与归档 |
| [`active/AGENT-1042-improve-retrieval-timeout.md`](active/AGENT-1042-improve-retrieval-timeout.md) | 当前活跃计划，可能产生或消化债务 |
| [`completed/AGENT-1001-tool-gateway-rollout.md`](completed/AGENT-1001-tool-gateway-rollout.md) | 已归档计划，其遗留项在此登记 |
| [`../QUALITY_SCORE.md`](../QUALITY_SCORE.md) | 债务影响领域对应的质量评分 |
| [`../architecture/dependency-rules.md`](../architecture/dependency-rules.md) | 依赖规则豁免与临时偏离的登记要求 |
| [`../../AGENTS.md`](../../AGENTS.md) | 发现范围外问题时的上报要求 |
