<!-- agent-workbench-rescue-managed -->
# Coordination Lock

## Coordinator-Only Files

Only the Coordinator may edit:

- MASTER_STATUS_BOARD.md
- PARALLEL_WORK_QUEUE.md
- HANDOFF_PROMPTS.md
- AGENT_REPORT_RECONCILIATION.md
- MERGE_READINESS_CHECKLIST.md
- COORDINATION_LOCK.md
- AGENT_SESSION_LEDGER.md
- EVIDENCE_POLICY.md
- STATE_TRANSITIONS.md

Agents must treat these as read-only.

## Agent Ownership

Each agent may write only inside:

    docs/dev/agent-workbench/agents/<agent>/

## Stale Agent Rule

If an agent stops updating or produces conflicting output, the Coordinator may mark it BLOCKED, NEEDS_UPDATE, or DO_NOT_MERGE depending on reconciliation status.
