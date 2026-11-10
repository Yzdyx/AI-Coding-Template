/**
 * Operator console entry point.
 *
 * Layer: UI. This module renders state and forwards operator actions. It owns
 * no business rule and performs no data access: every value it shows arrives
 * through a `Runtime`-provided interface, and every command it sends goes back
 * through the same interface.
 */

import type { AgentRunSummary, ApprovalRequest, RunStatus } from '@agent-platform/agent-contracts';

/** Interface the Runtime layer implements and injects into the console. */
export interface ConsoleGateway {
  listRuns(limit: number): Promise<readonly AgentRunSummary[]>;
  listPendingApprovals(): Promise<readonly ApprovalRequest[]>;
  approve(requestId: string, operator: string): Promise<void>;
  reject(requestId: string, operator: string, reason: string): Promise<void>;
}

/** Statuses that require an operator decision before the run can continue. */
const DECISION_STATUSES: readonly RunStatus[] = ['awaiting_approval', 'degraded'];

/** Renders one run row. Presentation only. */
export function renderRunRow(run: AgentRunSummary): string {
  const marker = DECISION_STATUSES.includes(run.status) ? '!' : ' ';
  const degraded = run.degraded === true ? ' (degraded)' : '';
  return `${marker} ${run.agent} ${run.status}${degraded} steps=${run.steps}`;
}

/** Renders the approval queue. An empty queue is stated, not implied. */
export function renderApprovalQueue(requests: readonly ApprovalRequest[]): string {
  if (requests.length === 0) {
    return 'No approvals are waiting.';
  }
  return requests
    .map(
      (request) =>
        `#${request.id} ${request.agentId} ${request.tool} risk=${request.risk ?? 'unknown'}`,
    )
    .join('\n');
}

/** Loads and renders the console state through the injected gateway. */
export async function renderConsole(gateway: ConsoleGateway, limit = 50): Promise<string> {
  const [runs, approvals] = await Promise.all([
    gateway.listRuns(limit),
    gateway.listPendingApprovals(),
  ]);

  const sections = [
    `Runs (${runs.length}):`,
    ...runs.map(renderRunRow),
    '',
    `Approvals (${approvals.length}):`,
    renderApprovalQueue(approvals),
  ];

  return sections.join('\n');
}

/** Forwards an operator decision. The gateway applies the authorization rule. */
export async function submitDecision(
  gateway: ConsoleGateway,
  request: ApprovalRequest,
  operator: string,
  approve: boolean,
  reason = '',
): Promise<void> {
  if (approve) {
    await gateway.approve(request.id, operator);
    return;
  }
  if (reason.trim() === '') {
    throw new Error('A rejection requires a reason');
  }
  await gateway.reject(request.id, operator, reason);
}
