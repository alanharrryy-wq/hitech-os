# Runbook post-release PC Backoffice

## Smoke recomendado

```powershell
$Pc = "F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app"
node "$Pc\tools\verify_pc_catalog_02.mjs" --root $Pc
node "$Pc\tools\verify_pc_stock_counts_audit_03.mjs" --root $Pc
node "$Pc\tools\verify_pc_operation_04.mjs" --root $Pc
node "$Pc\tools\verify_pc_sync_release_05.mjs" --root $Pc
node "$Pc\tools\verify_pc_release_complete_06.mjs" --root $Pc --log-dir "F:\descargasf"
pnpm -C $Pc exec tsc --noEmit
```

## Rutas UI esperadas

- `/catalog`
- `/stock`
- `/counts`
- `/audit`
- `/purchasing`
- `/receiving`
- `/replenishment`
- `/dashboard`
- `/sync`
