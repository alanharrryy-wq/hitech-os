# Hydration Sentinel PRO Report

- Repo root: `F:\repos\hitech-os\tools\codex\worktrees\B_tooling`
- Files scanned: **414**
- Total findings: **411**
- Baseline ignored: **0**
- Risk level: **critical**
- Risk score: **2276.88**
- React graph nodes: **414**
- React graph edges: **601**

## Findings by category

- `hydration_keyword`: 211
- `browser_api_non_client`: 57
- `nondeterministic_render`: 49
- `dom_mutation_signature`: 22
- `storage_hydration`: 18
- `server_client_import`: 15
- `graph_server_client_chain`: 14
- `graph_nondeterministic_reachability`: 10
- `graph_storage_reachability`: 10
- `graph_dom_mutation_reachability`: 5

## Findings by severity

- `high`: 88
- `info`: 211
- `low`: 50
- `medium`: 62

## Regression summary

- Previous run available: **True**
- New findings: **0**
- Resolved findings: **0**
- Unchanged findings: **411**

## Graph trend summary

- Previous snapshot available: **True**
- Graph new findings: **0**
- Graph resolved findings: **0**
- Delta total findings: **0**

## Top risky paths

- `tools/codex/runs/20260305_092736_F9A0/B_tooling/FILES/apps/keystone/app/dev/_luxury/dataSpine.ts` -> score 180.0 (150 findings, highest `info`)
- `tools/codex/runs/20260305_092736_F9A0/B_tooling/FILES/apps/keystone/app/dev/_luxury/tools/localStorageSafe.ts` -> score 151.68 (16 findings, highest `high`)
- `apps/keystone/lib/pitch-engine-tooling/player.mjs` -> score 114.0 (14 findings, highest `high`)
- `tools/codex/runs/20260304_061005_61C9/B_tooling/FILES/apps/keystone/lib/pitch-engine-tooling/player.mjs` -> score 114.0 (14 findings, highest `high`)
- `apps/keystone/lib/pitch-engine-tooling/retention.mjs` -> score 81.0 (5 findings, highest `high`)
- `tools/codex/runs/20260304_061005_61C9/B_tooling/FILES/apps/keystone/lib/pitch-engine-tooling/retention.mjs` -> score 81.0 (5 findings, highest `high`)
- `tools/codex/runs/20260305_092736_F9A0/B_tooling/FILES/apps/keystone/app/dev/_luxury/tools/clipboard.ts` -> score 77.04 (7 findings, highest `high`)
- `apps/keystone/lib/pitch-engine-tooling/exec.mjs` -> score 64.8 (4 findings, highest `high`)
- `tools/codex/runs/20260304_061005_61C9/B_tooling/FILES/apps/keystone/lib/pitch-engine-tooling/exec.mjs` -> score 64.8 (4 findings, highest `high`)
- `tools/codex/runs/20260305_092736_F9A0/B_tooling/FILES/apps/keystone/app/dev/kpi-supermarket/KpiSupermarketClient.tsx` -> score 61.08 (7 findings, highest `medium`)

## React graph summary

- Entry points: **35**
- Client nodes: **46**
- Serverish nodes: **15**
- Shared nodes: **293**
- Tooling nodes: **60**

### Graph path counts

- `use_client`: 14
- `storage_api`: 10
- `nondeterministic`: 10
- `dom_mutation`: 5

### Graph notes

- Storage APIs are reachable from entrypoints. Focus on client-only post-mount hydration for those branches.
- Nondeterministic render sources are still reachable through the import graph. Stabilize them before SSR boundaries.
- At least one client island has high import fan-in. Consider slicing it into smaller islands.

## Recommendations

- Audit browser APIs and client boundaries together. Tighten the island contract where server entrypoints reach client-only surfaces.
- Review storage-backed render state and move persistence reads behind post-mount hydration or explicit client entrypoints.
- Replace render-time Date, random, and UUID generation with deterministic server data or client effects.
- Move DOM mutation helpers behind effects or tooling-only wrappers before they leak into normal entrypoints.
- Do not enable strict enforcement yet. Clean exclusions and highest-risk files before turning the scanner into hard policy.

## Sample findings

- [medium] storage_hydration :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:34 -> Storage-backed render or hydration state detected. Verify deterministic SSR fallback and post-mount hydration flow.
- [medium] storage_hydration :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:46 -> Storage-backed render or hydration state detected. Verify deterministic SSR fallback and post-mount hydration flow.
- [medium] storage_hydration :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:48 -> Storage-backed render or hydration state detected. Verify deterministic SSR fallback and post-mount hydration flow.
- [info] hydration_keyword :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:95 -> Hydration keyword matched: hydrate
- [info] hydration_keyword :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:107 -> Hydration keyword matched: hydrate
- [info] hydration_keyword :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:126 -> Hydration keyword matched: hydrate
- [info] hydration_keyword :: apps/keystone/app/dev/scene-studio/FloatingWindow.tsx:128 -> Hydration keyword matched: hydrate
- [medium] graph_nondeterministic_reachability :: apps/keystone/app/dev/scene-studio/SceneStudioEditor.tsx:1 -> Entrypoint reaches nondeterministic render logic. Stabilize values before crossing SSR/CSR boundaries.
- [low] graph_server_client_chain :: apps/keystone/app/dev/scene-studio/SceneStudioEditor.tsx:1 -> Serverish entrypoint reaches a client boundary through an import chain. Validate the island split and data handoff.
- [medium] graph_storage_reachability :: apps/keystone/app/dev/scene-studio/SceneStudioEditor.tsx:1 -> Entrypoint reaches storage-backed render logic. Prefer post-mount hydration or server-safe defaults.
- [medium] graph_nondeterministic_reachability :: apps/keystone/app/dev/scene-studio/page.tsx:1 -> Entrypoint reaches nondeterministic render logic. Stabilize values before crossing SSR/CSR boundaries.
- [low] graph_server_client_chain :: apps/keystone/app/dev/scene-studio/page.tsx:1 -> Serverish entrypoint reaches a client boundary through an import chain. Validate the island split and data handoff.
- [high] graph_storage_reachability :: apps/keystone/app/dev/scene-studio/page.tsx:1 -> Entrypoint reaches storage-backed render logic. Prefer post-mount hydration or server-safe defaults.
- [low] graph_server_client_chain :: apps/keystone/app/layout.tsx:1 -> Serverish entrypoint reaches a client boundary through an import chain. Validate the island split and data handoff.
- [medium] server_client_import :: apps/keystone/app/layout.tsx:1 -> Serverish file imports explicit client module: apps/keystone/providers/app-providers.tsx
