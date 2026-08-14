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
8. The current Tablet `Cobrar` candidate remains blocked because the compact layer index does not publish an exact `layerId`.
