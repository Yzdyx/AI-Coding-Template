# 运行手册：agent-api 降级

## 触发信号

下列任一信号触发本手册：

| 信号 | 来源 | 阈值 |
| --- | --- | --- |
| 错误率 | `agent_api_requests_total{status=~"5.."}` | 见 [`../../RELIABILITY.md`](../../RELIABILITY.md) |
| P95 延迟 | `agent_api_request_duration_seconds` | 见 [`../../RELIABILITY.md`](../../RELIABILITY.md) |
| 依赖不可用 | `tool_gateway_up` | 连续 2 分钟为 0 |
| 任务积压 | `worker_queue_depth` | 持续增长且无消费 |

## 1. 确认影响面

1. 查当前版本：`kubectl -n platform get deploy agent-api -o jsonpath='{.spec.template.spec.containers[0].image}'`。预期输出为一个镜像 digest。
2. 查错误分布：按 `status` 与 `route` 分组，确认是全站还是单路由。
3. 查依赖状态：`tool_gateway_up`、`state_store_up`、`model_provider_up`。

若只有单路由异常，跳到第 3 节。若依赖为 0，跳到第 4 节。

## 2. 判断是否与本次发布相关

1. 查发布记录：`git log --oneline -1` 与当前镜像 digest 对应的提交。
2. 若当前版本在最近 30 分钟内发布，按 [`rollback.md`](rollback.md) 回滚。
3. 若不是本次发布引入，按第 3 节定位。

## 3. 定位单路由异常

1. 取一条失败请求的 `trace_id`：在日志中查 `level=error` 的最近一条记录。
2. 用 `trace_id` 拉取完整调用链，确认失败发生在哪个步骤：配置、策略、工具、模型。
3. 策略拒绝导致的失败不是故障。检查 `policy_decision{result="deny"}` 是否同步上升。
4. 工具超时导致的失败按降级路径处理，确认返回体带有 `degraded` 标记。

## 4. 依赖不可用

1. 工具网关不可用：`kubectl -n platform rollout status deploy/tool-gateway`。
2. 状态存储不可用：检查连接池耗尽与慢查询。
3. 模型提供方不可用：切换到已批准的备用提供方配置，不要修改 Agent 清单。

## 5. 缓解与恢复

1. 扩大副本：`kubectl -n platform scale deploy/agent-api --replicas=<n>`。
2. 暂停非关键任务来源，保住交互式请求的容量。
3. 恢复后确认：错误率回落、P95 回到预算内、积压开始下降。

## 停止条件与升级

出现下列任一情况，停止自助处置并升级到 `@sre-team`：

- 需要修改 `infra/environments/prod/` 才能缓解。
- 疑似数据越权或数据泄露。
- 回滚后问题仍存在。

## 事后

1. 在 `docs/operations/incident-reviews/` 新建复盘。
2. 把可自动化的判定写进检查或告警，而不是写进提示词。
