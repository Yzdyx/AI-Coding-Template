# 威胁模型

本文档列出本平台的威胁、信任边界与缓解措施。架构细节见 [`security-architecture.md`](security-architecture.md)，工程要求见 [`../SECURITY.md`](../SECURITY.md)。

## 1. 资产

| 资产 | 泄露或篡改的后果 |
| --- | --- |
| 租户数据 | 隐私与合规违规 |
| 工具凭据 | 第三方系统被越权操作 |
| 提示词与工具契约 | 行为被外部操纵 |
| 审计记录 | 事后无法追责 |
| 评测基线与数据集 | 质量回退无法被识别 |

## 2. 威胁清单

| 编号 | 威胁 | 场景 | 缓解 | 检查位置 |
| --- | --- | --- | --- | --- |
| T1 | 提示注入 | 检索到的文档或工具输出携带指令，改变 Agent 行为 | 把外部内容标记为不可信；系统提示词声明边界；工具参数校验 | [`../../.agents/skills/security-review/SKILL.md`](../../.agents/skills/security-review/SKILL.md) |
| T2 | 越权工具调用 | Agent 调用未在清单中声明的工具 | 清单白名单；策略引擎失败即拒 | [`../../schemas/agent-manifest.schema.json`](../../schemas/agent-manifest.schema.json) |
| T3 | 重复副作用 | 重试导致重复付款、重复发送、重复删除 | 每个副作用工具调用携带幂等键 | [`../../packages/state-store/`](../../packages/state-store/) |
| T4 | 跨租户读取 | 查询缺少租户过滤，或租户标识由调用方提供 | 租户标识在数据访问层强制注入 | [`../../packages/state-store/src/repository.ts`](../../packages/state-store/src/repository.ts) |
| T5 | 凭据泄露 | 密钥写入代码、日志或测试夹具 | 密钥只经环境变量注入；日志脱敏；提交前扫描 | [`../../.codex/hooks/post-edit-lint.sh`](../../.codex/hooks/post-edit-lint.sh) |
| T6 | 检查被削弱 | 为让变更通过而放宽断言或关闭策略 | 检查改动需要独立评审；规则变更需 ADR | [`../../CODEOWNERS`](../../CODEOWNERS) |
| T7 | 供应链 | 新增未固定版本或来源不明的依赖 | 版本固定；新增依赖类别需要 ADR | [`../../.agents/skills/review-architecture/SKILL.md`](../../.agents/skills/review-architecture/SKILL.md) |
| T8 | 审计缺失 | 高风险动作未留痕 | 高风险动作必须经审批节点并写审计 | [`security-architecture.md`](security-architecture.md) |
| T9 | 状态恢复导致重复执行 | 崩溃后从检查点恢复时重放副作用 | 检查点加幂等键，必要时补偿流程 | [`../RELIABILITY.md`](../RELIABILITY.md) |
| T10 | 模型提供方变更 | 外部模型行为变化导致输出漂移 | 固定评测样例与基线；记录模型版本 | [`../../evals/baselines/baseline-2026-01.json`](../../evals/baselines/baseline-2026-01.json) |

## 3. 信任边界

与 [`security-architecture.md`](security-architecture.md) 第 1 节一致。任何跨越边界的输入都按不可信处理，包括：用户输入、检索结果、工具返回值、外部系统的回调。

## 4. 未覆盖

| 项 | 说明 |
| --- | --- |
| 物理安全 | 由基础设施提供方负责 |
| 终端安全 | 由企业终端管理负责 |
| 模型内部机制 | 平台不假设模型行为可解释，只通过评测与约束控制风险 |

## 5. 维护规则

1. 新增一个外部数据来源、一个新工具类别或一个新 Provider 时，同步更新本表。
2. 每条缓解措施必须指向一个可执行的位置：检查脚本、策略文件、测试或清单字段。
3. 只有描述、没有对应位置的缓解措施视为未实施。
