# Promotion Rules

This document defines the initial promotion and acceptance gates for the `control_tower` phase.

## Gate philosophy

Promotion is not a mood.
Promotion is a decision backed by explicit checks.

The default states of a candidate bundle are:
- `pass`
- `fail`
- `blocked`
- `not_applicable`

## Candidate types

These rules apply to:
- documentary bundles
- governance code bundles
- read-side snapshot/audit bundles
- combined future `control_tower` promotions

## Gate family A: documentary integrity

### A1. Canonical path gate
The bundle must place orchestration docs into the canonical documentary location.

Pass when:
- docs target `F:\repos\hitech-os\docs\orchestration`

Fail when:
- docs are scattered into ad hoc directories
- duplicate shadow docs are introduced

### A2. Shared dictionary gate
The bundle must preserve the canonical dictionary terms unchanged.

Fail when:
- `repo_analizer` is silently renamed
- lifecycle terms are altered
- access modes are widened or renamed without revision

### A3. Boundary fidelity gate
The bundle must preserve the boundary doctrine and not widen operational authority.

### A4. Chat split fidelity gate
If the work is parallelized, file ownership must remain non-overlapping.

## Gate family B: governance core integrity

Applies mainly to Chat A outputs.

### B1. Ownership clarity gate
Owned vs read-only vs forbidden must be explicit for protected domains.

### B2. Non-invasive governance gate
The governance core must not introduce runtime mutation or scheduler ownership.

### B3. Dependency clarity gate
Relationships among domains must be explicit and not imply absorption.

### B4. Work-order discipline gate
Any work-order model must not bypass documentary boundaries.

## Gate family C: state and assurance integrity

Applies mainly to Chat B outputs.

### C1. Read-only reader gate
Reader code and models must remain read-only.

### C2. Artifact contract gate
Artifacts must be typed using the canonical artifact kinds or an additive extension that does not redefine them.

### C3. Snapshot coherence gate
The snapshot model must represent state coherently across:
- `git_sentinel_modular`
- `engine_guardian`
- `control_tower`

### C4. No-remediation gate
Assurance/reporting must not mutate runtime state.

## Gate family D: package usability

### D1. Full-file delivery gate
The bundle must contain complete files, not patches.

### D2. Zip integrity gate
The bundle must be deliverable as a coherent zip.

### D3. Local execution workflow gate
If scripts exist, they must follow the user’s script rules.

### D4. Codex placement clarity gate
The bundle must be easy for Codex to place without guessing.

## Gate family E: protected system preservation

### E1. Closed front preservation gate
No bundle may reopen closed operational work implicitly.

### E2. Legacy intact gate
`HITECH-OS-GitSentinel-Guardian` must not be touched by implication.

### E3. Guardian scheduler preservation gate
The existing guardian scheduler contract must not be reassigned.

## Promotion outcomes

### Promote
Use only when all required gates pass.

### Block
Use when:
- evidence is incomplete
- boundaries are ambiguous
- parallel ownership conflicts exist

### Reject
Use when:
- operational authority is widened improperly
- protected systems are touched
- read-only restrictions are violated
- documentary authority is undermined

## Minimum documentary promotion checklist

A documentary bundle should not be promoted unless it includes:
- authority policy
- scope
- shared dictionary
- placement structure
- boundaries
- ownership
- rules and restrictions
- promotion rules
- artifact registry contract
- status snapshot contract
- assurance model
- chat split rules
- path authority matrix
- change control policy
