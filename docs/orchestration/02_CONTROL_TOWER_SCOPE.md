# Control Tower Scope

## Domain name

`control_tower`

## Target repo path

`F:\repos\hitech-os\control_tower`

## Mission

Create a governance and assurance layer that sits above stabilized operational domains and makes coexistence explicit, durable, and auditable.

## Positive scope

`control_tower` is allowed to define and document:

- boundaries
- ownership
- domain relationships
- allowed vs forbidden touch points
- promotion gates
- artifact contracts
- snapshot contracts
- assurance logic
- work-order and coordination semantics
- audit-oriented read models
- non-invasive state consolidation

## Explicit non-scope

`control_tower` is not allowed to become:

- another engine remediation loop
- another cloudflare healer
- another scheduler controller
- an owner of engine runtime mutation
- an owner of `git_sentinel_modular` internals
- an excuse to absorb sibling systems into a single invasive mega-tool

## Protected closed domains

The following are already stabilized and are not to be reopened by default:

### `git_sentinel_modular`
Status:
- applied
- validated
- closed

### `engine_guardian`
Status:
- applied
- validated
- activated
- closed

### legacy protection
`HITECH-OS-GitSentinel-Guardian` remains intact and must not be casually touched.

## Operating model

The recommended operating model for the next phase is:

- **Chat A** owns normative/write-side governance definition
- **Chat B** owns read-side state, registry, snapshot, and audit

This keeps the governance layer expressive without turning it into a new invasive operational subsystem.

## Design constraints

The new domain must be:

- explicit
- low-ambiguity
- non-invasive
- audit-friendly
- compatible with local user execution
- easy to place by Codex
- compatible with full-file zip delivery
- split-friendly across parallel chats

## Minimum success criteria

The `control_tower` phase is successful only if it produces:

- documentary boundaries that stop ownership drift
- a stable shared dictionary
- a clear file allocation split
- promotion gates that prevent sloppy rollout
- artifact and snapshot contracts that make evidence legible
- an assurance model that reads and reports without hijacking operational ownership
