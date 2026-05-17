# ATLAS TABLET - Ronda 2

## Alcance

Este atlas cubre únicamente el paquete Tablet/POS observado en `ATLAS_CHAT_TABLET.zip`, con raíz de análisis `products/tablet/app`. La entrega está publicada en staging bajo `docs/atlas/_incoming/tablet/` y no representa escritura en rutas finales del proyecto.

## Reglas de frontera

- No se modifica código funcional.
- No se declara ownership sobre PC, Mobile, Backoffice ni Shared Core.
- Shared Core, Shared UI, Visual OS externo y licensing se documentan sólo como dependencias externas.
- Cualquier elemento no confirmable dentro del ZIP queda marcado como pendiente.

## Inventario confirmado

| Categoría | Evidencia confirmada |
| --- | --- |
| Pantallas Next | 28 rutas de pantalla bajo `app/**/page.tsx` |
| APIs Next | 35 rutas bajo `app/api/**/route.ts` |
| Componentes | Componentes POS, ventas, devoluciones, turno, inventario, offline, sync, visual y licencia bajo `components/**` |
| Servidor Tablet | Módulos bajo `src/server/**`, `src/modules/**`, `src/composition/**` |
| DB local | Prisma + SQLite local en `data/tablet-pos.db` y `prisma/data/tablet-pos.db` |
| QA/verificación | Scripts `verify:*`, `tablet:*`, runtime gates y validadores bajo `tools/**` y `scripts/**` |
| Assets | Manifest de assets públicos detectado; disponibilidad física de PNG queda pendiente según snapshot |

## Pantallas principales

| Ruta | Responsabilidad Tablet confirmada |
| --- | --- |
| `/` | Entrada principal de la app Tablet |
| `/pos` | Superficie POS/táctil principal |
| `/checkout` | Flujo checkout |
| `/catalog` | Catálogo local operativo |
| `/inventory`, `/existencias`, `/stock`, `/inventory/low-stock` | Inventario y stock |
| `/sales`, `/sales/today`, `/sales/today/[saleId]`, `/sales/today/[saleId]/return` | Ventas del día, ticket y retorno asociado |
| `/returns` | Devoluciones |
| `/shift` | Apertura/cierre/estado de turno |
| `/sync`, `/offline`, `/events/outbox` | Sync, outbox y auditoría offline |
| `/release-gate`, `/runtime-snapshot-preview` | Estado de release y runtime |
| `/settings/license`, `/settings/export` | Licencia y exportación |
| `/visual-os`, `/visual-os/pro`, `/visual-os/realtime`, `/visual-os/detached`, `/referencia-visual`, `/prisma-dark-pos-reference` | Superficies visuales y referencias Visual OS |

## APIs confirmadas por dominio

### Runtime y release

- `/api/health`
- `/api/tablet/runtime/snapshot`
- `/api/pos/release-gate`

### Licencia, como dependencia externa

- `/api/license/status`
- `/api/license/features`
- `/api/license/features/[key]`
- `/api/license/refresh`
- `/api/license/refresh/status`

### Catálogo y productos

- `/api/pos/catalog/products`
- `/api/pos/catalog/resolve`
- `/api/pos/catalog/import`
- `/api/pos/products/search`
- `/api/pos/products/resolve`
- `/api/pos/products/create`
- `/api/pos/products/update`
- `/api/pos/products/barcodes/validate`

### Venta, ticket, reportes y devoluciones

- `/api/pos/sales/complete`
- `/api/pos/sales/today`
- `/api/pos/sales/detail`
- `/api/pos/returns/create`
- `/api/pos/reports/operational-today`

### Turno

- `/api/pos/shift/current`
- `/api/pos/shift/open`
- `/api/pos/shift/close`

### Offline, outbox, sync y export

- `/api/pos/offline/audit`
- `/api/pos/events/outbox`
- `/api/pos/events/recent`
- `/api/pos/sync/panel`
- `/api/pos/sync/retry`
- `/api/pos/export/contextual`
- `/api/pos/export/sales-today`
- `/api/pos/export/events`
- `/api/pos/export/inventory-movements`

## Módulos funcionales de Tablet

- `src/server/local-catalog`: catálogo local importable/resoluble.
- `src/server/pos-engine`: persistencia durable de ventas, líneas, movimientos y outbox.
- `src/server/pos-api`: capa API de productos/ventas/devoluciones/turnos.
- `src/server/pos-export`: generación de CSV de ventas, eventos y movimientos.
- `src/server/pos-reports`: reporte operacional, low stock, movimientos y outbox pendiente.
- `src/server/pos-outbox`: consulta de outbox.
- `src/server/sync`: panel/retry de sync con dependencia externa Shared Kernel para contratos.
- `src/server/licensing`: adaptador Tablet hacia `shared/licensing`, no ownership local.
- `src/composition` y `src/modules`: manifiestos de módulos Tablet que consumen tipos del kernel compartido.

## Estado de verificadores

| Verificador | Estado observado | Nota |
| --- | --- | --- |
| `verify:i01-runtime` | PASS | Scaffolding runtime y scripts presentes |
| `verify:i02-catalogo` | PASS | Catálogo local operativo con fixtures |
| `verify:i03a-ticket-detail` | FAIL | Fallan llamada directa a detalle y link con `encodeURIComponent(saleId)` |
| `verify:04-offline` | FAIL | Falla render esperado de outbox en pantalla offline |
| `verify:05-release` | BLOCKED | Bloqueado por I03A y T04 |
| `tools/validate_package.py` | FAILED | Dependencias compartidas externas no incluidas en el ZIP |

## Correcciones frente a Ronda 1

- Se separa estrictamente staging de rutas finales.
- Se evita tratar Shared Core/licensing/Visual OS como propiedad Tablet.
- Se distingue código confirmado, dependencia externa y pendiente de confirmar.
- Se documentan los checks fallidos exactos de I03A y T04.
- Se mantiene JSON parseable/canónico en `atlas.tablet.json`.

## Pendientes críticos

1. Confirmar dependencias externas reales del monorepo: `shared/twin-kernel`, `shared/licensing`, `shared-ui/prisma` y `styles/config prisma-visual-os`.
2. Resolver I03A: pantalla de detalle debe cumplir el endpoint directo esperado y lista debe enlazar con `saleId` codificado.
3. Resolver T04: pantalla offline debe renderizar outbox según el verificador.
4. Confirmar disponibilidad física/licencia de packshots PNG referidos por el manifest de assets.
5. Ejecutar build/typecheck completo sólo en entorno con dependencias compartidas presentes.
