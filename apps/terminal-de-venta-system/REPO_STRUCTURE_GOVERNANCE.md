# REPO_STRUCTURE_GOVERNANCE

## Purpose
Keep `terminal-de-venta-system` structurally truthful, maintainable, and twin-safe.

## Canonical Source of Truth
- `products\pc\app`
- `products\tablet\app`
- `shared\twin-kernel`

These are the only source-of-truth areas for runtime behavior and shared twin contracts.

## Shared / Twin-Sensitive Surfaces
Treat these files as contract-critical:
- `shared\twin-kernel\src\types\module.ts`
- `shared\twin-kernel\src\runtime\module-registry.ts`
- `shared\twin-kernel\src\sync\events.ts`
- product module manifests and sync event usage

Changes here require cross-product review (PC + Tablet).

## Architecture Incubation
- `architecture\prisma-lab\**`

This area is exploratory only. It must not be merged into live runtime unless direct dependency proof is documented.

## Tooling
- `tooling\scripts\**` for repo operations and maintenance scripts.
- Launcher entrypoint: `terminal_de_venta.cmd`.

## Docs
- `docs\**` for real repository docs only.
- No historical claims that contradict current folder structure.

## Out Area
- `out\tmp\**`: local temporary workspace.
- `out\archive\**`: local archive residue.

Never treat `out` as canonical source.

## Never Commit Again (anywhere in repo)
- `*.zip`
- `.next\**`
- `node_modules\**`
- `*.log`
- `.install_state*.json`
- `tsconfig.tsbuildinfo`
- local runtime db files like `prisma\dev.db`

## Naming Rules
- Use domain + role naming only (`products`, `shared`, `architecture`, `tooling`, `docs`, `out`).
- Do not introduce misleading packaging history names in source trees.
- Iteration labels (`i01..i11`) are legacy active code; new code should use domain names.

## Structural Change Protocol
1. classify folders by role
2. move to truthful destination paths
3. update imports and config aliases
4. validate PC and Tablet (typecheck/build)
5. remove generated artifacts from canonical trees
