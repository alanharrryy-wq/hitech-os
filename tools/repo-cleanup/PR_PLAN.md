# PRISMA Repository Cleanup PR Plan

Status: UNBLOCKED_BY_SCENE_STUDIO_ISOLATION_PENDING_PR_MERGE

Repository root:

`F:\repos\hitech-os`

## Gate Before Any PR Work

This command now passes on branch `fix/remove-scene-studio-blocker` and must remain green after this branch merges:

```powershell
pnpm run typecheck
```

Current result:

GO, exit code `0`.

Evidence:

`F:\repos\hitech-os\tools\repo-cleanup\scene-removal\logs\root-typecheck-final.log`

## Required Precondition PR

### PR 0: Remove Scene Studio / Pitch From Active Scope

Purpose:

Restore the repository-wide typecheck baseline without repairing off-scope Scene Studio/Pitch and without touching PRISMA terminal source.

Scope:

- `F:\repos\hitech-os\apps\keystone\app\layout.tsx`
- `F:\repos\hitech-os\apps\keystone\app\dev\layout.tsx`
- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\api\scene-studio\run\route.ts`
- `F:\repos\hitech-os\apps\keystone\app\pitch\**\page.tsx`
- `F:\repos\hitech-os\apps\keystone\tsconfig.json`
- `F:\repos\hitech-os\apps\keystone\vitest.config.ts`
- `F:\repos\hitech-os\package.json`
- `F:\repos\hitech-os\tools\repo-cleanup\scene-removal\**`

Validation:

```powershell
pnpm run lockfile:check
pnpm -C apps/terminal-de-venta-system run verify:product-integrity
pnpm -C apps/terminal-de-venta-system run verify:round2
pnpm -C apps/keystone run typecheck
pnpm -C apps/keystone run build
pnpm -C apps/keystone run test
pnpm run typecheck
```

Status:

READY. Merge this branch before the broader cleanup/consolidation PRs.

PR:

`https://github.com/alanharrryy-wq/hitech-os/pull/72`

## Proposed PR Split After Baseline Is Green

### PR 1: PRISMA Round 2 Commerce Core

Purpose:

Preserve the validated Round 2 commerce productization.

Scope:

- schemas
- shared Round 2 event map
- Tablet contextual export hardening
- Tablet standalone verifier bootstrap fix
- QA readonly audit
- Round 2 smoke aggregator
- release docs

Validation:

```powershell
pnpm -C apps/terminal-de-venta-system run verify:round2
pnpm -C apps/terminal-de-venta-system run verify:product-integrity
pnpm run typecheck
```

### PR 2: PRISMA Product Integrity Gate

Purpose:

Keep workspace and release-lane determinism permanent.

Scope:

- `tools/verify_prisma_product_integrity.mjs`
- `pnpm-workspace.yaml`
- Product Integrity docs

Validation:

```powershell
pnpm -C apps/terminal-de-venta-system install --frozen-lockfile
pnpm -C apps/terminal-de-venta-system run verify:product-integrity
pnpm run lockfile:check
```

### PR 3: Control Center / Phase 5 Lane

Purpose:

Preserve and validate Control Center / Phase 5 without contaminating Tablet Core First.

Scope:

- `apps/terminal-de-venta-system/prisma-control-center/**`
- `apps/terminal-de-venta-system/quality/**`
- `apps/terminal-de-venta-system/tools/prisma-pqos-phase5-runner.mjs`

Validation:

```powershell
pnpm -C apps/terminal-de-venta-system run quality:phase5
pnpm -C apps/terminal-de-venta-system run quality:release
```

Status:

Needs dedicated validation. Do not merge into Round 2 core PR.

### PR 4: Web/EIT Off-Release Preservation

Purpose:

Preserve `products/web/app` while keeping it out of active workspace until deterministic.

Scope:

- `apps/terminal-de-venta-system/products/web/app/**`
- docs explaining off-release status

Validation:

No build validation until dependency versions are pinned. This PR should probably be draft-only or quarantined as off-release if the operator does not approve exact dependency pinning.

### PR 5: Open Branch Retirement / Quarantine Plan

Purpose:

Quarantine or supersede obsolete branch content after surviving implementations are chosen.

Scope:

- `tools/repo-cleanup/quarantine/**`
- `tools/repo-cleanup/QUARANTINE_MANIFEST.*`

Validation:

```powershell
pnpm run lockfile:check
pnpm run typecheck
```

## Explicit Non-Changes

For the broader cleanup/consolidation plan:

- Do not mix PRISMA Round 2, Control Center / Phase 5, Web/EIT, and quarantine decisions into the Scene Studio blocker-removal PR.
- Do not move files to quarantine unless a later topic PR proves isolation is insufficient.
- Do not delete branches.
- Do not update visual baselines.

## Merge Order

Planned order:

1. Merge `fix/remove-scene-studio-blocker`.
2. PRISMA Product Integrity Gate.
3. PRISMA Round 2 Commerce Core.
4. Control Center / Phase 5 lane.
5. Web/EIT off-release preservation or quarantine.
6. Cleanup/quarantine manifest PR.
