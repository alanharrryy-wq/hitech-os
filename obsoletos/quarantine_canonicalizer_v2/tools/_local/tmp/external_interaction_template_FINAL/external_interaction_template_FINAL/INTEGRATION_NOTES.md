# Shared integration pack

This pack contains only the shared files that coordinate layout, flow runner, inbox, record detail, sync center, shared UI surface behavior, and supporting utilities/tests.

## What it assumes
- Base project comes from `external_interaction_template.zip`.
- Additive UI package is applied separately before or alongside this pack.

## What this pack does
- Aligns the shared app surfaces to the additive package APIs.
- Uses the more polished `finished` layout and page structure as the baseline where safe.
- Adapts shared files to additive prop names such as `stats`, `options`, `meta`, `previewFields`, and `layout`.
- Keeps the core workflow/service files in the shared list synchronized with the new surfaces.

## Important note
The additive package provided by the parallel chat is not byte-identical to the `finished` zip. This pack was adjusted to the additive package that was actually uploaded in this conversation, especially around:
- `PageHeader`
- `StatCard`
- `FilterPills`
- `InboxRecordCard`
- runtime UI helpers

## Suggested application order
1. Start from the current project zip.
2. Apply the additive package files.
3. Apply this shared integration pack, allowing overwrite of the files included here.
4. Run your own smoke test / typecheck once the release hygiene patches land.
