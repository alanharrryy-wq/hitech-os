# PRISMA Tablet Ticket Detail Not Found Fix 01

## Objetivo
Eliminar el falso estado `Ticket no encontrado` cuando Tablet sí acaba de cerrar una venta o cuando el ticket existe en la base local pero el detalle llega con un identificador incompleto.

## Cambios
- `getSaleDetail` ahora busca por `id`, `folio` o `clientRequestId`.
- Primero busca con `businessId`; si no aparece, hace fallback local por identificador.
- La pantalla de detalle acepta `businessId` desde query string.
- El cierre de venta publica `ticketEvidence` con contrato `SALE_AS_TICKET_EVIDENCE_V1`.
- El identificador canonico local es `saleId`; `folio` y `clientRequestId` son aliases documentados.
- El botón `Ver detalle` del cierre de venta usa `ticketEvidence.localDetailHref` o `saleId` y conserva `businessId`.
- El detalle expone lineas, totales, pago, negocio/tienda/terminal, turno/caja y evidencia local disponible.

## No toca
- schema Prisma
- motor POS
- cobro
- stock
- turnos
- APIs de escritura

## Contrato vigente

`Sale` es el ticket local durable de Tablet. No se agrega tabla de tickets mientras `Sale`, `SaleLine`, `CashSession`, `Terminal`, `Store` y `OutboxEvent` puedan resolver la evidencia local.

## Validación manual
1. Cerrar una venta en `http://127.0.0.1:3120/`.
2. Presionar `Ver detalle`.
3. Debe abrir el ticket, no la pantalla de `Ticket no encontrado`.
4. Entrar a `Ventas de hoy` y abrir el mismo ticket.
