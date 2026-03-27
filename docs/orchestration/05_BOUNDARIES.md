# Boundaries

This document defines the hard coexistence boundaries for the stabilized system and the new `control_tower` phase.

## Boundary doctrine

Boundaries exist to prevent:
- accidental ownership drift
- duplicate operational loops
- scheduler overlap
- path mutation by the wrong domain
- “temporary” hacks that become silent architecture

The default boundary posture is conservative.
Authority must be explicit, not implied.

## Domain boundary 1: `git_sentinel_modular`

### Canonical path
`F:\repos\hitech-os\tools\hos\git_sentinel_modular`

### Inside boundary
Allowed internal concerns:
- package internals
- package tests
- package docs
- package plugin seam
- package-local rollout/control behavior

### Outside boundary
Not part of its authority:
- engine public health ownership
- `engine_guardian` scheduler ownership
- `engine_guardian` runtime root
- Cloudflare public engine operations
- `control_tower` governance ownership

### External access by others
- `control_tower` may describe it
- `control_tower` may read state about it
- `engine_guardian` must not absorb its internals
- no domain may rewrite it casually under the excuse of orchestration

## Domain boundary 2: `engine_guardian`

### Canonical path
`F:\repos\hitech-os\engine_guardian`

### Runtime root
`F:\OneDrive\Descargas\engine_guardian`

### Inside boundary
Allowed owned concerns:
- public engine orchestration
- public endpoint truth model
- origin checks/remediation wrapper
- cloudflared validation wrapper
- official scheduler contract
- guardian runtime folders
- guardian-owned reports, backups, logs, snapshots, install outputs
- wrapper relationship over `repo_analizer`
- guardian igniters relationship

### Outside boundary
Not part of its authority:
- internal rewrite of `git_sentinel_modular`
- broad rewrite of `tools\infra\cloudflare`
- ownership of `control_tower`
- casual mutation of `HITECH-OS-GitSentinel-Guardian`

## Domain boundary 3: `repo_analizer`

### Canonical path
`F:\repos\hitech-os\tools\graphviz\repo_analizer`

### Boundary meaning
`repo_analizer` is a sibling domain.
It may be wrapped or referenced by `engine_guardian`, but it is not absorbed into guardian internals and does not become the owner of engine critical health.

### Consequence
Any future `control_tower` model must preserve:
- sibling status
- non-absorption
- non-owner role for critical engine health

## Domain boundary 4: `control_tower`

### Canonical target path
`F:\repos\hitech-os\control_tower`

### Allowed concerns
- policy
- boundaries
- ownership
- gates
- artifact contracts
- snapshot contracts
- assurance logic
- audit-oriented state consolidation
- coordination semantics

### Forbidden role expansion
`control_tower` must not become:
- an operational healer
- a scheduler registrar
- a service controller
- a runtime mutator for guardian
- an owner of sentinel internals
- a Cloudflare operator

## Boundary between Chat A and Chat B

### Chat A boundary
Owns:
- normative and contractual governance definitions
- write-side policy modeling
- non-runtime coordination semantics

### Chat B boundary
Owns:
- read-side state observation
- snapshot consolidation
- artifact registry
- assurance reporting
- drift visibility

### Hard no-overlap
Neither chat may produce or edit the same target file.

## Protected legacy boundary

### Protected entity
`HITECH-OS-GitSentinel-Guardian`

### Rule
It remains intact unless new evidence requires deliberate action.
The `control_tower` phase does not receive implied permission to touch it.

## Boundary violation examples

The following are violations:

- Chat B adds a promotion rule in code or docs owned by Chat A
- Chat A defines a runtime reader that mutates guardian state
- `control_tower` schedules tasks for guardian
- a snapshot reader restarts services
- a governance bundle rewrites `git_sentinel_modular` internals
- a convenience patch widens ownership without documentary revision

## Enforcement principle

When a conflict appears, prefer:
- stopping promotion
- marking blocked
- requesting explicit governance revision

Do not “just proceed” across a boundary.
