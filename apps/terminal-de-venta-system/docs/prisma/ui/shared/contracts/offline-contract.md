# Offline Contract

## Purpose

This contract defines how PRISMA behaves when connectivity is unavailable, degraded, delayed, or risky.

Offline support must be intentional. It is not a magic trick. It is a controlled operating mode with clear limits, sync rules, audit events, and recovery behavior.

## Core rule

Offline mode may allow operation, but it must never hide uncertainty.

Every offline action must clearly declare:

1. What can be done.
2. What cannot be done.
3. What remains pending.
4. What can conflict later.
5. What requires online confirmation.

## Offline states

| State | Meaning | UI behavior |
|---|---|---|
| online | Normal operation | No special warning |
| online_degraded | Connected with latency or queue | Show sync warning |
| offline_operational | Local operation allowed | Persistent offline banner |
| offline_restricted | Only safe flows allowed | Strong warning and blocked risky actions |
| recovery_syncing | Connection returned and events are syncing | Show progress and pending events |
| conflict_required | Sync found conflicts | Block affected entities until resolution |

## Flow policy

| Flow | Offline allowed | Notes |
|---|---:|---|
| simple sale | Yes | Requires cached catalog and price list |
| cash payment | Yes | Generates pending receipt event |
| card payment | Limited | Depends on payment terminal capability |
| customer lookup | Yes | Cached data only |
| customer create | Yes | Pending validation |
| customer credit approval | No | Requires online policy unless explicitly cached |
| inventory count | Yes | Sync later |
| inventory adjustment | Limited | Requires permission and risk flag |
| purchase reception | Limited | Capturable offline, confirmation may wait |
| order capture | Yes | Local folio required |
| production stage update | Yes | Requires cached order and stages |
| membership check-in | Yes | Requires recent cached membership state |
| membership renewal | Limited | Depends on payment and policy |
| fiscal stamping | No | Queue for later |
| plugin configuration | No | PC online only |
| permission changes | No | PC online only |
| sync conflict resolution | No | PC online only |

## Local event requirements

Every offline action must generate a local event with:

| Field | Required | Description |
|---|---:|---|
| event_id | Yes | Stable unique event ID |
| local_sequence | Yes | Device sequence number |
| device_id | Yes | Device that created the event |
| terminal_id | Yes | Terminal identity |
| actor_id | Yes | User responsible |
| module_id | Yes | Module owner |
| plugin_id | If applicable | Plugin source |
| entity_type | Yes | Entity family |
| entity_id | Yes | Entity identifier |
| action | Yes | Business action |
| created_at_local | Yes | Local timestamp |
| sync_status | Yes | pending, sent, confirmed, conflict |
| risk_level | Yes | low, medium, high, critical |
| conflict_strategy | Yes | Resolution strategy |

## Conflict strategies

| Strategy | Use case |
|---|---|
| append_only | Ledgers, audit, immutable events |
| last_writer_blocked | Dangerous mutable entities |
| server_authoritative | Central policy, permissions, fiscal |
| manual_resolution | Inventory conflicts, customer debt, duplicate folios |
| local_pending_review | Offline customer creation, field orders |

## Tablet behavior

Tablet must be able to operate in offline mode, but it must stay honest.

It should show:

- offline banner
- pending event count
- disabled risky actions
- cached data age
- local folio indicators
- sync recovery progress
- plugin degraded states

## PC behavior

PC owns recovery and governance.

It should support:

- reviewing offline queues
- resolving conflicts
- inspecting device event history
- replaying failed events when safe
- marking events as rejected, merged, or accepted
- auditing who resolved what
- configuring offline limits per module and plugin

## Plugin offline rule

A plugin must explicitly declare its offline behavior.

A plugin cannot inherit offline support from a screen unless it declares:

- cached entities required
- local events produced
- sync strategy
- conflict strategy
- degraded mode
- blocked actions
- PC recovery workflow

## Degraded mode rule

When offline or degraded, PRISMA must prefer partial safe operation over total collapse.

Allowed degraded examples:

- capture sale locally
- capture order draft
- perform inventory count
- validate membership from cache
- issue local receipt pending sync
- queue fiscal work for later

Blocked degraded examples:

- change permissions
- activate plugins
- resolve sync conflicts
- approve credit without policy
- stamp fiscal documents while offline
- modify canonical pricing without sync

## Sync recovery

When connection returns, the system should move through:

```text
offline_operational -> recovery_syncing -> online
```

If conflicts appear:

```text
offline_operational -> recovery_syncing -> conflict_required
```

## Non-negotiables

- No silent offline writes.
- No fiscal promise while offline.
- No hidden conflict resolution.
- No plugin offline support without declared policy.
- No offline credit override unless explicitly permitted.
- No local event without audit metadata.
- No user-facing lie that says "synced" before confirmation.

## Acceptance checklist

An offline-capable flow is accepted only if it declares:

- offline state support
- cached data requirements
- local event shape
- sync behavior
- conflict behavior
- audit behavior
- blocked actions
- degraded mode
- PC recovery path
- Tablet UI feedback
