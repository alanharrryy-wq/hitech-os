# Code Atlas documentation index

> **Navigation only.** This file is not an authority source and does not grant certification status.

Use this index to distinguish current architecture/contracts from historical or feature-specific notes under `tools/code-atlas/docs`.

## Current overview

- [`../README.md`](../README.md)  
  Canonical current Code Atlas architecture and usage overview.

## Governing reusable boundary

- [`../AGENTS.md`](../AGENTS.md)  
  Workspace rules for agents and maintainers.

- [`../NEUTRALITY_POLICY.md`](../NEUTRALITY_POLICY.md)  
  Human-readable machine/repository/product neutrality policy.

- [`../CODE_ATLAS_NEUTRALITY_CONTRACT.json`](../CODE_ATLAS_NEUTRALITY_CONTRACT.json)  
  Machine-readable neutral-core / explicit-adapter boundary.

These documents define or describe reusable execution rules. A documentation index never overrides them.

## Current Change Intelligence / Customer Wow contract

- [`CODE_ATLAS_CUSTOMER_WOW_V1.md`](CODE_ATLAS_CUSTOMER_WOW_V1.md)  
  Customer Wow V1 architecture, fail-closed semantics, evidence, runner boundary and limitations.

- [`CODE_ATLAS_CUSTOMER_WOW_V1.contract.json`](CODE_ATLAS_CUSTOMER_WOW_V1.contract.json)  
  Machine-readable Customer Wow V1 contract.

Current governed state remains `LOCAL_VERIFIED`. External-repository evidence is broader but intentionally bounded; independent evaluator replication remains externally blocked and human usefulness remains unmeasured. `certifiable=false` and `productionCertified=false` remain unchanged by this index.

## How to interpret other files in this directory

Many files in `docs/` predate the Universal Intelligence + Customer Wow architecture or describe a single historical feature, UI experiment, support workflow or implementation phase.

Examples include families such as:

```text
ATLAS_PLUS_*
CODE_ATLAS_BLACK_GLASS_*
CODE_ATLAS_DEPENDENCY_*
CODE_ATLAS_SUPPORT_*
other versioned V01/V03/V04/V05 feature notes
```

Treat those files as **historical or feature-specific evidence/notes unless a current governing contract explicitly promotes them**.

They may still be useful for:

- implementation history;
- compatibility behavior;
- specialized feature context;
- prior visual/operator decisions;
- forensic evidence;
- migration and rollback understanding.

They must **not** be used by filename, age or detail level alone to claim:

- current architecture authority;
- repository-wide ownership;
- production readiness;
- production certification;
- current customer-facing behavior;
- universal repository compatibility.

## Current architecture map

```text
Universal Intelligence Core
  discovery / authority / graphs / impact / snapshot / drift / retrieval
        |
        v
Optional profiles and adapters
        |
        v
Change Intelligence / Customer Wow
  Change Studio / Authority Pack / Verify / Evidence / ROI
        |
        v
PASS / BLOCKED / UNKNOWN
```

Profiles and adapters are explicit opt-in. Semantic retrieval is not proof. Derived SQLite/query indexes are not authority. Impact Radius is not authorization.

## Product-specific documentation

PRISMA/hitech-os documentation may reference richer product-specific systems such as Authority Mesh, Factory Ledger, NDC, visual surfaces or local Windows paths. Those are explicit product/operator contexts, **not requirements of the universal Code Atlas core**.

For the current PRISMA Authority Mesh / AutoMesh v2 operator flow, use:

- [`../../../apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md`](../../../apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md)  
  Current GitHub-first operation, relevant-drift revalidation, fast-path/full-refresh behavior, artifact chaining/security, Git-blob/CRLF portability, Layer Map fail-closed rules, concurrency and evidence closure.

- [`../../../apps/terminal-de-venta-system/docs/ops/README.md`](../../../apps/terminal-de-venta-system/docs/ops/README.md)  
  PRISMA operational documentation index.

For PRISMA/hitech-os capability maturity, the repository Factory Ledger remains the canonical anti-rework status source. These navigation docs do not override it.

## Documentation maintenance rule

When Code Atlas architecture or a governed product adapter changes materially:

1. update the canonical [`../README.md`](../README.md) only with evidence-backed current behavior;
2. update governing contracts only when their actual contract changes;
3. update the appropriate product-specific runbook when operator behavior changes;
4. keep historical feature/exception docs historical instead of rewriting history;
5. add or adjust navigation here when needed;
6. do not promote source/local verification into production claims;
7. do not rebuild Universal Intelligence or Customer Wow merely to make documentation look current.

If documentation and source evidence disagree, resolve the governing source/evidence first. Do not create a green claim in Markdown.
