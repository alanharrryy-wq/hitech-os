# PRISMA Change Intelligence Capability Map

Status: `CANONICAL_ANTI_REWORK_GATE`

This document is the human-readable projection of `PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json`. The JSON file is the machine-readable authority.

## Mandatory order

For every PRISMA Change Intelligence technical proposal or repository task:

`Factory Ledger -> Capability Map -> DONE/VERIFY/FIX/BUILD/EXTERNAL -> nextGate -> fresh task-exact Authority Mesh -> mutation/evidence`

A proposal that does not name the affected capability IDs is **BLOCKED**. A capability marked `doNotRebuild=true` cannot be proposed as a rebuild. `UNKNOWN`, missing, stale, or contradictory capability state is `BLOCKED_ANTI_REWORK`, never an invitation to guess.

Pure business/commercial analysis may remain read-only under the existing issue #250 governance rule. The moment a proposal authorizes Git-tree/source/config/workflow/runtime work, this gate applies.

## Authority provenance

- governed repo head: `42a533c0085aafdc32b27b854b14615d2b695070`
- Authority Mesh run: `32210002453`
- artifact: `9350435721`
- request digest: `f00e115802ee0b319044d7a95cd17b36ea0135299f5e13ebdd67206b9e9e7302`
- result: `PASS_COMPOSED_AUTHORITY_MESH`
- lanes: `2/2`
- required authority/directory coverage: `100%`
- blockers: `0`
- Layer Map: `present`

## Anti-rework decisions

The existing Code Atlas / Customer Wow engine already owns repository inventory, authority resolution, graphs, prepare/verify, Authority Packs, Evidence Reports/bundles, ROI raw instrumentation, and customer runner contracts. Those capabilities are `DONE` and `doNotRebuild=true`.

The Cloud Center surface is already a merged runtime-verified slice. Its currently disconnected Repository, Analysis Runs, Authority/Evidence, Entitlements and ROI areas are **adapter/projection work only**. They are not permission to create second repository, run, authority, evidence, licensing, or ROI engines.

Private-repository rental V2, bounded Go/Java dependency intelligence, and Go `actionableReview` are reuse-only unless fresh evidence proves a specific defect. The human study kit is reuse-only; missing human measurement is an `EXTERNAL` gate, not a coding backlog.

Independent-agent replication remains externally blocked by evaluator availability. Hosted multi-tenant execution and enterprise IAM/security are separate future builds and must never be inferred from the current local/portable runner contracts.

## Operational commands

Validate the canonical map:

```powershell
python "PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py" --validate-map
```

Before a proposal or mutation, create a request JSON with explicit `capabilityIds` and run:

```powershell
python "PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py" --request "<request.json>"
```

For `MUTATION`, the request must carry a fresh task-exact `PASS_COMPOSED_AUTHORITY_MESH`, 100% authority coverage, zero blockers, exact current repo HEAD, and `layerMapPresent=true` for visual work.

## Capability index

The canonical JSON currently registers 31 Change Intelligence capabilities across core intelligence, change authority, evidence, ROI, runners/private-repo rental, impact intelligence, Cloud Center projections, human/independent evidence, and hosted/enterprise productization. Each row binds classification, current status, do-not-rebuild semantics, evidence, next gate, proposal rule, and protected existing owners for BUILD entries.
