# STRUCTURAL_CLEANUP_REPORT

## Scope
Truthful structural cleanup for:
`F:\repos\hitech-os\apps\terminal-de-venta-system`

## Before
The repository contained mixed concerns:
- canonical source mixed with packaging-oriented structure
- delivery/package artifacts living inside repo source tree
- zip artifacts and packaging history names
- generated/runtime residue intermixed with code
- duplicated shared twin contract copies

## Final Structural Classification
| Path | Classification | Final Status |
|---|---|---|
| `products\pc\app` | live product source | canonical |
| `products\tablet\app` | live product source | canonical |
| `shared\twin-kernel` | shared twin contract surface | canonical |
| `architecture\prisma-lab` | architecture incubation | isolated from runtime |
| `tooling\scripts` | tooling | reserved operational area |
| `docs` | documentation | real docs only |
| `out\tmp`, `out\archive` | local residue | non-canonical |

## Key Decisions
1. PC source is directly visible under `products\pc\app`.
2. Tablet source is directly visible under `products\tablet\app`.
3. Shared contract code is single-sourced under `shared\twin-kernel`.
4. Prisma exploratory material remains in `architecture\prisma-lab`; no runtime promotion.
5. All zip artifacts were removed from this repository tree.
6. Packaging-style structures were removed from canonical tree.
7. Generated/build residue was cleaned from source areas.

## Renamed / Removed Structural Material
- Removed packaging-oriented folder hierarchy that was not canonical source.
- Removed zip artifacts from repository.
- Removed misleading packaging names from active repository paths.
- Removed stale dependency graph artifact references; no generated graph artifact remains in canonical docs by default.

## Shared/Twin Risk Handling
- Preserved `@shared-kernel/*` contract usage.
- Preserved twin event/module contract files in `shared\twin-kernel`.
- Updated path/config references to shared contract location.
- No business logic rewrite was introduced for twin contracts.

## Validation Executed
Commands used after cleanup:
1. `pnpm install --ignore-workspace --dir products\pc\app`
2. `pnpm install --ignore-workspace --dir products\tablet\app`
3. `terminal_de_venta.cmd pc-typecheck`
4. `terminal_de_venta.cmd pc-build`
5. `terminal_de_venta.cmd tablet-typecheck`
6. `terminal_de_venta.cmd tablet-build`
7. cleanup pass removing generated runtime artifacts:
   - `products\pc\app\node_modules`, `products\pc\app\.next`, `products\pc\app\tsconfig.tsbuildinfo`
   - `products\tablet\app\node_modules`, `products\tablet\app\.next`, `products\tablet\app\tsconfig.tsbuildinfo`

## Final Assertions
- No `.zip` files remain in this repository tree.
- Canonical source is directly visible and coherent in `products/*/app`.
- Shared code is visible and centralized in `shared/twin-kernel`.
- `architecture/prisma-lab` remains exploratory and isolated.
- Repository documentation reflects the real current tree.
