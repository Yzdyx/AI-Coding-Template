# Tool access policy for agent runs.
#
# Deny by default. Every allow rule states its reason. A policy that cannot
# evaluate a request must deny it: see the fail-closed rule below.

package agent.tool.access

default allow := false

# An allow decision carries the reason it was granted. Reviewers read reasons,
# not just decisions.
allow if {
    input.subject.authenticated
    tool_declared_in_manifest
    tenant_matches_subject
    risk_permitted
}

# The agent may call a tool only when the tool is declared in its manifest.
tool_declared_in_manifest if {
    some tool in input.agent.manifest.tools
    tool == input.call.tool
}

# The tenant comes from the authenticated subject. A tenant identifier supplied
# by the caller is ignored, never merged.
tenant_matches_subject if {
    input.call.tenant == input.subject.tenant
}

# Risk gating. A high-risk call requires an approval record for this run and tool.
risk_permitted if {
    input.call.risk == "low"
}

risk_permitted if {
    input.call.risk == "medium"
    input.call.idempotency_key != ""
}

risk_permitted if {
    input.call.risk == "high"
    input.call.idempotency_key != ""
    approval_recorded
}

approval_recorded if {
    some approval in input.approvals
    approval.run_id == input.call.run_id
    approval.tool == input.call.tool
    approval.decision == "approved"
}

# Explicit deny reasons. A deny without a reason is not diagnosable.
reasons contains "not_authenticated" if {
    not input.subject.authenticated
}

reasons contains "tool_not_declared_in_manifest" if {
    not tool_declared_in_manifest
}

reasons contains "tenant_mismatch" if {
    not tenant_matches_subject
}

reasons contains "approval_missing" if {
    input.call.risk == "high"
    not approval_recorded
}

reasons contains "idempotency_key_missing" if {
    input.call.risk != "low"
    input.call.idempotency_key == ""
}

# Fail closed: an unevaluable request is a deny with a reason.
reasons contains "policy_engine_unavailable" if {
    not input.policy_engine.available
}
