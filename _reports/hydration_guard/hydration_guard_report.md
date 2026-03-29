# Hydration Guard Audit Report

- Repo root: `F:\repos\hitech-os`
- Files scanned: **10361**
- Files skipped: **40**
- Total findings: **16505**
- Tool version: **1.0.0**

## Findings by category

- `client_boundary_hint`: 101
- `diagnostic_hint`: 43
- `dom_mutation_signature`: 16
- `dynamic_ssr_false`: 14
- `hydration_keyword`: 883
- `suppress_hydration_warning`: 18
- `tooling_route_hint`: 15021
- `use_client`: 409

## Recommendations

- Investigate affected internal routes for narrow client-only isolation. The warning signature resembles external DOM mutation before hydration.
- Review all dynamic(..., { ssr: false }) usages and confirm they are scoped narrowly to internal tooling subtrees rather than full route trees.
- Audit suppressHydrationWarning usages and replace broad suppression with route-local root cause analysis where possible.

## Likely internal tooling paths

- `tools\codex\worktrees\C_features\apps\keystone\components\pitch\__tests__\layerResolution.matrix.test.ts`
- `scripts\hydration_guard_bundle\hydration_guard_bundle\_selftest\hydration_guard_findings.json`
- `tools\codex\runs\20260228_164549_2F73\B_tooling\FILES\packages\ui-kit\tests\layers\resolveLayerFlags.determinism.test.ts`
- `tools\codex\worktrees\C_features\apps\keystone\components\pitch\__tests__\routeNavigation.matrix.test.ts`
- `tools\codex\worktrees\A_core\apps\keystone\tests\pitch-engine-core\mass-invariants.test.ts`
- `tools\codex\worktrees\A_core\tools\codex\runs\20260304_061005_61C9\A_core\FILES\apps\keystone\tests\pitch-engine-core\mass-invariants.test.ts`
- `tools\codex\worktrees\D_validation\apps\keystone\tests\pitch-engine-validation\fixtures\capability_degrade_scenarios.generated.ts`
- `apps\keystone\app\dev\_luxury\registry\kpiCatalogBulk.ts`
- `apps\keystone\app\dev\_luxury\registry\presetGallery.ts`
- `apps\keystone\app\dev\_luxury\registry\surfaceRecipeCatalog.ts`
- `tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\kpiCatalogBulk.ts`
- `tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\presetGallery.ts`
- `tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\surfaceRecipeCatalog.ts`
- `tools\codex\worktrees\B_tooling\tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\kpiCatalogBulk.ts`
- `tools\codex\worktrees\B_tooling\tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\presetGallery.ts`
- `tools\codex\worktrees\B_tooling\tools\codex\runs\20260305_092736_F9A0\B_tooling\FILES\apps\keystone\app\dev\_luxury\registry\surfaceRecipeCatalog.ts`
- `tools\codex\runs\20260305_092736_F9A0\Z_integrator\FINAL_REPORT.txt`
- `tools\codex\runs\20260305_092736_F9A0\_context\REPO_TREE.txt`
- `scripts\hydration_guard_bundle\hydration_guard_bundle\_selftest\hydration_guard_report.md`
- `tools\codex\runs\20260304_130900_QA11\_context\REPO_TREE.txt`

## Risky broad workaround paths

- None detected from the configured heuristics.

## Sample findings

