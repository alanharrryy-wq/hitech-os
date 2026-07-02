# TABREST_NON_POS Preexisting Dirty Files

Date: 2026-07-02

## Baseline Before TABREST

Initial `git status --short --branch` was clean:

```text
## main...origin/main
```

## Intentional Dirty Files Before Non-POS Polish

After the initial TABREST read/inventory work started, the user asked to correct the cobro surface back to light colors before continuing. These files are now dirty by intent and are not part of the non-POS surface polish:

```text
M  apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-cobro-surface.module.css
M  apps/terminal-de-venta-system/products/tablet/app/package.json
?? apps/terminal-de-venta-system/products/tablet/app/tools/verify_tablet_cobro_light_amounts_0207.mjs
```

## Boundary

- Do not mix these cobro files into TABREST non-POS change accounting except as a separate prerequisite correction.
- Do not revert them while continuing non-POS polish.
- Do not commit or push automatically.
