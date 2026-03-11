# ARCHITECTURAL_GRAVITY_POLICY

STATUS: LAW

## Scope

Factory-level policy for graph-analysis outputs and impact-aware dispatch planning.

## Canonical Output Set (Z)

Canonical JSON:

- `GRAVITY_REPORT.json`
- `PROTECTED_NODES.json`
- `IMPACT_CONE_REPORT.json`
- `DEPENDENCY_DIFF.json`
- `DISPATCH_RECOMMENDATIONS.json`

Mirrors:

- `GRAVITY_SUMMARY.md`
- `DISPATCH_RECOMMENDATIONS.md`

## Canonical Enum Families

- reason codes: shared vocabulary in graph-analysis schemas
- risk levels: `NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- protection levels: `WATCHED`, `GUARDED`, `PROTECTED`, `LOCKED`
- impact radius categories: `LOCAL`, `MULTI_SCOPE`, `CROSS_WORKER`, `REPO_WIDE`

Legacy protection aliases remain accepted for reader compatibility:

- `WATCH`, `ELEVATED`, `STRICT`

## Compatibility Metadata Requirement

Each canonical JSON artifact must include:

- `schema_version`
- `schema_family`
- `compatibility_mode`
- `minimum_reader_version`
- `breaking_change`

## Semantic Version Policy

- PATCH: non-breaking, non-semantic corrections
- MINOR: additive optional structures
- MAJOR: breaking schema/semantic changes

## Provenance Requirement

Each artifact must include:

- generator provenance (`actor`, `tool_name`, `tool_version`, `execution_mode`, `invocation_context`, `source_inputs`)
- repository comparison provenance
- snapshot lineage provenance

## Protected-Node Protocol

Mandatory steps:

1. declaration
2. impact cone
3. dependency diff
4. D review
5. Z approval

Missing step => `BLOCKED`.

## Dispatch Policy

Dispatch recommendations must include structured rationale:

- rationale codes
- evidence sources
- risk drivers
- dependency basis
- protocol requirements

Default behavior remains advisory for next iteration.
