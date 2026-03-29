# 21. One-Page Operator Flow

## Purpose

This document compresses the control-plane operating model into one deterministic flow that the operator can execute without re-deriving the framework every time.

Use this document as the short-form companion to:

- `docs/parallel_execution/17_chat_coordination_model.md`
- `docs/parallel_execution/18_handoff_queue_protocol.md`
- `docs/parallel_execution/19_blocker_escalation_playbook.md`
- `docs/parallel_execution/20_operator_daily_control_loop.md`
- `docs/parallel_execution/22_install_bootstrap_run_boundaries.md`
- `docs/parallel_execution/23_inter_chat_communication_policy.md`
- `docs/parallel_execution/24_exception_and_waiver_policy.md`
- `docs/parallel_execution/26_go_live_readiness_gates.md`

## The operator mission

The operator does not perform package work.

The operator keeps the system legible and moving by forcing every active item to have:

1. one visible owner
2. one legal channel
3. one current state
4. one next action owner when blocked
5. enough evidence to trust the next decision

## Fast path

Run the following sequence in order.

### 1. Preflight the round

Confirm that the round exists and that the coordination plane can be trusted before interpreting any signal.

Required checks:

- run root exists under `ops/runs/<run_id>`
- round root exists under `ops/runs/<run_id>/rounds/<round_id>`
- `round_manifest.json` exists and names the intended package set
- active package ids still match `configs/execution_framework/system_config.json`
- package ownership still matches `configs/execution_framework/path_policies.json`

If any of those checks fail, do not begin coordination. Treat the issue as infrastructure or scope depending on the first blocking cause.

### 2. Bootstrap once

If the round has no coordination directory yet, bootstrap it.

Expected result:

- `coordination/channels/`
- `coordination/snapshots/`
- `coordination/views/`
- an additive plane manifest
- zero mutation of framework source files

Bootstrap is idempotent. Re-running bootstrap is safe when the structure already exists.

### 3. Confirm liveness

Before trusting deeper state, confirm that chats are current enough to be acted on.

Read, in order:

- heartbeat freshness
- latest checkpoint by chat
- silent chats above warning threshold
- silent chats above escalation threshold

The operator should assume stale state is untrusted state.

### 4. Triage blockers before anything else

If `sev1` or `sev2` blockers exist, they outrank routine progress reporting.

The operator must answer:

- who owns the blocker right now
- what package ids are impacted
- what next action owner is named
- whether escalation is already published
- whether the blocker threatens a merge window or dependency due time

If those answers are incomplete, the blocker record itself is incomplete and must be corrected before other scheduling choices are made.

### 5. Keep cross-package work governed

Any cross-package need must appear as one of the following:

- `handoff_ticket`
- `dependency_request`
- `dependency_response`
- `escalation_event`

Do not accept narrative chat updates as a substitute for a governed contract. If the need crosses ownership and no contract exists, open one.

### 6. Refresh the global picture

A coordination snapshot is required whenever any of the following change materially:

- a new blocker opens
- a blocker escalates
- a handoff becomes overdue
- a dependency misses its due time
- a waiver is approved, denied, or revoked
- a merge window is scheduled, changed, or invalidated
- a silent chat crosses a warning or escalation threshold

The snapshot is the operator's ground truth for the round, not the chat transcript.

### 7. Protect integration timing

Do not open or preserve a merge window by optimism.

A merge window is safe only when:

- target packages have current checkpoints
- no open `sev1` or `sev2` blockers threaten the target set
- any waiver linked to the target set is explicit, bounded, and unexpired
- readiness evidence exists for the target packages
- the integration order is deterministic

### 8. Close the cycle cleanly

At the end of the cycle or handoff to another operator:

- publish or refresh the latest coordination snapshot
- make sure every open blocker has a next action owner
- make sure every overdue dependency or handoff is visible
- record every active waiver and its expiry
- record the next control action in plain language

## Decision ladder

When multiple things look urgent, choose in this order:

1. unsafe integration risk
2. `sev1` blockers
3. stale or silent chats that make state untrustworthy
4. overdue dependencies and handoffs
5. merge-window collisions
6. routine progress updates

## The operator should never do these things

- merge peer-to-peer package coordination into private chat behavior
- treat a missing heartbeat as acceptable without writing it down
- accept a waiver that has no expiry, no owner, or no rollback plan
- allow a blocked item to survive without a named next action owner
- let a merge window stand on stale checkpoints
- rely on memory instead of the latest coordination snapshot

## Minimum evidence set for a trustworthy round

A round is operationally trustworthy when the operator can point to all of the following without interpretation work:

- a current round manifest
- a current coordination snapshot
- current heartbeat data for active chats
- current blocker records for open blockers
- current governed contracts for cross-package work
- current waiver records for every approved exception
- current merge-window record when integration is planned

## Short-form operator script

Use this exact mental script:

1. Is the round structure valid
2. Are the chats alive enough to trust
3. Are the blockers classified and owned
4. Are cross-package needs represented as contracts
5. Is the current snapshot fresh enough to decide
6. Is integration safe right now
7. If not safe, what single control action restores trust first

If the operator cannot answer any of those seven questions from artifacts, not conversation, the control plane still needs work.
