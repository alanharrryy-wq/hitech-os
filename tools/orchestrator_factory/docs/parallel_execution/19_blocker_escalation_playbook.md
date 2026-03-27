# 19. Blocker Escalation Playbook

## Purpose

This playbook describes how the operator and mission-control chat should handle blockers from first report to closure using:

- `configs/execution_framework/blocker_taxonomy.json`
- `configs/execution_framework/escalation_matrix.json`
- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/sync_cadence.json`

The playbook is intentionally procedural. When a blocker lands, the operator should not invent a bespoke process. The operator should classify it, assign severity, identify the next action owner, and decide whether escalation is required.

## The first question

When a new blocker is reported, ask this first:

**What first external condition prevents forward progress right now?**

That question drives blocker type.

## Canonical blocker types

The blocker taxonomy is intentionally small.

### Dependency

Use `dependency` when progress waits on another owner to deliver an artifact, contract, approval, or bounded output.

Signals include:

- overdue dependency response
- open handoff waiting on another owner
- checkpoint explicitly waiting on external input

### Scope

Use `scope` when progress stops because the requested outcome, acceptance criteria, or ownership boundary is unclear or contradictory.

Signals include:

- contradictory instructions
- unclear package boundary
- handoff rejected for missing scope
- checkpoint reporting conflicting outcomes

### Infra

Use `infra` when the environment, filesystem, runtime, or framework path prevents progress.

Signals include:

- missing required directories
- config load failure
- unavailable tool path
- broken initialization path

### Quality

Use `quality` when output exists but cannot advance because a validation, evidence, or readiness gate failed.

Signals include:

- schema validation failure
- required evidence missing
- readiness gate failure
- integration safety rejection

## Severity assignment

Severity answers a different question:

**How badly does this blocker threaten the current round or integration safety?**

The matrix uses four levels:

- `sev1` critical
- `sev2` high
- `sev3` medium
- `sev4` low

A blocker type never determines severity by itself. The operator should consider impact window, scope of damage, and time sensitivity.

### Practical severity cues

Use `sev1` when:

- the current round cannot complete without action in roughly the next hour
- integration safety is at immediate risk
- mission control must intervene now

Use `sev2` when:

- the package objective is threatened in the current work cycle
- a dependency or quality issue is likely to miss a same-cycle deadline

Use `sev3` when:

- the issue slows one stream but the round can continue elsewhere

Use `sev4` when:

- the issue is localized and does not threaten today's flow

## Initial triage procedure

When a blocker report arrives, execute this sequence.

1. Validate the report fields and evidence.
2. Confirm the active owner chat.
3. Classify the blocker type using the primary-cause rule.
4. Assign severity using impact, time window, and scope.
5. Name the next action owner.
6. Decide whether escalation is required now.
7. Ensure the blocker appears in the next coordination snapshot if severity requires it.
8. Link any related dependency request or handoff ticket.

The point of the first triage pass is not to solve everything. The point is to remove ambiguity fast enough that the next action is obvious.

## Escalation rules

Escalation policy is deterministic.

### Severity-driven obligations

- All `sev1` blockers escalate immediately.
- All `sev2` blockers escalate on the operator timeline defined by the matrix.
- `sev3` and `sev4` blockers may remain visible in snapshots without an immediate escalation event unless their context worsens.

### Type-driven obligations

Some blocker types demand stronger control even at the same severity.

- A `quality` blocker near a merge window deserves tighter control than a low-risk dependency.
- An `infra` blocker affecting mission control deserves faster action than a localized package issue.
- A `scope` blocker with contradictory ownership should not linger, because it creates unsafe decisions downstream.

## Response playbook by blocker type

### Dependency blocker response

1. Confirm which external owner or chat owes the next deliverable.
2. Check the due time on the dependency request or linked handoff.
3. If no proper request exists, create the governed request path immediately.
4. Decide whether to reprioritize the dependency queue or reroute through a new handoff.
5. Publish the revised due time and next action owner.

Escalate to `sev1` when the round cannot progress without the dependency in the immediate control window.

### Scope blocker response

1. Identify the conflicting or missing instruction.
2. Freeze the affected downstream item.
3. Ask mission control to issue the clarified requested outcome.
4. Update acceptance criteria and scope refs before resuming work.
5. Reissue the affected handoff or checkpoint if ownership or boundary changed.

Do not allow package chats to solve cross-package scope contradictions informally.

### Infra blocker response

1. Preserve evidence of the failure mode.
2. Identify whether the issue is local to one chat or affects the control plane.
3. Publish a workaround if one exists.
4. Reroute unaffected work to keep the round moving.
5. Keep mission control aware of any risk to cadence, state freshness, or merge timing.

Infra blockers are dangerous because they can make the operator blind if heartbeat and checkpoint paths degrade.

### Quality blocker response

1. Identify the failed validation or missing evidence.
2. Block any unsafe integration path immediately.
3. Require corrective action with fresh evidence.
4. Keep the item in blocked state until readiness is actually restored.
5. Reflect the quality risk in the merge-window readiness view.

A quality blocker should never be softened into a documentation issue when it is actively preventing safe acceptance.

## Escalation event contents

An escalation event should make the operator's judgment legible. It should record:

- blocker identifier
- blocker type
- severity
- owning chat
- impacted package identifiers
- required action
- resolution owner
- checkpoint frequency
- publication time
- history updates

Escalation events should be append-only apart from added history entries.

## Checkpoint discipline during blockage

A blocker is not static. Once an item is blocked, the operator still needs cadence.

Checkpoint frequency is severity-sensitive:

- `sev1` generally updates every 15 minutes
- `sev2` generally updates every 30 minutes
- `sev3` generally updates every 2 to 4 hours depending on type
- `sev4` generally updates at least daily or at the next operator cycle

Missed blocker checkpoints should themselves be treated as control-plane risk, because the operator loses certainty about whether the blocker is stable, worsening, or silently resolved.

## Interaction with merge windows

Before a merge window opens, the operator should review blockers through an integration lens.

The following should normally prevent readiness:

- any active `sev1` blocker
- any active `quality` blocker affecting the package
- unresolved cross-package dependency blockers tied to the same integration set
- unresolved scope blockers that affect acceptance criteria or path ownership

If a merge window stays open while these remain unresolved, the operator is accepting collision or safety risk without a legible decision trail.

## Closure criteria

A blocker is closed only when the first external condition that stopped progress no longer exists.

Closure requires:

- resolution summary
- evidence refs
- updated downstream state
- snapshot visibility if the blocker was `sev1` or `sev2`

If the blocker only changed shape, it should not be closed. It should be reclassified or linked to the next valid blocker record.

## Failure patterns to avoid

The operator should actively avoid these failure patterns:

- using one blocker record to represent multiple root causes
- misclassifying scope ambiguity as quality noise
- closing blockers because conversation feels calmer without evidence
- letting blockers remain active without a named next action owner
- allowing overdue severe blockers to disappear from the coordination snapshot

## Outcome

A good blocker playbook creates two kinds of stability:

- execution stability for the workers
- decision stability for mission control

The operator should be able to look at any blocker and immediately know what it is, how bad it is, who moves next, and what evidence will close it.
