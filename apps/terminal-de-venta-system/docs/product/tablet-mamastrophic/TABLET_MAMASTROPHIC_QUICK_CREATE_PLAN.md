# TABLET MAMASTROPHIC QUICK CREATE PLAN

Date: 2026-07-03

## Rules

- No dead tiles.
- No `coming soon`.
- No `alert()`.
- No fake persistence.
- Visible active tiles must have real route, handler, dialog, or existing endpoint.
- Deferred tiles must be visually disabled and documented.

## Surface Plan

| Surface | Active tiles | Deferred/blocked tiles | Notes |
|---|---|---|---|
| Inicio | Vender, Inventario, Turno, Sincronizar, Licencia, Nuevo producto if routed to Catalog | None if `Nuevo producto` routes to Catalog | Max 6 visible. |
| POS | Buscar/escanear, ticket/cobro actions, product-create handoff only when search misses | Nuevo proveedor, stock admin | POS remains for selling, not catalog admin. |
| Inventario | Nuevo producto -> `/catalog?new=1`, Ver stock bajo -> `/inventory/low-stock`, Importar catalogo -> existing import endpoint/route if owner is exposed, Exportar inventario -> `/settings/export`, Abrir venta -> `/pos` | Ajustar stock, Nueva categoria, Nuevo proveedor until owner/form confirmed | This is the main creation hub. |
| Catalogo | Nuevo producto active through existing drawer/form; Guardar, Guardar y vender, Guardar y agregar otro already exist | Nueva categoria separate owner | Existing labels/forms will be verified. |
| Turno | Abrir turno, Cerrar turno, Actualizar, Ir a vender | Registrar entrada/salida unless model owner exists | Existing screen already has labels and save/cancel-like actions through open/close. |
| Ventas hoy | Nueva venta -> `/pos`, Buscar ticket active, Exportar ventas active, Nueva devolucion -> `/returns` | Reimprimir until selected ticket context owner confirmed | Keep ticket detail flow contextual. |
| Historial | Buscar ticket, Filtrar fecha, Aplicar rango, Exportar historial if endpoint added/available, Devolucion from selected ticket | Reimprimir until owner confirmed | Avoid route-level dynamic nav exposure. |
| Devoluciones | Nueva devolucion -> ticket list flow, Buscar ticket, Ver ventas recientes | Escanear ticket until scan owner exists here | Existing contextual return API is real. |
| Sync | Enviar pendientes, Reintentar fallidos, Actualizar estado, Exportar respaldo -> `/offline`, Ver offline -> `/offline` | None for core actions | Diagnostics stay collapsed. |
| Offline | Exportar respaldo, Ver pendientes -> `/sync`, Reintentar conexion -> refresh/audit reload, Ir a sincronizacion | None for core actions | Existing offline audit provides export links. |
| Licencia | Copiar resumen if implemented client-side, Exportar respaldo -> `/offline`, Contactar soporte link/details, Ver detalles collapsed | Importar licencia until owner is confirmed | Keep canonical governor read-only. |
| Exportaciones | Ventas, Pendientes, Movimientos, Respaldo, JSON/CSV variants via real endpoints | Turno/caja until endpoint confirmed | Each tile opens/downloads a real endpoint and reports status. |
| Configuracion | Licencia, Exportaciones, Estado operativo, Soporte | Preferencias unless real owner exists | No technical/admin reset navigation. |

## Initial No-Dead-Tile Approach

1. Create active tiles only for confirmed routes/actions.
2. Render deferred tiles as non-buttons with `aria-disabled="true"` and `data-tile-state="deferred"`.
3. Make verifiers fail if an active tile lacks `href`, `onClick`, or a documented action data attribute.
