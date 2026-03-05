# Interface 02 Map

## Scope note
- Requested edit scope is `apps/keystone/src/**`.
- Current Keystone scene implementation is located under `apps/keystone/app/**`, `apps/keystone/components/**`, and `apps/keystone/lib/**`.
- This file is placed in `apps/keystone/src/_codex` as requested, but Interface 02 source files currently live outside `src`.

## What Interface 02 is
Interface 02 maps to Pitch Screen 02 (Industrial Flow):

- Route: `/pitch/02-industrial-flow`
- Screen slug: `02-industrial-flow`
- Scene Studio registry entries:
  - `pitch-02-industrial-flow-neutral-desktop`
  - `pitch-02-industrial-flow-layered-desktop`
- Primary exported UI component: `Screen02IndustrialFlowCinematic`

Registration and routing points:

- Scene Studio default scene registry: `apps/keystone/lib/scene-studio/default-scenes.ts`
- Scene Studio state/bootstrap source: `apps/keystone/components/scene-studio/use-scene-studio-state.ts`
- Visual scene manifest entries: `docs/visual-scenes/SCENES.json`
- Next.js route entry: `apps/keystone/app/pitch/02-industrial-flow/page.tsx`

## Mapping: Interface 02 -> code
- Scene IDs: `pitch-02-industrial-flow-neutral-desktop`, `pitch-02-industrial-flow-layered-desktop`
- Scene/route name: `Pitch 02` / `02-industrial-flow`
- Route: `/pitch/02-industrial-flow`
- Route page export: `default async function PitchIndustrialFlowPage(...)`
- Screen wrapper export: `export function ScreenIndustrialFlow(...)`
- Screen implementation export: `export function Screen02IndustrialFlowCinematic(...)`

## Primary Entry Files
- `apps/keystone/app/pitch/02-industrial-flow/page.tsx`
- `apps/keystone/components/pitch/screen-industrial-flow.tsx`
- `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`

Supporting registration/listing files:
- `apps/keystone/lib/scene-studio/default-scenes.ts`
- `apps/keystone/lib/pitch/deck-view-model.ts`
- `apps/keystone/components/pitch/route-index/pitch-route-card.tsx`
- `docs/visual-scenes/SCENES.json`

## Direct Dependencies
### Route/page-level dependencies
From `apps/keystone/app/pitch/02-industrial-flow/page.tsx`:
- `LayerFlagsProvider` (`@hitech/ui-kit`)
- `PitchShell`, `ScreenIndustrialFlow` (`apps/keystone/components/pitch` exports)
- `PitchLayerDevTools`
- `buildPitchShellFrameModel`
- `resolvePitchSearchParams`, `resolvePitchLayerFlags`
- `PITCH_DECK_FIXTURE`, `PITCH_SCREEN_FIXTURES` (`@hitech/contracts`)

### Screen implementation dependencies
From `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`:
- Layout primitives:
  - `PitchSection`
  - `PitchCardGrid`, `PitchCardGridItem`
  - `PitchDataChip`
  - `PitchExpandablePanel`
- Visual primitives:
  - `PitchSparkline`
  - `PitchMiniBars`
  - `PitchRadialGauge`
  - `PitchKpiChipCloud`

### Scene Studio dependencies
- `createDefaultSceneLibrary()` from `apps/keystone/lib/scene-studio/default-scenes.ts`
- Loaded by `useSceneStudioState()` in `apps/keystone/components/scene-studio/use-scene-studio-state.ts`

## Styling Touchpoints
- Global import of pitch theme CSS:
  - `apps/keystone/app/globals.css` (`@import "../components/pitch/theme/pitch-cinematic.css";`)
- Shell screen selector:
  - `apps/keystone/components/pitch/shell/pitch-shell.tsx` (`data-pitch-screen={model.nav.activeSlug ?? "pitch-index"}`)
- Screen-02 specific overrides:
  - `apps/keystone/components/pitch/theme/pitch-cinematic.css`
  - Selectors targeting `data-pitch-screen="02-industrial-flow"` and `#industrial-flow`
- Screen-local utility classes and CSS variable usage:
  - `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`

## Safe Edit Zones
Use these files for Interface 02 changes:

- Layout/content and composition:
  - `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`
- Screen wrapper behavior:
  - `apps/keystone/components/pitch/screen-industrial-flow.tsx`
- Route-level orchestration, shell model wiring, debug tools:
  - `apps/keystone/app/pitch/02-industrial-flow/page.tsx`
- Scene Studio metadata/title/query defaults for Interface 02 scenes:
  - `apps/keystone/lib/scene-studio/default-scenes.ts`
- Route metadata/cards text/icons for 02 in pitch index:
  - `apps/keystone/lib/pitch/deck-view-model.ts`
  - `apps/keystone/components/pitch/route-index/pitch-route-card.tsx`
- Screen-02 CSS overrides and visual tuning:
  - `apps/keystone/components/pitch/theme/pitch-cinematic.css`

## Do Not Touch
- Generated/build outputs:
  - `apps/keystone/.next/**`
  - `apps/keystone/.turbo/**`
  - `apps/keystone/test-results/**`
- Visual-proof artifacts and baselines/snapshots:
  - `artifacts/keystone-scene-studio/**`
  - Any baseline/snapshot artifacts produced by scene visual workflows
- Runner/report outputs:
  - Generated outputs from `apps/keystone/scripts/scene-studio-*.mjs`
- Do not run baseline update flows as part of Interface 02 UI editing unless explicitly requested.

## If you want to change X, edit Y
- Layout structure or card arrangement:
  - `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`
- Colors/theme accents (screen-specific):
  - `apps/keystone/components/pitch/theme/pitch-cinematic.css`
  - `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx` (token usage in props/classes)
- Typography/spacings:
  - `apps/keystone/components/pitch/screens/screen-02-industrial-flow-cinematic.tsx`
  - shared primitives in `apps/keystone/components/pitch/layout/**`
- Component behavior/data wiring for Screen 02:
  - `apps/keystone/app/pitch/02-industrial-flow/page.tsx`
  - `apps/keystone/components/pitch/screen-industrial-flow.tsx`
- Scene Studio listing/title/query defaults for Interface 02:
  - `apps/keystone/lib/scene-studio/default-scenes.ts`
- Pitch index card metadata for Interface 02:
  - `apps/keystone/lib/pitch/deck-view-model.ts`
  - `apps/keystone/components/pitch/route-index/pitch-route-card.tsx`
