# Active Scope Removal

Repo root: `F:\repos\hitech-os`

## Removed from active Keystone runtime/navigation

- `F:\repos\hitech-os\apps\keystone\app\layout.tsx`
  - Removed the non-production header link to `/dev/scene-studio?debug=1`.
  - PRISMA impact: none.

- `F:\repos\hitech-os\apps\keystone\app\dev\layout.tsx`
  - Removed the active `DevConsoleProvider` wrapper from `/dev/**` routes.
  - PRISMA impact: none.

## Disabled active routes/API

- `F:\repos\hitech-os\apps\keystone\app\dev\scene-studio\page.tsx`
  - Replaced stale Scene Studio imports and runtime with `notFound()`.
  - PRISMA impact: none.

- `F:\repos\hitech-os\apps\keystone\app\api\scene-studio\run\route.ts`
  - Replaced the stale runner/spawn path with `410 Gone`.
  - PRISMA impact: none.

- `F:\repos\hitech-os\apps\keystone\app\pitch\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\01-double-engine\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\02-industrial-flow\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\03-hitech-os\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\04-valuation\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\05-inventory-foundation\page.tsx`
- `F:\repos\hitech-os\apps\keystone\app\pitch\06-shipments-receiving\page.tsx`
  - Replaced stale Pitch runtime imports with `notFound()`.
  - PRISMA impact: none.

## Removed from active validation

- `F:\repos\hitech-os\apps\keystone\tsconfig.json`
  - Explicitly excludes off-scope Scene Studio, Pitch, DevConsole, and related tests from Keystone TypeScript validation.

- `F:\repos\hitech-os\apps\keystone\vitest.config.ts`
  - Explicitly excludes off-scope Scene Studio, Pitch, DevConsole, and route smoke tests from Keystone Vitest runs.

- `F:\repos\hitech-os\package.json`
  - Removed `pnpm run keystone:scene:proof:ci` from root `ci`.

## Not removed

Source files under Scene Studio/Pitch remain recoverable in place. No source tree was moved to quarantine because explicit isolation unblocked typecheck/build with less risk than moving large directories.
