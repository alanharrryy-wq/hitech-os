# 17. Chat Coordination Model

## Purpose

This document defines the canonical coordination model for multi-chat execution inside the orchestrator factory. It extends the run and round model already present in the framework and gives the operator one deterministic way to route work, observe progress, and prevent ad-hoc chat behavior.

The model is anchored in these control-plane files:

- `configs/execution_framework/chat_topology.json`
- `configs/execution_framework/chat_capability_matrix.json`
- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/handoff_policy.json`
- `configs/execution_framework/escalation_matrix.json`
- `configs/execution_framework/blocker_taxonomy.json`
- `configs/execution_framework/sync_cadence.json`
- `configs/execution_framework/operator_dashboard_views.json`

The goal is simple: every coordinated action must have a known owner, a legal channel, a valid state, and evidence that can be inspected later.

## Control-plane shape

The framework already uses a package model driven by:

- `system_config.json` for active package identifiers and mission control identity
- `path_policies.json` for ownership boundaries
- `repo_target_layout.json` for required repository structure
- run and round manifests for execution intent

The coordination layer keeps that model intact. It does not replace package ownership. It adds a deterministic communication plane around it.

### Mission control

The mission-control chat is `governance-control`.

Mission control is the only actor that may:

- arbitrate cross-package work
- reroute ownership across package boundaries
- publish escalation events
- open and manage merge windows
- consolidate global coordination snapshots

Mission control is not a worker chat. It protects flow, deadlines, and safety.

### Package chats

Each package chat owns one package identifier and executes only work inside that ownership boundary.

The active package identifiers remain:

- `01-identity-access-and-trust`
- `02-domain-data-and-persistence`
- `03-service-contracts-and-orchestration`
- `04-experience-clients-and-interactions`
- `05-platform-infrastructure-and-delivery`
- `06-quality-release-and-operations`

A package chat may:

- execute package-local work
- emit heartbeats and checkpoints
- request dependencies through the governed channel
- report blockers with evidence
- accept or reject handoffs addressed to itself

A package chat may not:

- coordinate directly with another package chat outside the official channels
- reassign work across package boundaries
- close escalations
- declare merge windows

## Topology

The coordination graph is hub-and-spoke.

Mission control is the hub. Package chats are spokes. Cross-package coordination is never peer-to-peer. Instead, it flows through mission control using the official channels defined in `chat_topology.json`.

### Official channels

The coordination model uses these channels:

1. `channel.heartbeats`  
   Liveness, current status, and freshness signals.

2. `channel.sync_checkpoints`  
   Periodic state publication and round progress.

3. `channel.handoffs`  
   Explicit transfer, assist, review, and blocker-resolution contracts.

4. `channel.dependencies`  
   Requests and responses for required artifacts, contracts, or decisions.

5. `channel.blockers`  
   Standardized blocker reporting and triage intake.

6. `channel.escalations`  
   Traceable escalation records and decisions.

7. `channel.merge_windows`  
   Integration timing and collision prevention.

Each message type has exactly one required channel. This matters because the channel is part of protocol validity, not just presentation.

## Routing model

Routing is driven by three layers, always in this order.

### 1. Package ownership

If a task belongs to one package and does not cross into another package boundary, it routes to the package chat that owns that package identifier.

This preserves local execution and keeps source changes inside the right ownership boundary.

### 2. Cross-package arbitration

If a task depends on another package, references more than one package, or needs a decision that affects more than one package, it routes to mission control first.

Mission control can then decide whether the right next step is:

- a dependency request
- a handoff ticket
- a blocker report
- a merge-window reservation
- a re-scope decision

### 3. Control-plane exclusivity

Some work never belongs to a package worker. Cadence enforcement, escalation recording, and coordination snapshots always route to mission control.

## State model

The coordination state model is intentionally narrow:

- `planned`
- `in_progress`
- `blocked`
- `done`

This is not a generic status palette. It is a controlled lifecycle used across handoffs, dependency flows, blocker reports, and checkpoints.

### Why four states

A narrower state model creates fewer interpretation gaps.

- `planned` means the work item exists and ownership is known.
- `in_progress` means the owner accepted it and is actively working it.
- `blocked` means forward progress cannot continue without external action or a governance decision.
- `done` means the required outputs and evidence exist.

Every coordinated entity must be representable inside these states, which lets the operator compare unlike artifacts in one dashboard without translation.

## Message model

The coordination plane uses a structured message envelope defined by `schemas/execution_framework/chat_message.schema.json`.

The message envelope is used for channel publication, not for package execution payloads.

A valid message always identifies:

- what it is
- which run and round it belongs to
- which chat published it
- where it was published
- what its current status is
- what summary the operator should read first

The envelope can attach entity references, evidence references, or a dedicated payload reference, but it cannot hide the status summary.

## Handoff model

A handoff is the canonical way to move work or bounded responsibility across a chat boundary.

The handoff contract exists to prevent three classic failures:

1. ownership transfer without explicit acceptance
2. work requests without acceptance criteria
3. resolved tickets without evidence

A handoff always includes:

- sender and receiver
- package identifier
- task reference
- bounded requested outcome
- acceptance criteria
- severity
- due time
- ownership mode
- traceability fields and history

Mission control is the only actor that may reroute a handoff across package boundaries. Package chats do not open direct peer-to-peer handoffs.

## Dependency model

Dependencies are not informal questions. They are tracked requests with due times and downstream impact.

A dependency request exists when progress requires:

- an artifact
- a contract
- an approval
- a scope decision
- a bounded deliverable from another owner

The key rule is that a dependency request does not reassign ownership by itself. If ownership must move, mission control converts the situation into an explicit handoff.

## Blocker model

A blocker is a typed, triaged interruption to progress. The blocker taxonomy is limited to:

- `dependency`
- `scope`
- `infra`
- `quality`

This keeps triage legible. The operator should be able to answer two questions quickly:

- what first external condition stopped progress
- who owns the next action

Severity is defined independently from blocker type. A scope blocker can be `sev1` if it threatens the round, while a dependency blocker can be `sev4` if the effect is localized and time-tolerant.

## Cadence model

Cadence is part of flow control, not optional observability.

Heartbeats prove a chat is alive and has recent progress. Checkpoints prove that the official status and evidence trail are fresh.

Mission control uses a tighter cadence than package chats because it owns control-plane freshness.

Package chats publish on time and also on important events, especially when work becomes blocked or done.

Silent chats are not merely late. They create coordination risk because mission control loses certainty about ownership, progress, and readiness.

## Operator view of the system

The operator dashboard is the practical surface of the model. It should answer these questions in order:

1. Which chats are healthy and current
2. Which items are blocked or aging
3. Which handoffs are overdue or low quality
4. Which dependencies are threatening the round
5. Which packages are ready for merge windows
6. Which global decisions must mission control publish now

The dashboard view configuration in `operator_dashboard_views.json` formalizes these questions so the operator is not forced to improvise.

## Non-negotiable invariants

The coordination model relies on a few invariants.

1. Every coordinated item has exactly one active owner chat at any instant.
2. Cross-package routing flows through mission control.
3. Items in `blocked` state must name a blocker type and next action owner.
4. Items in `done` state must attach evidence.
5. Timestamp sequences for the same item must be monotonic.
6. Silence and cadence are enforceable protocol concerns, not optional etiquette.

If one of these invariants breaks, the operator should treat it as protocol drift and correct it before adding more work.

## What this model does not do

This model does not:

- change package ownership boundaries
- permit direct package-to-package chat improvisation
- bypass the existing run and round lifecycle
- replace bundle validation or integration readiness checks
- infer meaning from unstructured text alone

It only standardizes the coordination layer around the framework that already exists.

## Practical reading order

For someone operating or extending the multi-chat layer, use this reading order:

1. `17_chat_coordination_model.md`
2. `18_handoff_queue_protocol.md`
3. `19_blocker_escalation_playbook.md`
4. `20_operator_daily_control_loop.md`

Then use the configs and schemas as the executable contract.

## Outcome

When the model is followed, the operator gains:

- deterministic routing
- explicit ownership
- bounded handoffs
- stable blocker triage
- enforced cadence
- safer merge timing
- auditable global state

That is the point of the coordination plane. It removes ad-hoc behavior from the hardest part of multi-chat execution: deciding who owns what, who moves next, and how the operator knows it is safe.
