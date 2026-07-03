# TABLET MAMASTROPHIC PREEXISTING DIRTY FILES

Date: 2026-07-03
Scope: preflight before Tablet mamastrophic source patch.

## Git Status Snapshot

Command run:

```powershell
git status --short --branch
```

Observed branch:

```text
## main...origin/main
```

Preexisting modified files:

```text
M apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_BACKOUT.md
M apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_CHANGED_FILES.md
M apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_FINAL_REPORT.md
M apps/terminal-de-venta-system/docs/product/tablet-polish/TABNP1_VERIFIER_SUMMARY.json
M apps/terminal-de-venta-system/prisma-control-center/internal/config/prismo_brain100_improvements.json
M apps/terminal-de-venta-system/prisma-control-center/internal/config/prismo_visual_response_contract.json
M apps/terminal-de-venta-system/prisma-control-center/internal/py/prismo_ai_bridge.py
M apps/terminal-de-venta-system/prisma-control-center/internal/web/prismo_console.js
M apps/terminal-de-venta-system/tools/quality/verify_tabnp1_tablet_non_pos_0207.mjs
```

## Handling Rule

- These files predate this mamastrophic pass.
- Do not revert them.
- Do not overwrite them unless a later user request explicitly targets them.
- New work must stay scoped to Tablet product sources, Tablet-local components/CSS, Tablet app tools, and the `docs/product/tablet-mamastrophic` report folder.
- Control Center dirty files are out of scope and must remain untouched.
