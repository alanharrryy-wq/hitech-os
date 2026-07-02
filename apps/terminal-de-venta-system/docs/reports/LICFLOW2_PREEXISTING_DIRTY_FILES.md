# LICFLOW2 Preexisting Dirty Files

Generated: 2026-07-02

Scope: `F:\repos\hitech-os` with LICFLOW2 work rooted at `apps/terminal-de-venta-system`.

## Git Status Before LICFLOW2 Patch

The live worktree was checked before functional LICFLOW2 edits. The following files were already dirty and are not treated as LICFLOW2-owned changes:

```text
 M apps/terminal-de-venta-system/products/pc/app/src/composition/navigation.ts
 M apps/terminal-de-venta-system/products/tablet/app/src/composition/navigation.ts
?? apps/terminal-de-venta-system/docs/product/surface-cleanup/PRISMA_RUNTIME_NAVIGATION_WIRING_0207.md
?? apps/terminal-de-venta-system/tools/quality/verify_surface_runtime_navigation_wiring_0207.mjs
```

## Handling Rule

- Do not restore, clean, delete, or stage these files as part of LICFLOW2.
- Do not use these files as evidence for LICFLOW2 unless a live repo read proves a direct activation-flow dependency.
- If later verifiers report these paths, classify them as preexisting unrelated work unless LICFLOW2 explicitly edits them after this report.

## LICFLOW2-Owned Pre-Patch Files

These inventory files are intentionally created before functional patching:

- `docs/reports/LICFLOW2_PREEXISTING_DIRTY_FILES.md`
- `docs/reports/LICFLOW2_EXISTING_INVENTORY.md`

## Additional Non-LICFLOW Dirty Files Seen During Work

Later status checks showed more dirty/untracked files outside LICFLOW2 ownership. These are still treated as unrelated and must not be reverted or mixed into LICFLOW2 claims:

```text
 M apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx
 M apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/tablet-nav.ts
?? apps/terminal-de-venta-system/docs/product/surface-cleanup/PRISMA_TABLET_SHELL_PRODUCT_NAVIGATION_WIRING_0207.md
?? apps/terminal-de-venta-system/tools/quality/verify_tablet_shell_product_navigation_wiring_0207.mjs
```
