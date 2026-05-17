# PRISMA Repository Cleanup Collision Map

Status: PRELIMINARY_READ_ONLY

Repository root:

`F:\repos\hitech-os`

## Stop Condition

Baseline monorepo typecheck failed before consolidation, so this collision map is classification only. No conflict has been resolved.

## High-Risk File Collisions Across Open PRs

| File | PR Count | Involved PRs | Risk |
| --- | ---: | --- | --- |
| `pnpm-lock.yaml` | 8 | #71, #68, #43, #32, #23, #15, #14, #4 | CRITICAL: lockfile must be one final source of truth |
| `.gitignore` | 7 | #43, #41, #39, #22, #15, #14, #4 | HIGH: preservation policy collisions |
| `apps/external_interaction_template/next-env.d.ts` | 7 | #71, #68, #43, #35, #22, #15, #14 | HIGH: generated file churn |
| `apps/terminal-de-venta-system/prisma/schema.prisma` | 4 | #71, #70, #68, #43 | CRITICAL: canonical schema collision |
| `apps/terminal-de-venta-system/products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx` | 4 | #71, #68, #66, #43 | HIGH: Mobile intelligence contract collision |
| `apps/terminal-de-venta-system/products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx` | 4 | #71, #68, #66, #43 | HIGH: Mobile adder contract collision |
| `apps/terminal-de-venta-system/products/tablet/app/tools/verify_tablet_standalone_core_closeout_02.mjs` | 4 | #71, #70, #68, #43 | HIGH: Tablet autonomy proof collision |
| `apps/terminal-de-venta-system/products/tablet/app/src/server/pos-shift/repository.prisma.ts` | 4 | #71, #70, #68, #43 | HIGH: Tablet local operation collision |
| `package.json` | 4 | #71, #68, #4, #3 | HIGH: root script/dependency collision |
| `apps/keystone/app/pitch/page.tsx` | 4 | #32, #23, #22, #4 | CRITICAL: Keystone baseline typecheck blocker area |

## Theme Collisions

### PRISMA Terminal Core

Involved branches:

- `prisma/launcher-os-quality-phase4`
- `codex/prisma-sync-observability-20260512`
- `agent-workbench-rescue-20260508_020502_utc`
- `prisma/tablet-pos-pages-shell-03`
- current working tree

Collision surfaces:

- root PRISMA schema
- Tablet standalone verifier
- Tablet shift/cash and local sale paths
- Mobile supervisor dashboard and premium navigator
- PC route/admin surfaces
- PRISMA docs and quality gates

Risk:

CRITICAL. This must be split into smaller PRs only after repository baseline typecheck is green.

### Keystone Scene Studio / Pitch

Involved branches:

- `feature/keystone-scene-studio-and-pitch`
- `feat/keystone-pitch-tabs-demo`
- `chore/stack-clean-07-example-legacy-cleanup`
- `hos/factory-launcher/Z_aggregator`
- current default branch state

Collision surfaces:

- scene-studio exports
- SceneRecord shape
- FloatingWindow props
- pitch route search params

Risk:

CRITICAL. This is the current baseline typecheck blocker.

### External Interaction Template / Web

Involved branches:

- `feature/external-interaction-template`
- `chore/stack-clean-07-example-legacy-cleanup`
- `feat/pyside6-glass-bundle-round2`
- `feat/deltaforge-integrated-bundle-wireup`
- `prisma/tablet-pos-pages-shell-03`
- current untracked `products/web/app`

Collision surfaces:

- EIT app pages
- UI components
- Prisma schema/seed
- package metadata
- generated `next-env.d.ts`

Risk:

HIGH. Must not be mixed with PRISMA Commerce cleanup.

### Code Atlas / CAPATCH

Involved branches:

- `codex/capatch-phase0-close-fix`
- `feature/code-atlas-capatch-runtime`
- `codex/code-atlas-capatch-workspace`
- `prisma/tablet-pos-pages-shell-03`

Collision surfaces:

- CAPATCH plugin registry
- CAPATCH runtime scripts
- `apps/code-atlas/code-atlas.py`

Risk:

HIGH. Needs a separate CAPATCH PR lane.

### Synapse X

Involved branches:

- `feature/synapse-x-app`
- `codex/synapse-x-engine-ui-host`
- `prisma/tablet-pos-pages-shell-03`

Collision surfaces:

- `apps/synapse-x/README.md`
- `apps/synapse-x/src/synapse_x/cli.py`

Risk:

HIGH. Separate app lane.

## Current Working Tree Collisions

Current uncommitted work under `apps/terminal-de-venta-system` includes at least five themes:

- Round 2 commerce productization
- Round 2.1 product integrity
- Control Center / Phase 5
- Web/EIT off-release lane
- Quality Phase 5 gates

These must not be committed together.

## No Resolution Yet

No file was moved, quarantined, edited, staged, committed, pushed, or merged as part of collision resolution.
