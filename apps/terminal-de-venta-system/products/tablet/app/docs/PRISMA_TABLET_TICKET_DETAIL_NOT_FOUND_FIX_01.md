# PRISMA Tablet Ticket Detail Not Found Fix 01

## Objetivo
Eliminar el falso estado `Ticket no encontrado` cuando Tablet sí acaba de cerrar una venta o cuando el ticket existe en la base local pero el detalle llega con un identificador incompleto.

## Cambios
- `getSaleDetail` ahora busca por `id`, `folio` o `clientRequestId`.
- Primero busca con `businessId`; si no aparece, hace fallback local por identificador.
- La pantalla de detalle acepta `businessId` desde query string.
- El botón `Ver detalle` del cierre de venta usa folio primero y conserva `businessId`.

## No toca
- schema Prisma
- motor POS
- cobro
- stock
- turnos
- APIs de escritura

## Validación manual
1. Cerrar una venta en `http://127.0.0.1:3120/`.
2. Presionar `Ver detalle`.
3. Debe abrir el ticket, no la pantalla de `Ticket no encontrado`.
4. Entrar a `Ventas de hoy` y abrir el mismo ticket.
