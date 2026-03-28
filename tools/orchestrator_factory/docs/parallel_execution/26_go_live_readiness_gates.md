# 26. Go-Live Readiness Gates

## Purpose

This document defines the final readiness gates that must pass before the multi-chat orchestrator is treated as production-trustworthy for an active run.

A readiness gate is not a narrative statement. It is a binary control with required evidence.

This document is the framework-root companion to the readiness references already carried by run and round manifests. Where those manifests point to governance-controlled readiness documents outside the framework root, the semantics should remain aligned with this gate set.

## Gate design principles

Each gate must be:

- observable
- attributable
- repeatable
- binary at decision time
- linkable from the coordination snapshot or run evidence

## Gate 1: Static contract integrity

### Question

Are the install-layer contracts coherent enough to trust runtime output

### Required evidence

- configs parse as valid JSON
- schemas parse as valid JSON
- templates parse as valid JSON
- runtime tooling can load the referenced configs and schemas without missing-file errors

### Failure meaning

The control plane cannot be trusted because the rules themselves are malformed or inconsistent.

### Allowed next action

Fix the install layer before starting or continuing the run.

## Gate 2: Topology and routing coherence

### Question

Do chat ids, message types, channels, states, severities, and blocker types agree across the coordination configs and schemas

### Required evidence

- official channels map cleanly to allowed message types
- allowed chat ids are consistent across message-bearing schemas
- lifecycle states are consistent with `planned`, `in_progress`, `blocked`, and `done`
- severity values are consistent with `sev1` through `sev4`
- blocker types are consistent with the taxonomy and escalation matrix

### Failure meaning

The system could accept or emit artifacts that disagree on meaning. That is a hard stop.

## Gate 3: Bootstrap safety

### Question

Can a round coordination plane be created idempotently without mutating framework source files

### Required evidence

- bootstrap creates only additive runtime structure
- re-running bootstrap does not destroy or overwrite existing evidence
- missing run or round context fails loudly with actionable errors

### Failure meaning

Round initialization is unsafe and may corrupt evidence.

## Gate 4: Liveness proof

### Question

Can the control plane distinguish current chats from stale or silent chats according to `sync_cadence.json`

### Required evidence

- heartbeat emission produces valid artifacts
- staleness calculation yields `ok`, `warning`, `escalated`, or `missing`
- the coordination snapshot surfaces stale chats

### Failure meaning

Operators cannot safely trust the live picture of the round.

## Gate 5: Governing-contract proof

### Question

Can cross-package work be represented through governed contracts rather than ad-hoc conversation

### Required evidence

- handoff tickets validate
- dependency requests and responses validate
- blocker reports validate
- escalation events validate
- merge windows validate
- every cross-package need in the current round appears as one of those contract classes

### Failure meaning

The round depends on hidden conversation rather than auditable contracts.

## Gate 6: Blocker and escalation control

### Question

Can the system classify blockers consistently and recommend escalation deterministically

### Required evidence

- blocker types align with the taxonomy
- severities align with the escalation matrix
- high-severity blockers are visible in snapshots
- blocker records include next action owners and sufficient traceability

### Failure meaning

The operator cannot prioritize or explain why work is blocked.

## Gate 7: Snapshot integrity

### Question

Can the coordination snapshot reconstruct the global round state without replaying the chat transcript

### Required evidence

- snapshot aggregates heartbeats, blockers, handoffs, dependencies, and merge timing
- snapshot counts are internally coherent
- snapshot rows carry enough ids and refs for drill-down
- markdown summary and JSON snapshot agree on core health conclusions

### Failure meaning

The control plane is not legible enough for production operation.

## Gate 8: Waiver control

### Question

Can deviations from normal readiness or coordination rules be approved, monitored, expired, and audited deterministically

### Required evidence

- waiver requests validate
- active waivers appear in the latest coordination snapshot or linked evidence
- waivers have expiry or bounded scope
- waivers link to affected artifacts through refs
- revocation and denial remain explainable after the fact

### Failure meaning

The system can proceed on exceptions without preserving trust.

## Gate 9: Merge-window safety

### Question

Can integration timing be opened only when the target package set is actually safe enough to merge

### Required evidence

- merge window record exists
- admission rules are explicit
- target package ids are explicit
- integration order is deterministic
- no unaccounted sev1 or sev2 blocker threatens the target set
- active waivers affecting the target set are visible and unexpired

### Failure meaning

Integration decisions are optimistic instead of controlled.

## Gate 10: Operator handoff continuity

### Question

Can the next operator resume the round from artifacts alone

### Required evidence

- latest coordination snapshot exists
- latest blocker view is current
- overdue contracts are visible
- active waivers and expiries are visible
- next control action is explicit

### Failure meaning

The control plane depends on private memory, which is not acceptable for production use.

## Decision policy

### Ready

The system is ready when every gate above is green or when any non-green gate is covered by an explicit approved waiver that is itself valid, bounded, and visible.

### Not ready

The system is not ready when:

- any gate fails without a valid waiver
- a sev1 or sev2 issue undermines integration safety
- the latest snapshot is too stale to support a trustworthy decision
- the operator cannot identify the next action owner for current blockers

## Readiness review order

Run gates in this order:

1. static contract integrity
2. topology and routing coherence
3. bootstrap safety
4. liveness proof
5. governing-contract proof
6. blocker and escalation control
7. snapshot integrity
8. waiver control
9. merge-window safety
10. operator handoff continuity

The sequence matters because later gates depend on earlier ones being trustworthy.

## Minimum go-live evidence bundle

A serious go-live review should be able to point to:

- the relevant configs and schemas
- one valid round bootstrap artifact
- current heartbeat artifacts
- current blocker and escalation artifacts
- the latest coordination snapshot
- any active waiver requests
- the current merge-window record if integration is planned

That bundle is the minimum bar for saying the orchestrator is ready to carry production coordination.
