# PC I03 - Auditoría de inventario

## Objetivo

Convertir `/audit` en una vista de hallazgos accionables de inventario: stock negativo, stock crítico, movimientos sin motivo, ledger derivado y conteos con variación alta.

## Alcance

- Hallazgos generados por `inventory-integrity.ts`.
- Acciones sensibles desde movimientos recientes.
- Severidad CRÍTICO/ALTO/MEDIO.
- Evidencia visible sin tocar shared-kernel ni contratos compartidos.

## Límite honesto

Los movimientos existentes no guardan actor real ni before/after nativo. I03 muestra equivalentes derivados y documenta la brecha para una fase posterior de hardening.
