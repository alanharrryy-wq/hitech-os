# PRISMA Tablet 03L - Turno, caja y corte operativo

Instala un flujo completo para abrir turno, registrar caja inicial, bloquear venta sin turno, calcular ventas del turno, capturar conteo fisico y cerrar con diferencia visible.

## APIs
- GET /api/pos/shift/current
- POST /api/pos/shift/open
- POST /api/pos/shift/close

## Regla de negocio
Una venta cerrada debe quedar asociada a un turno abierto. Sin turno abierto, `POST /api/pos/sales/complete` responde `SHIFT_NOT_OPEN`.

## Calculo
Efectivo esperado = caja inicial + ventas del turno + movimientos operativos manuales.
Diferencia = conteo fisico - efectivo esperado.

## Limites
No cambia Prisma schema, no toca PC y no toca shared-kernel.
