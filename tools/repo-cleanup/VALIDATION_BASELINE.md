# PRISMA Repository Cleanup Validation Baseline

Status: NO-GO

Repository root:

`F:\repos\hitech-os`

## Commands Run

| Command | CWD | Exit | Log |
| --- | --- | --- | --- |
| `pnpm run lockfile:check` | `F:\repos\hitech-os` | 0 | `F:\repos\hitech-os\tools\repo-cleanup\logs\root-lockfile-check.log` |
| `pnpm -C apps/terminal-de-venta-system run verify:product-integrity -- --out-dir tools/codex/runs/prisma-round2-product-integrity` | `F:\repos\hitech-os` | 0 | `F:\repos\hitech-os\tools\repo-cleanup\logs\prisma-product-integrity.log` |
| `pnpm -C apps/terminal-de-venta-system run verify:round2` | `F:\repos\hitech-os` | 0 | `F:\repos\hitech-os\tools\repo-cleanup\logs\prisma-round2-smoke.log` |
| `pnpm run typecheck` | `F:\repos\hitech-os` | 2 | `F:\repos\hitech-os\tools\repo-cleanup\logs\root-typecheck.log` |

## Passing Checks

Root lockfile check passed:

```text
Lockfile is up to date, resolution step is skipped
Already up to date
```

PRISMA Product Integrity passed:

```text
STATUS: GO
PASS: 8
WARN: 0
FAIL: 0
```

PRISMA Round 2 smoke passed:

```text
status: PASS
tablet pcRequiredForBasicSale: false
PC route smoke: PASS
Mobile release hardening: ok true
```

## Failing Baseline Check

Root monorepo typecheck failed:

```powershell
pnpm run typecheck
```

Exit code:

`2`

Failing workspace:

`F:\repos\hitech-os\apps\keystone`

Representative failures:

```text
apps/keystone typecheck: app/dev/scene-studio/ControlRoom.tsx(12,3): error TS2724: "./SceneStudioEditor" has no exported member named "SceneStudioEditorPanel".
apps/keystone typecheck: app/dev/scene-studio/ControlRoom.tsx(13,3): error TS2305: Module "./SceneStudioEditor" has no exported member "SceneStudioRuntimeProvider".
apps/keystone typecheck: app/dev/scene-studio/page.tsx(3,10): error TS2305: Module "../../../lib/scene-studio" has no exported member "resolveSceneStudioAccess".
apps/keystone typecheck: components/pitch/debug/pitch-route-scene-binding.tsx: multiple SceneRecord shape mismatches.
apps/keystone typecheck: tests/scene-studio-schema.test.ts: multiple missing scene-studio exports.
```

## Decision

STOP CONSOLIDATION.

No topic branches, PRs, merges, or quarantine moves may start until this baseline failure is resolved or explicitly scoped out by the operator. The failure is outside the PRISMA terminal path but inside the repository-wide build contract.

## Likely Theme

Keystone scene-studio / pitch contract drift:

- Missing exports from `apps/keystone/lib/scene-studio`
- Component prop contract drift around FloatingWindow / LayerDebugPanel
- `SceneRecord` shape drift around layers, query, layerProfile, viewport, notes, createdAt, updatedAt, motion
- Next search params type drift in pitch routes

This should be handled as a separate prerequisite PR before PRISMA cleanup PRs are merged.
