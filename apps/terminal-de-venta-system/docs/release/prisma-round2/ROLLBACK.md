# Rollback

Rollback is source-only. Do not delete unrelated local work.

Suggested rollback scope for this Round 2 productization:

```powershell
git diff -- apps/terminal-de-venta-system/prisma/schema.prisma
git diff -- apps/terminal-de-venta-system/products/tablet/app/prisma/schema.prisma
git diff -- apps/terminal-de-venta-system/products/pc/app/prisma/schema.prisma
git diff -- apps/terminal-de-venta-system/shared/contracts/prisma-round2-event-map.v1.json
git diff -- apps/terminal-de-venta-system/tools/qa/prisma_round2_readonly_audit.py
git diff -- apps/terminal-de-venta-system/tools/verify_prisma_round2_productization.mjs
```

To rollback manually, reverse only the files listed in `FINAL_REPORT.md` under "Files changed".

Generated/local artifacts are ignored and may be removed safely only by explicit path:

```powershell
Remove-Item -LiteralPath F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\.next -Recurse -Force
Remove-Item -LiteralPath F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\.next -Recurse -Force
Remove-Item -LiteralPath F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\.next -Recurse -Force
```

Do not run `git clean`, `git reset --hard`, or broad recursive deletion.

