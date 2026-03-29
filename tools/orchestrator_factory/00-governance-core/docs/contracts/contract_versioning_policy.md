
# Contract Versioning Policy

## Purpose
Shared contracts and interfaces need version semantics that work across packages, runs, and retries.

## Version format
Use semantic versioning:
`MAJOR.MINOR.PATCH`

## Meaning
- `PATCH`: editorial correction, clarification, or non-behavioral fix
- `MINOR`: additive backward-compatible expansion
- `MAJOR`: breaking change or changed invariant

## Freeze-state interaction
### Draft
- may change rapidly
- must not be treated as production-safe
- may use `0.x` versions

### Provisional
- must be versioned
- may be consumed for drafting only
- breaking changes require explicit consumer notice

### Frozen
- versioned and safe for downstream production work
- any version change requires a decision record
- a breaking frozen change requires a `MAJOR` bump

### Superseded
- must point to the replacement version or decision record
- must state whether it is deprecated first or immediately invalid

## Required register fields
Every governed shared contract should record:
- `contract_id`
- owner package
- source path
- version
- freeze state
- status: active, deprecated, or superseded
- downstream consumers
- supersedes or superseded-by
- compatibility notes

## Work packet and bundle expectations
- work packets should carry explicit `contract_refs` when contract usage matters
- bundles and package reports should echo the contract versions they consumed or changed
- do not silently target a newer contract version than the active packet or baseline allows

## Deprecation and supersession
- deprecation should state the sunset trigger
- supersession must identify the replacing version
- downstream consumers must be able to tell whether coexistence is temporary, permanent, or disallowed
