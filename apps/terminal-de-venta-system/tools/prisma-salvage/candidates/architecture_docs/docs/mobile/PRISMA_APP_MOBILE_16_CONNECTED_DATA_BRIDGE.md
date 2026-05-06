# PRISMA App Mobile 16 - Connected Data Bridge

## Objetivo

Retirar la dependencia visible de datos demo en PRISMA App Mobile y comenzar a alimentar la pantalla desde señales reales de Tablet POS y PC Backoffice.

## Decisión

Mobile no debe inventar ventas, caja, inventario ni alertas. A partir de esta inyección:

- `/api/mobile/*` deja de importar `prisma-app-api-demo-source`.
- Mobile usa `prisma-mobile-connected-source` como adaptador server-side.
- El adaptador consulta Tablet en `PRISMA_MOBILE_TABLET_ORIGIN`.
- El adaptador consulta PC en `PRISMA_MOBILE_PC_ORIGIN`.
- Si una fuente no responde, la app devuelve estados honestos vacíos/parciales, no fixture demo maquillado.

## Variables

```text
PRISMA_MOBILE_TABLET_ORIGIN=http://127.0.0.1:3120
PRISMA_MOBILE_PC_ORIGIN=http://127.0.0.1:3130
PRISMA_MOBILE_BUSINESS_ID=biz_tablet_standalone
PRISMA_MOBILE_TERMINAL_ID=terminal_tablet_local_01
PRISMA_MOBILE_BUSINESS_NAME=PRISMA Operación
```

## Fuentes conectadas

| Mobile | Fuente inicial |
|---|---|
| Ventas de hoy | Tablet `/api/pos/sales/today` + PC `/api/backoffice/dashboard` como respaldo |
| Inventario a vigilar | Tablet `/api/pos/inventory/low-stock` |
| Alertas | Señales derivadas de stock bajo, outbox y sync |
| Reportes | Agregado móvil desde ventas, inventario, alertas y PC |
| Sucursales | Operación actual como primera rama real; multi-sucursal queda para PC/sync posterior |
| Caja | Estado honesto parcial; falta conectar corte/shift real |

## Pendiente intencional

- Autenticación.
- Multi-sucursal real.
- Corte de caja/shift durable.
- Diferencia de efectivo real.
- Gráfica por hora real desde buckets de venta; por ahora se usa top de productos como señal temporal conectada.

## Regla anti-demo

No se elimina `prisma-app-demo-data.ts` porque todavía sirve como documentación/fixtures históricos, pero ya no queda conectado a rutas vivas de `/api/mobile/*` ni al fallback del cliente.
