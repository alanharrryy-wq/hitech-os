> DEPRECATED.
> Reemplazado por docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md.
> Razon: Tablet ya no se define como terminal subordinada a PC.
> Tablet es POS standalone vendible por si solo; PC es backoffice/gobierno.

# PRISMA Twin Runtime Integration

Este documento explica cómo conectar el kernel real sin reventar las apps. La intervención es intencionalmente lateral: agrega contratos y bridges sin tocar pantallas existentes. Así se avanza sin meterle bisturí con pulso de taquero en hora pico.

## Archivos instalados

- `docs/prisma/ui/qa/twin-runtime-smoke.md`
- `docs/prisma/ui/shared/contracts/twin-capability-contract.md`
- `products/pc/app/src/composition/twin-capabilities.ts`
- `products/tablet/app/src/composition/twin-capabilities.ts`
- `shared/twin-kernel/src/data/twin-capability-manifest.ts`
- `shared/twin-kernel/src/data/twin-parity-matrix.ts`
- `shared/twin-kernel/src/index.ts`
- `shared/twin-kernel/src/runtime/twin-capability-registry.ts`
- `shared/twin-kernel/src/sync/twin-capability-events.ts`
- `shared/twin-kernel/src/types/capability.ts`
- `shared/twin-kernel/src/validation/twin-capability-validator.ts`
- `tooling/scripts/validate_twin_runtime_kernel.py`

## Estrategia de integración

1. Mantener `TwinModuleManifest` intacto para no romper módulos existentes.
2. Agregar `TwinCapabilityManifest` como contrato superior de paridad.
3. Exponer bridges por app en `src/composition/twin-capabilities.ts`.
4. Usar scorecard para decidir qué pantalla recibe siguiente refactor.

### Integración: Catálogo maestro
- PC: `catalog` en `/catalog` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `observer`.
- Eventos: catalog.updated.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Señal de stock operativa
- PC: `stock` en `/stock` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `executor`.
- Eventos: stock.adjusted, stock.received.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Conteos físicos
- PC: `counts` en `/counts` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `executor`.
- Eventos: stock.adjusted, audit.completed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Órdenes de compra
- PC: `purchasing` en `/purchasing` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `observer`.
- Eventos: purchase_order.created.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Recepción de compras
- PC: `receiving` en `/receiving` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `executor`.
- Eventos: stock.received.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Reabasto inteligente
- PC: `replenishment` en `/replenishment` como `source_of_truth`.
- Tablet: `stock` en `/stock` como `executor`.
- Eventos: replenishment.requested.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Ticket de venta
- PC: `audit` en `/audit` como `observer`.
- Tablet: `sales` en `/sales` como `executor`.
- Eventos: sale.created, ticket.closed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Cobro y medios de pago
- PC: `audit` en `/audit` como `observer`.
- Tablet: `checkout` en `/checkout` como `executor`.
- Eventos: ticket.closed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Turno y caja
- PC: `audit` en `/audit` como `observer`.
- Tablet: `shift` en `/shift` como `executor`.
- Eventos: shift.opened, shift.closed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Devoluciones
- PC: `audit` en `/audit` como `observer`.
- Tablet: `returns` en `/returns` como `executor`.
- Eventos: return.created, stock.adjusted.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Salud de sincronización
- PC: `sync` en `/sync` como `source_of_truth`.
- Tablet: `sync` en `/sync` como `executor`.
- Eventos: sync.started, sync.succeeded, sync.failed, sync.conflict_detected, outbox.enqueued, outbox.dispatched.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Trazabilidad operativa
- PC: `audit` en `/audit` como `source_of_truth`.
- Tablet: `sync` en `/sync` como `executor`.
- Eventos: audit.completed, sale.created, return.created, shift.closed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: KPIs gemelos
- PC: `audit` en `/audit` como `source_of_truth`.
- Tablet: `sales` en `/sales` como `observer`.
- Eventos: sale.created, stock.adjusted, shift.closed.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.

### Integración: Contexto de cliente
- PC: `catalog` en `/catalog` como `source_of_truth`.
- Tablet: `sales` en `/sales` como `observer`.
- Eventos: catalog.updated.
- Próximo refactor sano: leer capability antes de agregar botón, acción o métrica nueva.