- **LOW** `tooling_route_hint` in `AGENTS.md:165` -> `B_tooling` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `AGENTS.md:173` -> `- isolated workspaces` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `AGENTS.md:249` -> `tools/_local/debug` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:15` -> `- Debug overlay behavior needed deterministic client-only mounting with explicit default-off gating:` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:17` -> `- apps/keystone/components/pitch/debug/debug-overlay-mount.tsx:6-18` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:18` -> `- apps/keystone/components/pitch/debug/overlay-gate.ts:1-2` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:28` -> `- apps/keystone/components/pitch/debug/overlay-gate.ts` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:29` -> `- apps/keystone/components/pitch/debug/debug-overlay-mount.tsx` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:30` -> `- apps/keystone/components/pitch/debug/debug-overlay-client.tsx` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `FINAL_REPORT.md:32` -> `- apps/keystone/visual-tests/hydration-console-guard.ts` (pattern match)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:34` -> `- apps/keystone/scripts/scene-studio-runner.mjs` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:48` -> `- Set: NEXT_PUBLIC_PITCH_DEBUG=1` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.md:49` -> `- Optional route query for panel rendering path: add `?debug=1` to the pitch URL.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.txt:6` -> `- Integrated worker outputs for A_core, B_tooling, C_features, D_validation, and Z_worker into main workspace.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.txt:8` -> `- Resolved TypeScript conflicts and exactOptionalPropertyTypes issues in dev tooling and data-spine.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.txt:60` -> `Next Steps for Control Room HUD Frames` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.txt:61` -> `1) Wrap current HUD shell with frame preset from packages/ui-kit/src/luxury/frames/applyFrame.ts.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `FINAL_REPORT.txt:62` -> `2) Bind HUD theme state to styleId/surfaceId/materialId/perfProfile/motionLevel.` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `package.json:15` -> `"quality": "pnpm run env:validate && pnpm run deps:check && pnpm run workspace:validate && pnpm run health && pnpm run lint && pnpm run typecheck && pnpm run test && pnpm run build && pnpm run snapshot:hos:validate",` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `package.json:40` -> `"workspace:validate": "node tools/scripts/validate_workspace_boundaries.mjs",` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:59` -> `specifier: workspace:*` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:62` -> `specifier: workspace:*` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:129` -> `specifier: workspace:*` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:132` -> `specifier: workspace:*` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:188` -> `packages/tooling: {}` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:1904` -> `debug@4.4.3:` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:3483` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:3499` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4217` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4229` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4244` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4255` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4268` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4282` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4588` -> `debug@4.4.3:` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4738` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:4992` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:5638` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:5656` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:5711` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `pnpm-lock.yaml:5746` -> `debug: 4.4.3` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `prettier.config.cjs:1` -> `module.exports = require("./packages/tooling/prettier/prettier.config.cjs");` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `WindowManagerProvider_hydration_diff_snippet.txt:3` -> `Fuente: f:\repos\hitech-os\apps\keystone\app\dev\scene-studio\window-manager\WindowManagerProvider.tsx` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `WindowManagerProvider_hydration_diff_snippet.txt:8` -> `diff --git a/apps/keystone/app/dev/scene-studio/window-manager/WindowManagerProvider.tsx b/apps/keystone/app/dev/scene-studio/window-manager/WindowManagerProvider.tsx` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `WindowManagerProvider_hydration_diff_snippet.txt:10` -> `--- a/apps/keystone/app/dev/scene-studio/window-manager/WindowManagerProvider.tsx` (likely internal tooling subtree)
- **LOW** `tooling_route_hint` in `WindowManagerProvider_hydration_diff_snippet.txt:11` -> `+++ b/apps/keystone/app/dev/scene-studio/window-manager/WindowManagerProvider.tsx` (likely internal tooling subtree)
- **MEDIUM** `hydration_keyword` in `WindowManagerProvider_hydration_diff_snippet.txt:36` -> `+function hydrateStateFromStorage(previous: WindowManagerState): WindowManagerState {` (pattern match)
- **MEDIUM** `hydration_keyword` in `WindowManagerProvider_hydration_diff_snippet.txt:88` -> `+    setState((previous) => hydrateStateFromStorage(previous));` (pattern match)
- **MEDIUM** `hydration_keyword` in `WindowManagerProvider_hydration_diff_snippet.txt:121` -> `SNIPPET EXACTO: buildInitialState + hydrateStateFromStorage` (pattern match)
- **MEDIUM** `hydration_keyword` in `WindowManagerProvider_hydration_diff_snippet.txt:137` -> `function hydrateStateFromStorage(previous: WindowManagerState): WindowManagerState {` (pattern match)
