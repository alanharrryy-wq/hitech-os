# SCENE_STUDIO_OPERATIONS

## Scope

This document defines operational tooling for Scene Studio triage, retention, rerun requests, and pinning support without modifying Scene Studio core runtime code.

## Artifact Root

`F:/repos/hitech-os/artifacts/keystone-scene-studio`

Managed outputs:

- `index.json`
- `index.md`
- `index.html`
- `triage/*`
- `retention/*`
- `decisions/*`
- `notes/*`
- `rerun-requests/*`

## CLI Surface

- `keystone:scene:triage`
- `keystone:scene:accept`
- `keystone:scene:reject`
- `keystone:scene:rerun`
- `keystone:scene:notes`
- `keystone:scene:pin`
- `keystone:scene:prune`
- `keystone:scene:doctor`
- `keystone:scene:onebutton`

## Triage Workflow

### 1. Open Triage Index

Run:

`pnpm --filter @hitech/keystone run keystone:scene:triage`

Optional open-in-browser:

`pnpm --filter @hitech/keystone run keystone:scene:triage -- --open`

### 2. Accept or Reject

Accept:

`pnpm --filter @hitech/keystone run keystone:scene:accept -- --sceneId=<id> --runId=<id>`

Reject:

`pnpm --filter @hitech/keystone run keystone:scene:reject -- --sceneId=<id> --runId=<id>`

### 3. Append Notes

`pnpm --filter @hitech/keystone run keystone:scene:notes -- --sceneId=<id> --runId=<id> --append="<note>"`

### 4. Queue Rerun

`pnpm --filter @hitech/keystone run keystone:scene:rerun -- --sceneId=<id>`

Creates request file:

`rerun-requests/<sceneId>.json`

## Decision Records

Decision payload structure:

- `sceneId`
- `runId`
- `current`
- `history[]`

Each history entry includes:

- `status`
- `actor`
- `reason`
- `metadata`
- `decidedAtUtc`

Statuses:

- `accepted`
- `rejected`
- `pending`

## Notes Records

Notes are markdown files in:

`notes/<sceneId>--<runId>.md`

Format:

- heading `# Diff Notes`
- timestamp section headings
- actor line
- note line

Guardrails:

- max note length enforced
- actor max length enforced
- deterministic append-only order

## Retention Policy

Default keep-last:

- `20` files per owner segment.

Retention applies to operation records under `retention/`.

Command:

`pnpm --filter @hitech/keystone run keystone:scene:prune -- --keep=20`

Output:

- retention summary JSON
- updated scene index files

## Pinning

Pin command writes marker:

`retention/<sceneId>--<runId>.PIN.marker`

Marker semantics:

- intent marker for operators
- used by governance reviews
- durable across prune operations

## Doctor

Scene doctor reuses shared deterministic checks and validates operation layout initialization.

Checks include:

- node/pnpm
- Playwright CLI/browser
- artifact root permissions
- port status
- scene operation index generation

## One-Button

Scene one-button flow executes:

1. `keystone:scene:doctor`
2. `keystone:scene:triage`
3. `keystone:scene:prune`

Non-interactive and nonzero on failure.

## Governance and Ownership

Scene tooling intentionally does not mutate Scene Studio core components, route code, or domain models.

When checks require non-owned edits, tooling reports actionable WARN/FAIL reason instead of mutating restricted files.

## Operational Safety

- IDs are sanitized and path-safe.
- traversal tokens are blocked.
- all writes remain inside artifact root.
- every command logs deterministic JSON output.

## Incident Response

### Missing index files

Run:

- `keystone:scene:triage`

This recreates layout and index files.

### Corrupt decision file

Re-run accept/reject command with same `sceneId` and `runId`; command rewrites deterministic JSON structure.

### Excessive retention growth

Run prune with explicit keep value:

`keystone:scene:prune -- --keep=10`

## Example Session

1. `keystone:scene:doctor`
2. `keystone:scene:triage -- --open`
3. `keystone:scene:accept -- --sceneId=01-double-engine--scene --runId=20260304_061005_61C9`
4. `keystone:scene:notes -- --sceneId=01-double-engine--scene --runId=20260304_061005_61C9 --append="Diff accepted after copy lock review."`
5. `keystone:scene:pin -- --sceneId=01-double-engine--scene --runId=20260304_061005_61C9`
6. `keystone:scene:prune`

## Compatibility

Windows-first behavior is default. Paths are normalized to forward slashes in reports for readability.

## Version

- `1.0.0` initial scene operations tooling.
