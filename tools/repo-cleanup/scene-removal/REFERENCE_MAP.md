# Scene Studio / Pitch Active Reference Map

Repo root: `F:\repos\hitech-os`

## Why root typecheck reaches Scene Studio / Pitch

Root `F:\repos\hitech-os\package.json` defines:

- `typecheck`: `pnpm -r --if-present typecheck`

Workspace `F:\repos\hitech-os\pnpm-workspace.yaml` includes:

- `apps/*`
- `services/*`
- `packages/*`
- `tools/*`

Keystone `F:\repos\hitech-os\apps\keystone\package.json` defines:

- `typecheck`: `tsc --noEmit`

Keystone `F:\repos\hitech-os\apps\keystone\tsconfig.json` includes every `**/*.ts` and `**/*.tsx`, so stale Scene Studio/Pitch files are typechecked even when they are not relevant to PRISMA.

## Current blocker files from baseline typecheck

Observed in `F:\repos\hitech-os\tools\repo-cleanup\logs\root-typecheck.log`:

- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\ControlRoom.tsx`
- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\ControlRoomToolbarWindow.tsx`
- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\SceneGraphPanel.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\01-double-engine\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\02-industrial-flow\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\03-hitech-os\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\04-valuation\page.tsx`
- `F:\repos\hitech-os\apps\keystone\components\dev-console\console-core\console-core-diagnostics.ts`
- `F:\repos\hitech-os\apps\keystone\components\dev-console\console-core\console-core-shell.tsx`
- `F:\repos\hitech-os\apps\keystone\components\dev-console\DevConsoleContext.tsx`
- `F:\repos\hitech-os\apps\keystone\components\pitch\debug\pitch-dev-console-stability-helpers.tsx`
- `F:\repos\hitech-os\apps\keystone\components\pitch\debug\pitch-route-scene-binding.tsx`
- `F:\repos\hitech-os\apps\keystone\components\pitch\debug\pitch-scene-runtime-bridge.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\scene-studio-diagnostics.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\scene-studio-editor.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\scene-studio-list.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\scene-studio-page.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\scene-studio-preview.tsx`
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\use-scene-studio-state.ts`
- `F:\repos\hitech-os\apps\keystone\tests\scene-studio-access.test.ts`
- `F:\repos\hitech-os\apps\keystone\tests\scene-studio-diagnostics.test.ts`
- `F:\repos\hitech-os\apps\keystone\tests\scene-studio-schema.test.ts`
- `F:\repos\hitech-os\apps\keystone\tests\scene-studio-store.test.ts`

## Active route and validation references

Scene Studio/Pitch currently appears in these active Keystone areas:

- `F:\repos\hitech-os\apps\keystone\app\layout.tsx` links to `/dev/scene-studio?debug=1` in non-production.
- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\page.tsx` exposes a Scene Studio route.
- `F:\repos\hitech-os\apps\keystone\app\api\scene-studio\run\route.ts` exposes a Scene Studio runner API.
- `F:\repos\hitech-os\apps\keystone\app\pitch\**\page.tsx` exposes Pitch routes.
- `F:\repos\hitech-os\apps\keystone\components\scene-studio\**` contains stale Scene Studio UI.
- `F:\repos\hitech-os\apps\keystone\components\pitch\debug\**` and top-level Pitch debug helpers import Scene Studio runtime shapes.
- `F:\repos\hitech-os\apps\keystone\components\dev-console\**` imports Scene Studio and Pitch debug surfaces.
- `F:\repos\hitech-os\apps\keystone\tests\*scene-studio*` and `F:\repos\hitech-os\apps\keystone\tests\*pitch*` validate off-scope Scene Studio/Pitch behavior.
- Root `F:\repos\hitech-os\package.json` includes Scene Studio aliases and a root `ci` suffix that invokes `keystone:scene:proof:ci`.

## PRISMA reference check

Search under `F:\repos\hitech-os\apps\terminal-de-venta-system` found only documentary mentions of the word `pitch`:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\design\PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E.md`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-salvage\candidates\architecture_docs\docs\design\PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E.md`

No Tablet, PC, Mobile, schema, runtime, or validation path under PRISMA imports Keystone Scene Studio/Pitch.
