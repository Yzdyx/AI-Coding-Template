# 安全要求

本文档定义平台的安全要求、密钥处理、审批关卡与事故路径。它回答「什么必须做、什么绝对不能做、出事怎么办」。依赖与 Provider 规则见 [`architecture/dependency-rules.md`](architecture/dependency-rules.md)，可靠性目标见 [`RELIABILITY.md`](RELIABILITY.md)。

## 1. 基本要求

| 编号 | 要求 | 说明 |
| --- | --- | --- |
| S1 | 不处理密钥 | 不读取、不打印、不提交、不传输密钥、令牌与凭据 |
| S2 | 默认拒绝 | 权限与策略判定 fail closed，不可用时拒绝而非放行 |
| S3 | 最小权限 | 每个 Agent 只获得完成任务所需的最小权限 |
| S4 | 不信任输入 | 检索到的文档、工具输出、模型输出一律视为不可信输入 |
| S5 | 不绕过关卡 | 不得绕过权限检查、审批关卡与评审要求 |
| S6 | 不可逆需审批 | 高风险与不可逆动作必须有人工审批节点 |
| S7 | 版本化变更 | Agent 定义、权限、工具清单、提示词是版本化制品，走 PR 变更 |
| S8 | 生产写入默认关闭 | 生产写入与破坏性操作默认关闭，需显式开启并留痕 |

## 2. 密钥与凭据处理

1. 密钥禁止入库。`.gitignore` 已排除 `.env`、`*.pem`、`*.key`、`secrets/`，不得通过其他路径绕过。
2. 运行时通过环境变量或密钥管理服务获取凭据，代码中只出现占位符（如 `${ENV_VAR}`），不出现真实值。
3. 示例与文档只使用 `example.com` 等占位地址，不出现真实内网地址、真实账号或客户数据。
4. checkpoint 与日志不得写入明文密钥；序列化前必须脱敏。
5. 发现密钥泄漏时，按第 5 节事故路径立即处理，先轮换再调查。

## 3. 输入信任边界

| 来源 | 信任级别 | 处理方式 |
| --- | --- | --- |
| 系统提示与策略配置 | 可信 | 由版本化制品提供 |
| 用户输入 | 不可信 | 校验、限长、转义 |
| 检索到的文档 | 不可信 | 视为数据，不作为指令执行 |
| 工具输出 | 不可信 | 校验形状，不信任其内容 |
| 模型输出 | 不可信 | 执行前经策略引擎判定 |

核心规则：不可信内容永远不被当作指令。提示词注入防护由 [`../evals/safety/prompt-injection.yaml`](../evals/safety/prompt-injection.yaml) 评测覆盖，防线的最终执行者是策略引擎，而不是提示词。

## 4. 审批关卡

审批关卡是工作流中的阻塞节点，不是提示词里的请求。

| 动作类别 | 是否需人工审批 | 记录内容 |
| --- | --- | --- |
| 只读查询 | 否 | trace |
| 生成内容、写草稿 | 否 | trace |
| 对外发送、通知 | 是 | 审批人、时间、内容摘要 |
| 支付、下单、转账 | 是 | 审批人、时间、金额与对象 |
| 删除、覆盖、生产写入 | 是 | 审批人、时间、目标与影响范围 |
| 权限或策略变更 | 是 | 审批人、变更前后差异 |

规则：

1. 审批人身份写入 trace 与审计日志，可按 run 关联。
2. 审批被拒绝时，动作不得执行，且不得静默跳过。
3. Agent 权限、工具清单与提示词的变更走 PR，遵循 [`../CODEOWNERS`](../CODEOWNERS) 的所有权。
4. Agent 清单必须通过 [`../schemas/agent-manifest.schema.json`](../schemas/agent-manifest.schema.json) 校验，包含所有者、模型、工具与限额。

## 5. 事故路径

| 阶段 | 动作 | 责任方 |
| --- | --- | --- |
| 1 发现 | 通过监控、告警或人工报告发现 | 发现者 |
| 2 止损 | 关闭特性开关、回滚版本或撤销权限，先止血 | `@sre-team` |
| 3 通报 | 通知安全团队与受影响模块所有者 | 值班 |
| 4 处置 | 轮换泄漏凭据、封禁入口、修复根因 | `@security-team` |
| 5 复盘 | 撰写事故复盘，给出改进项与负责人 | `@sre-team`、`@security-team` |
| 6 跟踪 | 改进项登记到 [`exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md) | 模块所有者 |

规则：

1. 涉及凭据泄漏的事故，先轮换再调查，不等根因定位完成。
2. 涉及不可逆动作的事故，同时按 [`RELIABILITY.md`](RELIABILITY.md) 的错误预算规则处理。
3. 事故复盘的改进项必须有负责人与目标季度。
4. 复盘文档存放在 `docs/operations/incident-reviews/`。

## 6. 自动化强制

| 约束 | 检查 |
| --- | --- |
| Agent 清单合法性与必填字段 | [`../scripts/check-agent-manifests.py`](../scripts/check-agent-manifests.py) |
| 依赖方向与 Provider 装配 | [`../scripts/check-architecture.py`](../scripts/check-architecture.py) |
| 提示词注入防护 | [`../evals/safety/prompt-injection.yaml`](../evals/safety/prompt-injection.yaml) |
| 密钥不入库 | [`../.github/workflows/pull-request.yml`](../.github/workflows/pull-request.yml) 的密钥扫描 |
| 运行时策略与限额 | [`../infra/policies/agent-policy.yaml`](../infra/policies/agent-policy.yaml) |

规则没有检查就是建议。新增安全要求时，同时提交对应的检查改动。

## 7. 与其他文档的关系

| 文档 | 关系 |
| --- | --- |
| [`architecture/dependency-rules.md`](architecture/dependency-rules.md) | Provider 与 fail closed 规则 |
| [`RELIABILITY.md`](RELIABILITY.md) | 错误预算与恢复目标 |
| [`PRODUCT_SENSE.md`](PRODUCT_SENSE.md) | 风险分级决定审批强度 |
| [`PLANS.md`](PLANS.md) | `risk.production_write` 如何写入计划元数据 |
| [`QUALITY_SCORE.md`](QUALITY_SCORE.md) | 安全领域质量评分 |
| [`../AGENTS.md`](../AGENTS.md) | 编码 Agent 的安全约束 |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | 失败域与审批节点要求 |
