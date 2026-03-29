# 25. Contract Versioning Policy

## Purpose

This document defines how orchestration contracts evolve without corrupting active runs or making historical artifacts unreadable.

Contracts in this framework include:

- configs
- schemas
- templates
- runtime message shapes that depend on those schemas
- policy references embedded in run and round manifests

The goal is controlled evolution, not novelty.

## Versioning principle

Version contracts in a way that preserves three things:

1. active-round stability
2. historical replayability
3. deterministic upgrade decisions

If a change improves clarity but breaks active consumers, it is not ready.

## Contract classes

### Static control contracts

These are install-layer contracts:

- `configs/execution_framework/**`
- `schemas/execution_framework/**`
- `templates/execution_framework/**`
- policy documents referenced by run and round manifests

### Runtime contracts

These are the produced artifacts that depend on static contracts:

- heartbeats
- checkpoints
- handoffs
- dependency records
- blocker reports
- escalation events
- snapshots
- merge windows
- waivers

Runtime contracts must always name the schema version they were produced against.

## Allowed change types

### Additive change

An additive change introduces new optional meaning without invalidating old valid payloads.

Typical additive changes:

- new optional field
- tighter documentation that does not change interpretation
- a new template sample that is compatible with the current schema

Additive changes may be introduced between rounds when they do not break current tooling.

### Behavioral change

A behavioral change alters how an existing field is interpreted or how a policy is enforced.

Behavioral changes require explicit review because they can create hidden drift even if JSON parsing still succeeds.

### Breaking change

A breaking change makes a previously valid payload invalid or changes the required meaning of an existing field.

Typical breaking changes:

- required field added
- allowed value removed
- identifier semantics changed
- channel mapping changed
- ownership rule changed
- readiness gate changed in a way that invalidates current run assumptions

Breaking changes should not land in the middle of an active high-risk run unless the alternative is operationally worse and governance records the decision.

## Versioning rules

### Rule 1: schema_version must stay honest

If the meaning of the contract changed materially, the declared version must reflect that.

### Rule 2: templates move with schemas

A template that no longer matches the schema is a broken contract, even if the schema itself is valid.

### Rule 3: policy refs are part of the contract surface

A run manifest that points to a communication or readiness document is effectively pinning a contract. Replacing the target document with incompatible semantics is a contract change even if the path string stays the same.

### Rule 4: active runs should prefer stability over elegance

If a cleaner contract would destabilize active rounds, schedule it for the next clean upgrade window rather than sneaking it into current operations.

## Upgrade discipline

Use the following discipline when changing coordination contracts.

### Before the change

- identify which runtime artifacts depend on the contract
- identify which templates must change with it
- identify whether any active run or round references the affected contract
- identify whether historical replay needs to preserve the prior meaning

### During the change

- keep old and new meanings distinguishable
- avoid partial updates where schema, template, and policy diverge
- update documentation that operators use for decisions, not only the machine-readable pieces

### After the change

- refresh readiness checks if they depend on the changed contract
- refresh templates and operator docs together
- verify that current snapshots and message validators still interpret the contract deterministically

## Compatibility posture

The default compatibility posture is conservative.

Preferred order:

1. additive first
2. behavioral only with explicit review
3. breaking only at a controlled boundary

Controlled boundaries include:

- before a new run starts
- between rounds when no active artifacts still rely on the old meaning
- after governance explicitly declares the upgrade window

## Historical artifacts

Never make old artifacts meaningless.

If a postmortem or replay tool cannot interpret a past waiver, blocker, or snapshot because contract semantics moved under it, the versioning policy failed.

## Operator responsibilities

The operator should ask three questions before accepting a contract change into live coordination:

1. Can active rounds continue without reinterpretation work
2. Can old artifacts still be explained correctly
3. Did schema, template, and policy move together

If any answer is no, the change is not ready for production coordination.

## Interaction with waivers

A waiver may temporarily allow an operational deviation. It does not automatically create a new contract norm.

If teams find themselves repeatedly waiving the same rule, that is evidence that the contract may need to evolve. The correct response is a versioned contract change, not permanent dependence on waivers.

## Release freeze rule

During a merge-critical or sev1 operating window, contract changes should be frozen unless governance explicitly records that the contract defect is itself the highest operational risk.

That freeze protects the meaning of the control plane when the team is already under pressure.

## Minimum versioning record

For any meaningful contract update, the review trail should record:

- changed contract paths
- change class: additive, behavioral, or breaking
- affected runtime artifact classes
- required companion updates
- activation boundary
- rollback posture

Without that record, the upgrade is guesswork.
