# Release note - PC I03 Inventario

## Entrega

`install_pc_i03_inventario.py` genera localmente `pc_i03_inventario.zip` e instala stock, conteos y auditoría dentro de `products/pc/app/**`.

## Cambio funcional

```text
/stock
/counts
/audit
  -> InventoryWorkspaceView
  -> getInventoryWorkspace
  -> InventoryRepository
  -> Prisma StockSnapshot + StockMovement + AuditCount
  -> inventory-integrity validator
```

## Pruebas mínimas

- Manifest y checksums.
- Dry-run interno.
- Backup antes de sobrescribir.
- Verify de archivos instalados.
- `node tools/verify_pc_stock_counts_audit_03.mjs --root <pc_app>`.
- DB smoke con SQLite si existe `canonical.db`.
- HTTP smoke opcional de `/stock`, `/counts`, `/audit` si PC está levantada en puerto 3130.
- `pnpm exec tsc --noEmit` si `pnpm` y `node_modules` están disponibles.

## Estado esperado

`READY` si todo instala, verifica y pasan pruebas funcionales disponibles.

`READY_WITH_CAVEATS` si DB/HTTP/typecheck quedan bloqueados por entorno pero install/verify/verifier pasan.

`BLOCKED` si falla carril, manifest, checksums, apply, verify o verifier crítico.
