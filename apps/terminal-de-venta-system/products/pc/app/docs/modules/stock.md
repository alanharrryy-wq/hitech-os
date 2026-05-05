# PC I03 - Stock y ledger operativo

## Objetivo

Convertir `/stock` en una vista de inventario explicable: snapshots por ubicación, movimientos recientes y ledger derivado con before/after cuando el schema lo permite.

## Alcance

- Lee `StockSnapshot` con `Product`.
- Lee `StockMovement` con `Product`.
- Calcula estado crítico/bajo/ok por `available` y `daysCover`.
- Deriva `beforeQty` y `afterQty` desde stock actual y deltas recientes.
- Presenta actor derivado `system:canonical-db` porque el schema actual no trae actor nativo.

## Límite honesto

No se modifica schema Prisma. Por eso el ledger fuerte queda como vista derivada, no como bitácora nativa. Si se requiere auditoría legal/operativa fuerte, una iteración posterior debe persistir `beforeQty`, `afterQty`, `actorId`, `sourceType` y `sourceId` en el modelo.
