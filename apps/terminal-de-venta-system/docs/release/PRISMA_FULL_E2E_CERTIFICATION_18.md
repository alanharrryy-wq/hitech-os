# PRISMA_FULL_E2E_CERTIFICATION_18_20260504_v01

## Propósito

Cerrar una ronda de certificación E2E sin agregar features nuevas. El objetivo es convertir la sensación de “ya jala” en evidencia revisable.

## Definición de listo

PRISMA FULL queda certificado sólo si existen pruebas o evidencia de:

1. **Tablet vende**: producto buscado, carrito, checkout, ticket, descuento de stock, movimiento, outbox, reporte y export.
2. **PC gobierna**: catálogo, stock, conteos, compras, recepción, reabasto, auditoría, KPIs, sync y conflictos.
3. **Mobile supervisa**: Command Center, inbox, brief diario, ledger, timeline, radar de salud, readiness y estados offline/parcial/listo.
4. **Cadena completa**: una venta o evento de Tablet queda visible para PC/Mobile, o se declara caveat explícito.

## No metas más adornos

Esta iteración no debe construir otra pantalla bonita para tranquilizar la ansiedad humana, ese deporte nacional. Debe probar lo que ya existe y separar verde, amarillo y rojo.

## Salidas esperadas

- Reporte JSON.
- Reporte Markdown.
- Checklist humano.
- Dictamen `READY`, `READY_WITH_CAVEATS` o `BLOCKED`.
