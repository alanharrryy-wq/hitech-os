# 18. Handoff Queue Protocol

## Purpose

This document defines the operational protocol for the handoff queue that sits on top of the canonical handoff contract in:

- `configs/execution_framework/handoff_policy.json`
- `schemas/execution_framework/handoff_ticket.schema.json`
- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/chat_topology.json`

The queue exists to guarantee that cross-chat work does not disappear into conversational fog. A handoff is not complete because someone mentioned it. A handoff is complete when its state, scope, acceptance criteria, due time, and evidence are present in a valid ticket.

## Queue objectives

The handoff queue serves five objectives:

1. preserve ownership clarity
2. bound the requested outcome
3. make acceptance explicit
4. expose overdue or weak tickets
5. preserve closure evidence

## What counts as a handoff

A handoff exists when one chat needs another chat to do one of these things:

- deliver a dependency artifact
- clarify scope so work can resume
- prepare integration evidence before a merge window
- resolve a blocker through a bounded action
- review a bounded output when review itself is the requested outcome

The queue is not used for casual status narration. It is used when one owner expects a bounded output from another owner.

## Queue structure

Each queue item is a `handoff_ticket`.

A ticket is valid only when it includes all required identity, scope, control, and traceability fields. Those fields exist to make the queue auditable, not ornamental.

### Identity block

The identity block answers:

- which run and round this belongs to
- which chat opened the ticket
- which chat is expected to respond
- what kind of handoff it is

### Scope block

The scope block answers:

- which package the work belongs to
- which task or packet triggered the handoff
- what outcome is requested
- which files, packets, or decisions define the boundary
- how the receiver knows the work is complete

### Control block

The control block answers:

- current state
- severity
- due time
- ownership mode

### Traceability block

The traceability block answers:

- which evidence already exists
- which dependencies this handoff touches
- which blockers are linked
- what history entries explain the ticket path

## Ownership modes

The queue supports three ownership modes.

### Transfer

Use `transfer` when execution ownership moves to the receiver after acceptance.

This is the heaviest mode. It should be used only when responsibility genuinely shifts.

### Assist

Use `assist` when the receiver must produce a bounded output, but the origin chat keeps primary ownership.

This is the default mode for dependency-style support work.

### Review

Use `review` when the receiver validates or approves a bounded output without taking execution ownership.

This mode should not be abused as a proxy for general coordination.

## Queue lifecycle

The queue lifecycle mirrors the protocol states.

### Planned

The ticket exists, is addressed to one receiver, and has enough scope to evaluate.

A planned ticket is not yet accepted.

### In progress

The receiver accepted the ticket and became responsible according to the ownership mode.

The first checkpoint after acceptance should satisfy the SLA in `handoff_policy.json`.

### Blocked

The receiver cannot continue without external action. A blocked handoff must link the blocker that caused the stop.

### Done

The requested outcome exists, evidence refs are attached, and the completion summary explains what the receiver delivered.

A done ticket without evidence is invalid.

## Queue intake rules

The operator or mission-control chat should reject queue intake when any of these are true:

- the ticket has more than one intended receiver
- the requested outcome is vague
- acceptance criteria are missing
- the due time is missing
- ownership mode is absent
- scope refs are empty for nontrivial work
- severity is missing
- the ticket tries to create direct package-to-package routing outside mission control

Intake discipline matters because the queue becomes unreadable if malformed tickets are allowed in.

## Queue routing rules

Cross-package handoffs do not route directly between package chats.

The legal path is:

1. origin chat frames the need
2. mission control opens or validates the ticket
3. mission control routes it to the single receiving chat
4. receiver accepts, rejects, or requests revision
5. receiver publishes checkpoints until closure

This extra step is deliberate. It keeps ownership, policy, and escalation visibility in one place.

## Acceptance rules

A receiver may answer a new ticket in only three ways:

- `accept`
- `reject`
- `request_revision`

### Accept

Use `accept` only when:

- scope is bounded
- acceptance criteria are testable
- the requested outcome belongs inside the receiver's role
- the due time is realistic

Acceptance starts the SLA clock for the first checkpoint after acceptance.

### Reject

Use `reject` when:

- the ticket is outside role or package boundary
- scope cannot be bounded
- the requested outcome contradicts current policy
- the dependency must be re-scoped or rerouted

A rejection must include a reason.

### Request revision

Use `request_revision` when the ticket might be correct, but required fields or evidence are missing.

A revision request must identify the missing fields instead of replying with generic uncertainty.

## Queue service levels

The queue uses severity-based service levels already defined in `handoff_policy.json`.

### Acknowledgement targets

- `sev1`: 15 minutes
- `sev2`: 30 minutes
- `sev3`: 2 hours
- `sev4`: 8 hours

### Resolution targets

- `sev1`: 1 hour
- `sev2`: 4 hours
- `sev3`: 1 day
- `sev4`: 3 days

The queue is not successful because tickets exist. It is successful because tickets move predictably against those clocks.

## History discipline

Every material state change should append a history entry. The queue is a record of operational decisions, not only a list of current items.

A strong history entry should state:

- who made the change
- when the change happened
- what changed
- why the change happened

History is especially important for:

- reassignment by mission control
- transition to blocked
- acceptance of revised scope
- completion with evidence

## Overdue handling

The operator should treat overdue tickets in three buckets.

### Overdue acknowledgement

The receiver has not answered before the acknowledgement target. This is a queue intake failure or silence risk.

### Overdue progress

The receiver accepted the ticket but failed to publish the first checkpoint or next expected checkpoint.

### Overdue resolution

The requested outcome is still not delivered by the target time.

Each bucket should drive a different action. Do not collapse them into one generic "late" label.

## Queue quality checks

Mission control should inspect queue quality continuously.

A handoff queue is healthy when:

- each ticket has one clear receiver
- each ticket has a bounded requested outcome
- acceptance criteria are concrete
- due times exist and make sense
- state transitions are legal
- evidence is attached on closure
- blocked tickets link a blocker record
- no ticket remains in planned state without a response beyond its acknowledgement target

## Relationship to blockers and dependencies

A handoff ticket is not the same thing as a blocker, and it is not the same thing as a dependency request.

- A handoff is a bounded unit of requested work across a chat boundary.
- A dependency request records the need for an external deliverable or decision.
- A blocker explains why progress cannot continue.

One situation may include all three, but they should stay separate so the operator can reason about the system:

- the dependency identifies the need
- the handoff routes the bounded action
- the blocker captures the stopped progress

## Closure protocol

A ticket is only closed when:

- status is `done`
- completion summary exists
- evidence refs exist
- resolution can be tied back to the requested outcome and acceptance criteria

When closure evidence is weak, the ticket should remain open or move to revision, not be waved through.

## Queue outcome

A disciplined handoff queue prevents work from vanishing between chats. It converts coordination into an explicit, measurable stream of bounded commitments.

That is why the queue protocol exists. It protects the operator from ambiguity and protects package chats from invisible obligations.
