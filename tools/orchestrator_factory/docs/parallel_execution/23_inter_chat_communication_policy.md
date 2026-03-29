# 23. Inter-Chat Communication Policy

## Purpose

This policy hardens communication between mission control and package chats so that the coordination plane remains deterministic under pressure.

The rule is simple:

Cross-package coordination must be artifact-backed, channel-valid, and reconstructable without replaying the raw conversation.

## Governing references

This policy is derived from:

- `configs/execution_framework/chat_topology.json`
- `configs/execution_framework/chat_capability_matrix.json`
- `configs/execution_framework/coordination_protocol.json`
- `configs/execution_framework/handoff_policy.json`
- `configs/execution_framework/sync_cadence.json`
- `schemas/execution_framework/chat_message.schema.json`
- `schemas/execution_framework/handoff_ticket.schema.json`
- `schemas/execution_framework/dependency_request.schema.json`
- `schemas/execution_framework/dependency_response.schema.json`
- `schemas/execution_framework/blocker_report.schema.json`
- `schemas/execution_framework/escalation_event.schema.json`
- `schemas/execution_framework/sync_checkpoint.schema.json`
- `schemas/execution_framework/chat_heartbeat.schema.json`
- `schemas/execution_framework/coordination_snapshot.schema.json`
- `schemas/execution_framework/merge_window.schema.json`

## Core policy

### 1. Package chats do not coordinate directly with each other

Package chats may contribute artifacts that affect one another, but any cross-package ask or answer must flow through governance control using the correct governed contract.

Allowed forms of cross-package coordination:

- handoff ticket opened or routed by governance control
- dependency request published to the dependencies channel
- dependency response published by governance control or the delegated owner through the governed path
- blocker report that explicitly names the next action owner
- escalation event
- merge-window record

Forbidden forms:

- peer-to-peer hidden negotiation
- undocumented ownership transfer
- verbal-only approval for integration
- narrative exceptions that are not written as a waiver

### 2. Every message has one legal channel

The channel is part of protocol validity.

Use the following mapping:

- `chat_heartbeat` -> `channel.heartbeats`
- `sync_checkpoint` -> `channel.sync_checkpoints`
- `coordination_snapshot` -> `channel.sync_checkpoints`
- `handoff_ticket` -> `channel.handoffs`
- `dependency_request` -> `channel.dependencies`
- `dependency_response` -> `channel.dependencies`
- `blocker_report` -> `channel.blockers`
- `escalation_event` -> `channel.escalations`
- `merge_window` -> `channel.merge_windows`

A payload on the wrong channel is not merely messy. It is invalid.

### 3. Every coordination message must answer one operational question

A valid message should reduce ambiguity, not create it.

The operator should be able to answer the following from the message body alone:

- who published it
- which run and round it belongs to
- what state it represents
- which entity ids it affects
- which evidence refs support it
- what action follows next

If a message does not answer those questions, it should not be treated as authoritative.

### 4. State changes require publication

Any material state change must be published as a governed artifact.

Material state changes include:

- planned to in progress
- in progress to blocked
- blocked to in progress
- in progress to done
- ownership reassignment
- merge window opened, changed, or closed
- waiver approved, denied, revoked, or expired

### 5. Silence is itself a signal

A chat that misses heartbeat or checkpoint cadence is not neutral. It reduces trust in downstream decisions.

Silent-chat handling must follow `configs/execution_framework/sync_cadence.json` and the coordination snapshot should make the staleness state visible.

## Message quality rules

### Messages must be traceable

Every governed message must have:

- a stable id
- UTC publication time
- origin chat id
- explicit run and round ids
- evidence refs if the message claims completion, health, or exception
- history entries when the message type supports lifecycle progression

### Messages must be bounded

Avoid broad or vague asks.

Good bounded asks include:

- deliver a contract
- clarify a scope edge
- provide evidence
- confirm a merge order
- resolve a named blocker

Bad asks include:

- help with the package
- look at this later
- coordinate this somehow

### Messages must respect ownership

A package chat may only claim authority for its owned package id unless governance has explicitly transferred or delegated work through a governed contract.

## Escalation and exception path

When normal communication cannot safely preserve flow:

1. publish a blocker report
2. classify severity and blocker type
3. publish an escalation event if the matrix requires it
4. publish a waiver request if a policy deviation is being considered
5. refresh the coordination snapshot

The exception path is still governed communication. It is not a suspension of governance.

## Merge-window communication rules

A merge window is a control artifact, not a suggestion.

Before a merge window is treated as active:

- target packages must be named
- admission rules must be explicit
- evidence refs must exist
- integration order must be deterministic
- active waivers must be known
- open sev1 and sev2 blockers affecting the window must be visible

No chat may claim that a merge is safe based only on conversation tone or recent activity.

## Operator enforcement

The operator should intervene when any of the following appear:

- peer-to-peer package coordination
- conflicting owners for one active item
- status changes with no artifact publication
- blockers with no next action owner
- dependencies with no response path
- readiness claims with no evidence
- waivers discussed but not recorded

## Minimum acceptable communication posture

A round has an acceptable communication posture when:

- all active chats are publishing on cadence
- all cross-package needs are represented as contracts
- all material state changes are published
- all exceptions are written and bounded
- the latest coordination snapshot can explain the state of the round without reading the entire chat log

That is the bar for production communication in this orchestrator.
