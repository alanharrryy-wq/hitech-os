# 24. Exception and Waiver Policy

## Purpose

This document defines the only acceptable path for deviating from normal coordination, readiness, or integration rules during an active run or round.

The point of a waiver is not convenience. The point is to make a bounded, auditable decision when strict compliance would create a worse operational outcome than a temporary, controlled deviation.

## Governing references

This policy is grounded in:

- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/escalation_matrix.json`
- `configs/execution_framework/sync_cadence.json`
- `schemas/execution_framework/bundle_manifest.schema.json`
- `schemas/execution_framework/coordination_snapshot.schema.json`
- `schemas/execution_framework/merge_window.schema.json`
- `schemas/execution_framework/waiver_request.schema.json`
- `templates/execution_framework/run/waiver_request.template.json`

## Core rule

No exception is valid unless it is recorded as a waiver request with:

- a named requester
- a named decision owner
- a bounded target
- a stated deviation
- a business impact statement
- a risk statement
- compensating controls
- a rollback plan
- an expiry or explicit persistence scope
- evidence refs
- a history trail

If any of those are missing, the operator should treat the exception as denied until the artifact is corrected.

## What may be waived

A waiver may be considered for:

- temporary evidence freshness gaps
- timing collisions when the underlying work is otherwise sound
- bounded workflow ordering changes that do not violate ownership or safety
- isolated non-critical readiness findings that can be compensated during the same round

## What may not be waived

A waiver must not approve:

- path ownership violations
- destructive operations forbidden by system policy
- direct peer-to-peer cross-package coordination outside governed channels
- missing run or round identity
- missing owner identity
- absent rollback plan
- unsafe merge admission when a sev1 or sev2 blocker remains unresolved
- fabricated evidence or retrospective status rewriting

If the only path forward requires one of those forbidden conditions, the correct answer is escalation or re-scope, not a waiver.

## Decision ownership

The decision owner for waivers is governance control unless a stricter governance structure is introduced later.

Package chats may request waivers. They may not approve their own waiver requests.

## Waiver lifecycle

### 1. Requested

The requester publishes the deviation, target refs, impact, risk, and mitigation.

The waiver is not active yet.

### 2. Reviewed

Governance evaluates whether the deviation is bounded, observable, reversible, and less risky than blocking the round.

### 3. Approved or denied

An approved waiver must include:

- approval summary
- expiry or scope limit
- compensating controls
- acknowledgement by the affected owner when applicable

A denied waiver must include a denial reason that is specific enough to guide the next action.

### 4. Monitored

Active waivers must remain visible in coordination snapshots, merge-window reviews, and affected bundle manifests through `waiver_refs`.

### 5. Closed

A waiver closes when it is:

- fulfilled and no longer needed
- expired
- revoked
- superseded by a new governed decision

Closure must also be recorded.

## Approval criteria

Governance should only approve a waiver when all of the following are true:

1. the target is explicit
2. the blast radius is bounded
3. the deviation does not violate ownership or destructive-operation policy
4. the issue is observable through existing artifacts
5. compensating controls are concrete
6. rollback is possible within the active control window
7. the waiver materially improves flow compared with strict denial

## Required links

Every active waiver should be linked from every artifact it materially affects.

At minimum, that may include:

- `bundle_manifest.json` through `waiver_refs`
- a coordination snapshot
- a blocker report if the waiver is tied to a blocker
- a merge-window record if integration timing depends on the waiver

## Expiry rules

A waiver without an expiry or scope limit is not production-safe.

Preferred scope order:

1. single item
2. single round
3. single run

Longer scope requires stronger justification and stronger compensating controls.

## Revocation rules

Governance should revoke an active waiver immediately when:

- the compensating controls fail
- the blast radius expands beyond the approved scope
- a new sev1 or sev2 blocker invalidates the original risk calculation
- the owner fails to acknowledge or fulfill the required corrective action
- the evidence base used for approval is found to be stale or wrong

Revocation is a control action, not a punishment. The point is to restore trust in the coordination plane.

## Operator handling

The operator must surface active waivers in every high-signal review.

At minimum:

- opening cycle
- blocker triage
- merge-window review
- closing cycle
- operator handoff to the next shift or next round

## Relationship to readiness gates

A waiver does not erase a failed readiness gate.

A waiver records a temporary decision to proceed despite a known failure under explicit conditions. The failed gate remains visible until the corrective evidence lands or the waiver expires.

That distinction matters in postmortems.

## Relationship to contract versioning

A waiver may allow a bounded operational deviation. It does not silently rewrite contract semantics. If the team decides the deviation should become normal behavior, that is a contract change and must follow the contract versioning policy.

## Non-negotiable audit line

The system must be able to answer these questions after the fact without guessing:

- what rule was deviated from
- who requested it
- who approved it
- why it was accepted
- what evidence supported it
- what controls limited the risk
- when it expired
- whether it was fulfilled, revoked, or denied

If the artifacts cannot answer those questions, the waiver process has failed.
