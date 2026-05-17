# PRISMA Round 2 Release Lanes

Product root:

`F:\repos\hitech-os\apps\terminal-de-venta-system`

## Decision

STATUS: ACTIVE

PRISMA Round 2.1 separates the release into explicit lanes so core product hardening is not mixed with adjacent work.

## Active Release Lane: Round 2 Core

Classification: IN_SCOPE

Purpose:

- Preserve Tablet Core First.
- Keep PC as a backoffice/admin adder.
- Keep Mobile as a supervisor adder.
- Keep Shared as the common contract/event language.
- Keep Health, Charts, and Control Center as observers or diagnostics.

Included paths:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\package.json`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\pnpm-workspace.yaml`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\qa`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\release\prisma-round2`

Gate:

```powershell
pnpm run verify:product-integrity
pnpm run verify:round2
```

## Active Workspace Lane

Classification: IN_SCOPE

The active pnpm workspace contains deterministic package importers that already exist in `pnpm-lock.yaml`:

- `products/pc/app`
- `products/tablet/app`
- `products/mobile/app`
- `products/chart-lab/app`

`products/web/app` is intentionally not active in this workspace lane.

## Control Center / Phase 5

Classification: SEPARATE_LANE

Current state:

- Preserved.
- Not deleted.
- Not folded into Round 2 core.
- Existing dirty files stay visible in git status.

Reason:

Control Center and Phase 5 quality work are valuable product-adder surfaces, but they need their own validation lane. Mixing those changes into Round 2 would blur the Tablet Core First release boundary.

Policy:

- Do not use Control Center changes as evidence that Tablet works.
- Do not block Tablet standalone sales on Control Center health.
- Do not clean or rewrite Control Center files as part of Round 2 core.

## products/web/app

Classification: Off-release

Current state:

- Preserved in place.
- Not deleted.
- Not added to the active pnpm workspace.
- Not used as a Round 2 validation blocker.

Reason:

`products/web/app` is a new untracked lane with dependency versions set to `latest`. Promoting it into the active workspace would require lockfile resolution for packages that are not part of Round 2 core and would make the release less deterministic.

Promotion requirements:

1. Replace `latest` dependency ranges with exact approved versions.
2. Add a lockfile importer intentionally.
3. Add a lane-specific validation command.
4. Document whether it is public Web/EIT, Control Center adjacent, or a separate product surface.

## Optional Proposal Set

Not part of this change set:

- Promote `products/web/app` after dependency pinning.
- Create a Control Center specific integrity gate.
- Split Phase 5 quality changes into their own reviewable commit.

## Operating Contract

When a future change crosses lanes, it must say so explicitly in docs and validation evidence. Silent mixing is release drift.
