# PRISMA Identity Binding Contract · IDBIND1

Status: `SOURCE_READY_PARTIAL_BINDINGS`

IDBIND1 resolves portable identity meaning into governed target coordinates without applying product changes.

## Canonical chain

`neutral meaning → identity/profile → recipe → surface → owner → route → region → slot → component → layer`

## Hard rules

1. `RESOLVED` requires non-null `ownerId`, `routeId`, `regionId`, `slotId`, `componentUiId` and `layerId`.
2. Every reference must exist in the current read-only RIFAT authority indexes.
3. Any authority hash drift blocks resolution and requires a fresh Authority Mesh.
4. One-to-many mappings are allowed only when the complete target set is demonstrated. Sample-only sets remain blocked.
5. Shared UI is neutral source authority, not a product location.
6. Binding envelopes are instruction-only. They never mutate runtime or product files.
7. No owner, route, region, slot, component or layer may be inferred merely from naming convention.
8. The current Tablet `Cobrar` target is resolved by `BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1` with exact layer `LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE` in the current element-binding registry. Any document or generated projection that claims the exact layer is still missing is stale and must fail the consistency gate.
9. `visualFamilyId` is visual-semantic authority only. It must never populate or synthesize NDC/business `neutralMeaningId`.
10. Source-only visual binding/layer identifiers may be generated deterministically only from exact UIMAP component coordinates plus exact `visualTargets` source evidence (`styleSourceFile`, anchor, and `sourceHash`). Generated visual-control projections do not certify product runtime or authorize application.
11. PC and Mobile remain blocked from binding-ready/product-application status until generated exact route-owner, region-owner, editable-slot and layer coverage is complete enough for the applicable gate and a fresh task-exact Authority Mesh authorizes the next action.
