# Status Snapshot

This document defines the documentary contract for consolidated status snapshots.

## Purpose

A snapshot provides a point-in-time view of the governed system without mutating it.

It exists to answer:
- what domains are present
- what lifecycle state each domain claims
- what evidence supports that state
- what is protected
- what is blocked
- where drift may be emerging

## Snapshot subjects

The initial snapshot scope should include:

- `git_sentinel_modular`
- `engine_guardian`
- `control_tower`

`repo_analizer` may appear as a related sibling domain when relevant.

## Required snapshot concerns

A snapshot should be able to represent:

- domain name
- canonical path
- declared lifecycle state
- last known evidence references
- ownership mode relative to `control_tower`
- verdict status
- warnings
- blockers
- drift indicators

## Example baseline interpretation

### `git_sentinel_modular`
Expected baseline state:
- `applied`
- `validated`
- `closed`

### `engine_guardian`
Expected baseline state:
- `applied`
- `validated`
- `activated`
- `closed`

### `control_tower`
Expected initial state:
- documentary phase beginning
- no implied operational ownership expansion

## Snapshot rules

### Rule 1
A snapshot is descriptive, not curative.

### Rule 2
A snapshot may use evidence references but must not rewrite evidence.

### Rule 3
A missing field should cause `blocked` or explicit warning, not silent assumption.

### Rule 4
A snapshot must not imply ownership transfer.

## Drift types worth tracking

- documentary drift
- vocabulary drift
- lifecycle drift
- ownership drift
- path drift
- artifact drift
- boundary drift

## Forbidden snapshot behavior

Do not:
- auto-fix drift
- restart services
- disable tasks
- rewrite manifests
- create ghost “healthy” status without evidence

## Snapshot output philosophy

A good snapshot is:
- legible
- precise
- evidence-backed
- low-drama
- explicit about unknowns

A bad snapshot is:
- vague
- overconfident
- silently mutating
- full of implied promotions
