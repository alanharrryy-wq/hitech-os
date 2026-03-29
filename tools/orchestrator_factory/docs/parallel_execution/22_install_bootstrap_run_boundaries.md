# 22. Install, Bootstrap, and Run Boundaries

## Purpose

This document prevents boundary collapse between framework setup, round initialization, and active execution. In practice, most orchestration failures start when those phases blur together and operators no longer know which changes are safe.

This policy defines four boundaries:

1. install
2. bootstrap
3. run
4. round

The boundaries are strict because they protect determinism, idempotence, and auditability.

## Boundary 1: Install

Install is the static framework layer. It is the repository material that defines how the orchestrator behaves before any particular run begins.

Install includes:

- `configs/execution_framework/**`
- `schemas/execution_framework/**`
- `templates/execution_framework/**`
- `tools/execution_framework/**`
- `docs/parallel_execution/**`

Install changes are framework changes, not run activity.

### Install rules

- install artifacts are edited intentionally, not implicitly
- install artifacts are not rewritten by runtime commands
- install artifacts are reviewed as code or contract changes
- install artifacts must stay deterministic and serializable
- install changes should not be mixed with round state publication in the same action

### Install anti-patterns

Do not:

- create runtime evidence under the install tree
- write operational state back into configs or schemas
- patch framework rules during an active round to rescue bad execution
- bypass change review by hiding policy updates in operator notes

## Boundary 2: Bootstrap

Bootstrap creates additive runtime structure for a specific run and round. It does not redefine framework behavior.

Bootstrap includes:

- creating `ops/runs/<run_id>/rounds/<round_id>/coordination/`
- creating channel directories
- creating snapshot and view directories
- writing the coordination-plane manifest
- seeding only missing runtime files that are explicitly additive

Bootstrap must be idempotent.

### Bootstrap rules

- bootstrap may create missing directories
- bootstrap may create missing additive files
- bootstrap must not overwrite existing runtime evidence
- bootstrap must fail loudly if the run root or round manifest are missing
- bootstrap must not modify any file under `configs/`, `schemas/`, `templates/`, `docs/`, or `tools/` inside the framework root

### Bootstrap anti-patterns

Do not:

- bootstrap by copying the framework tree into the run
- bootstrap by regenerating manifests that already exist
- use bootstrap to sneak in policy changes
- make bootstrap depend on private operator memory

## Boundary 3: Run

Run is the lifecycle container for one execution objective. It contains decisions, rounds, and cross-round continuity.

Run state includes:

- `run_manifest.json`
- decisions
- round directories
- accumulated evidence and reports

A run may span multiple rounds. That is precisely why run-level control material must remain stable enough to compare one round to the next.

### Run rules

- run-level identifiers remain stable across rounds
- run-level policies are inherited from install artifacts and explicit run references
- run-level changes should be rare and deliberate
- emergency decisions belong in decision records or governed waivers, not in ad-hoc edits to the run manifest

### Run anti-patterns

Do not:

- treat each round as a separate run when the objective is continuous
- mutate run intent every time a package gets blocked
- hide governance choices in free-form notes

## Boundary 4: Round

Round is the active work cycle. It is where coordination messages, blockers, handoffs, dependencies, heartbeats, checkpoints, waivers, and merge windows live.

Round activity includes:

- heartbeats
- sync checkpoints
- handoffs
- dependency flow
- blocker reporting
- escalation events
- coordination snapshots
- merge windows
- approved waivers linked to the current round

The round is the highest-change surface in the system.

### Round rules

- round state must be published as governed artifacts
- round state must never require private interpretation to understand
- round state must be refreshable without touching install artifacts
- every round decision that weakens a normal rule must be represented by an explicit waiver request
- every round artifact must be attributable to one chat or governance action

## Cross-boundary rules

### Install must never impersonate runtime

A policy document may define behavior, but it must never claim that a specific round is healthy. Health belongs to runtime evidence.

### Runtime must never rewrite install

A blocker, emergency, or merge deadline is not justification for changing schemas or configs mid-flight unless the team intentionally performs a framework change as its own governed action.

### Bootstrap must never become repair-by-overwrite

If runtime files exist and are malformed, the answer is diagnosis and repair, not silent replacement.

### Rounds may reference install artifacts, not mutate them

The normal pattern is:

- run manifest references control documents
- round manifest inherits those references
- round artifacts point back to the install-layer contracts they were judged against

## Operator decision table

Use this table whenever there is confusion.

### If the action changes a framework rule

It is install.

### If the action creates only missing run or round structure

It is bootstrap.

### If the action changes the lifecycle or intent of a multi-round effort

It is run.

### If the action publishes status, ownership, blocker, or integration data for active execution

It is round.

## Why this matters

Without these boundaries, three bad things happen fast:

1. no one can tell whether a file is policy or evidence
2. idempotent setup becomes destructive repair
3. operators cannot explain which changes affected a failure

A production orchestrator survives by keeping those classes separate.
