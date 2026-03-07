# Hydration Guard Audit Report

- Repo root: `/path/to/repo`
- Files scanned: **812**
- Files skipped: **41**
- Total findings: **17**
- Tool version: **1.0.0**

## Findings by category

- `client_boundary_hint`: 2
- `diagnostic_hint`: 1
- `dynamic_ssr_false`: 2
- `hydration_keyword`: 4
- `tooling_route_hint`: 8

## Recommendations

- Review all `dynamic(..., { ssr: false })` usages and confirm they are scoped narrowly to internal tooling subtrees rather than full route trees.
- Add opt-in hydration diagnostics for internal tooling boundaries so route, component, and strategy are logged only when explicitly enabled.
- The repo appears to contain internal tooling route hints without an obvious client-only boundary naming convention. Consider standardizing a reusable `InternalToolClientOnlyBoundary`.

## Likely internal tooling paths

- `apps/keystone/app/dev/scene-studio/page.tsx`
- `apps/keystone/components/internal-tooling/control-room.tsx`
- `apps/keystone/components/pitch/pitch-layer-devtools.tsx`

## Risky broad workaround paths

- `apps/keystone/app/dev/scene-studio/page.tsx`

## Sample findings

- **HIGH** `dynamic_ssr_false` in `apps/keystone/app/dev/scene-studio/page.tsx:12` -> `const StudioClient = dynamic(() => import('./scene-studio-client'), { ssr: false });` (broad client-only workaround candidate)
- **LOW** `tooling_route_hint` in `apps/keystone/components/internal-tooling/control-room.tsx:1` -> `export function ControlRoom() {` (likely internal tooling subtree)
