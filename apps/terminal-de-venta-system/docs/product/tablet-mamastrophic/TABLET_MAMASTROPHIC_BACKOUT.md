# TABLET MAMASTROPHIC BACKOUT

Use this only if the Tablet mamastrophic pass must be removed. Do not touch unrelated dirty files listed in the preexisting/external dirty notes.

## Backout Scope

Remove or reverse only:

- Tablet action tile component folder.
- Tablet source edits listed in `TABLET_MAMASTROPHIC_CHANGED_FILES.md`.
- Root verifiers added for this pass.
- `docs/product/tablet-mamastrophic` report files.

## Preservation Rules

- Do not revert `apps/terminal-de-venta-system/prisma-control-center/**`.
- Do not revert `apps/terminal-de-venta-system/docs/product/tablet-polish/**`.
- Do not revert `apps/terminal-de-venta-system/tools/quality/verify_tabnp1_tablet_non_pos_0207.mjs`.
- Confirm file ownership before reverting any file that has additional user edits after this report.

## Functional Backout Expectations

- Tablet returns to prior per-surface action styling.
- Home loses the new product-create tile.
- Catalog still keeps its original drawer/API behavior if only tile wiring is removed.
- Sync, offline, returns, sales, shift, and license retain their original business flows.
