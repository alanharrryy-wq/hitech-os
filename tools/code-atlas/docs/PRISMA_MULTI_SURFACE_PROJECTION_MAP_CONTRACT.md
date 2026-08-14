# PRISMA Multi-Surface Projection Map Contract V1

Status: `SOURCE_ONLY_BUILD_CONTRACT`

## Purpose

Close the mapping gap between the canonical PRISMA visual governor and current Tablet, PC and Mobile source targets without inventing owners, selectors or runtime bindings.

The compiler consumes certified UIMAP/component-atlas evidence and the existing RIFAT/Atlasfin/UI Bridge authorities. It emits a deterministic read-only projection matrix that says, per component, whether the exact chain needed for a future visual application is proven.

## Canonical chain

`neutral meaning -> identity/profile -> recipe -> surface adapter -> route -> owner -> region -> slot -> component -> visual target -> binding -> neutral layer -> implementation layer -> source hash`

A target may be marked `READY_FOR_EXACT_TARGET_AUTHORITY_PREFLIGHT` only when the source UIMAP record is `SOURCE_RESOLVED`, the full trace is present, NDC/source drift gates allow read-only resolution, and at least one compatible recipe produces a clean UI Bridge plan.

## Inputs

- current certified UIMAP batch(es) or component-atlas JSON accepted by `BridgeRepository`;
- `tools/code-atlas/profiles/prisma-ui-bridge.v1.json` or an equivalent explicit UI Bridge profile;
- RIFAT identity recipes / portable recipe sources already configured by the profile;
- Atlasfin surface-adapter registry;
- RIFAT static surface binding registry;
- RIFAT element binding registry;
- Atlasfin canonical visual reference registry.

## Outputs

- `PRISMA_UI_MULTI_SURFACE_PROJECTION.json`
- `PRISMA_UI_MULTI_SURFACE_BLOCKERS.json`
- `PRISMA_UI_MULTI_SURFACE_SUMMARY.md`

The JSON projection includes per-surface counts for Tablet, PC and Mobile, exact trace evidence, source hashes, visual targets, compatible recipe IDs, deterministic read-only plans and explicit blockers.

## Hard safety rules

- `applicationEnabled=false`
- `runtimeMutationAllowed=false`
- `productApplicationAllowed=false`
- no inferred `ownerId`, `routeId`, `regionId`, `slotId`, `componentUiId`, `layerId` or implementation layer;
- no CSS/runtime/product writes;
- no `!important` or global override layer;
- no process kill, port release, dev-server start or Prisma regeneration;
- source drift or incomplete trace remains blocked;
- a source-only plan is not visual certification and is not permission to apply a recipe.

## Command

Run through the existing Code Atlas UI Bridge:

```text
code-atlas-plus ui-bridge projection-map <UIMAP inputs...> --profile tools/code-atlas/profiles/prisma-ui-bridge.v1.json --surface tablet --surface pc --surface mobile --output-root <evidence-dir>
```

Omitting `--surface` defaults to Tablet + PC + Mobile.

## Future application gate

The projection map only makes future work cheap and deterministic. An actual request such as “reproduce this Atlasfin visual identity on these surfaces” must still run a fresh exact-target Authority Mesh, verify source hashes and scope, produce BEFORE evidence, apply only the authorized target set, run focused gates, capture AFTER evidence and automatically roll back on failure.
