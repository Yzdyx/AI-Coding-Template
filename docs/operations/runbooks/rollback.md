# 运行手册：回滚

## 触发信号

- 发布后错误率超过回滚阈值。
- P95 延迟超过性能预算。
- 安全红线用例失败。
- 部署的镜像 digest 与已验证的 digest 不一致。

## 1. 确认回滚目标

1. 读发布记录，取上一个已验证版本。
2. 确认该版本的镜像 digest 存在且可拉取。
3. 确认该版本对应的 Agent 清单版本与提示词哈希。

回滚目标不存在时，停止操作，升级到 `@sre-team`。

## 2. 回滚应用

```bash
kubectl -n platform set image deploy/agent-api agent-api=<previous-digest>
kubectl -n platform rollout status deploy/agent-api
```

1. 观察 5 分钟：错误率、P95、队列深度。
2. 回滚 `worker` 时使用同一 digest 系列，避免应用与 worker 版本错配。

## 3. 回滚基础设施

```bash
terraform -chdir=infra/environments/prod plan
terraform -chdir=infra/environments/prod apply
```

1. 先读 plan，确认只有预期变更。
2. 涉及数据库迁移时，回滚前确认迁移是向后兼容的。破坏性迁移不回滚，改用前滚修复。

## 4. 处理进行中的任务

1. 处于运行中的任务会读到旧版检查点。确认检查点格式向后兼容。
2. 不兼容时，把在途任务标记为失败并记录 run 事件，由业务侧重新提交。
3. 不要手工修改数据库中的任务状态。

## 5. 验证恢复

| 项目 | 预期 |
| --- | --- |
| 部署版本 | 等于回滚目标 digest |
| 错误率 | 回落到基线 |
| P95 | 回到预算内 |
| 在途任务 | 不再增加失败 |
| 冒烟评测 | 通过 |

## 停止条件与升级

- 回滚后指标不恢复：问题不在本次发布，转 [`agent-api-degradation.md`](agent-api-degradation.md)。
- 需要回滚数据库：停止，升级到 `@sre-team` 与数据所有者。

## 事后

1. 记录回滚原因、时间与操作人。
2. 把导致回滚的用例补进 [`../../evals/regression/`](../../../evals/regression/)。
3. 若门槛设置不合理，按 [`../../../.agents/skills/release-check/SKILL.md`](../../../.agents/skills/release-check/SKILL.md) 修正基线。
