# 20. Operator Daily Control Loop

## Purpose

This document defines the daily control loop for the operator responsible for multi-chat execution flow inside the orchestrator factory.

The loop does not replace run planning, round planning, or package execution. It keeps the coordination plane healthy while those activities happen.

The operator works through these files:

- `configs/execution_framework/chat_topology.json`
- `configs/execution_framework/chat_capability_matrix.json`
- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/handoff_policy.json`
- `configs/execution_framework/escalation_matrix.json`
- `configs/execution_framework/blocker_taxonomy.json`
- `configs/execution_framework/sync_cadence.json`
- `configs/execution_framework/operator_dashboard_views.json`
- `schemas/execution_framework/chat_message.schema.json`
- `schemas/execution_framework/handoff_ticket.schema.json`

## Control-loop principle

The operator's job is not to do package work. The operator's job is to preserve deterministic flow.

That means the operator continuously answers:

1. Is every active item owned by exactly one chat
2. Is every active chat current enough to trust
3. Is every blocked item classified and pointed at a next action owner
4. Is every cross-package need flowing through a governed contract
5. Is integration timing safe

## Recommended daily rhythm

A day should be run as repeated cycles, not as one giant review pass.

### Opening cycle

At the beginning of the operating window:

1. load the coordination overview
2. confirm all active chats and their owned package identifiers
3. inspect silence and cadence
4. inspect blocker pressure
5. inspect the handoff queue
6. inspect dependency flow
7. inspect merge-window readiness if integration is planned
8. publish or refresh a coordination snapshot if state is stale

The opening cycle establishes whether the control plane is trustworthy enough to begin the day.

### Steady-state cycle

During the work window, repeat a smaller loop.

1. review silent or stale chats
2. review new blockers
3. review overdue handoffs
4. review overdue dependency responses
5. review status transitions with missing checkpoints
6. decide whether a new escalation event is required
7. update the coordination snapshot when the global picture changed materially

The operator should not wait for chaos before looking again. The control loop works because it is frequent and narrow.

### Closing cycle

Near the end of the operating window:

1. review all open `sev1` and `sev2` items
2. confirm the latest owner and next action for every blocked item
3. verify the handoff queue has no unacknowledged critical tickets
4. verify integration timing for the next window
5. publish a coordination snapshot that makes the next operator or next cycle safe to resume

The closing cycle protects continuity.

## The five operator dashboards

The operator dashboard configuration formalizes five perspectives that should be reviewed in order.

### 1. Coordination overview

Use this view first. It answers whether the system is legible right now.

The operator should scan for:

- chats pinned as blocked
- chats whose heartbeat age exceeds warning thresholds
- chats with no recent progress
- items with protocol drift after a status-changing event

### 2. Blocker pressure

Use this to rank active risks.

The operator should scan for:

- all `sev1` and `sev2` blockers
- aging blockers past due time
- blockers missing a next action owner
- blockers that affect merge timing

### 3. Handoff queue

Use this to inspect cross-chat obligations.

The operator should scan for:

- overdue acknowledgements
- accepted tickets without checkpoints
- done tickets without evidence
- tickets with weak acceptance criteria

### 4. Dependency flow

Use this to see whether external needs are moving or stalling.

The operator should scan for:

- requests nearing due time
- requests with no response
- dependency chains attached to open blockers
- repeated requests that should become a stronger routing decision

### 5. Merge-window readiness

Use this whenever integration is possible in the same work cycle.

The operator should scan for:

- packages marked done but still carrying open blockers
- packages with open handoffs or dependencies that affect readiness
- packages missing evidence even though they claim completion
- cross-package collision signs before the window opens

## Operator actions by signal

### Silent chat signal

When a chat is silent beyond `warn_after`:

1. record the warning in the next coordination snapshot
2. check whether status-changing events lacked checkpoints
3. inspect whether the current items are at risk

When a chat is silent beyond `escalate_after`:

1. treat it as control-plane risk
2. open the required attention item according to cadence policy
3. consider whether ownership must be rerouted to protect the round

### New blocker signal

When a blocker lands:

1. confirm the blocker type
2. assign severity
3. name the next action owner
4. link any dependency or handoff records
5. decide whether escalation is required immediately

### Weak handoff signal

When a handoff lacks acceptance criteria, due time, or evidence discipline:

1. request revision or reject the ticket
2. do not allow the queue to absorb malformed work
3. preserve the audit trail so the sender can fix the ticket cleanly

### Cross-package drift signal

When package work starts crossing ownership without a governed ticket:

1. stop informal routing
2. convert the need into a dependency or handoff
3. publish the governing decision through mission control

### Integration-risk signal

When packages appear ready but blockers or evidence gaps still exist:

1. hold the merge window decision
2. require the missing evidence or blocker resolution
3. publish the updated readiness state before integration proceeds

## Snapshot policy

The coordination snapshot is the operator's strongest tool for resetting shared understanding.

Refresh the snapshot when:

- a `sev1` or `sev2` blocker opens or closes
- ownership moves across chats
- a merge window opens or materially changes
- multiple chats moved state since the last snapshot
- silence risk changes the trustworthiness of the overall picture

A stale snapshot is dangerous because it lets local truths diverge from the global truth.

## Escalation discipline

The operator should escalate because the matrix requires it, not because the moment feels dramatic.

Good escalation discipline means:

- using blocker type and severity together
- recording the required action
- setting the resolution owner
- enforcing the checkpoint frequency
- closing the escalation only with evidence

Escalation should reduce ambiguity, not increase noise.

## What the operator should never do

The operator should not:

- take over package execution by default
- allow direct peer-to-peer package routing outside the governed channels
- close blockers or handoffs without evidence
- treat heartbeats as optional
- open merge windows because work sounds complete without checking the readiness view
- let contradictory instructions persist across cycles

## Minimum artifacts to keep current

At all times, the operator should be able to point to the latest valid versions of:

- latest heartbeats
- latest sync checkpoints
- open blocker reports
- open handoff tickets
- active dependency requests and responses
- current escalation events
- current coordination snapshot
- active merge-window decisions

If any of these are missing, the operator is no longer running a controlled system.

## Healthy day outcome

A healthy operator day ends with:

- no invisible ownership gaps
- no untracked severe blockers
- no critical stale chats
- no malformed handoffs in the queue
- no unsafe merge-window decisions
- a fresh enough coordination snapshot to resume confidently

The daily control loop exists to maintain execution stability without improvisation. That is the standard the operator should hold all day long.
