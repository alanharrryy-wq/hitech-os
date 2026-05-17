# ATLAS PC INTERACTION - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance

Este documento describe interacciones confirmadas para PC: navegación, páginas, API routes, servicios, repositorios, sync, proveedores y licencia. No documenta Tablet, Mobile ni Shared Core como propiedad PC.

## Modelo de interacción confirmado

```text
Página Next / componente UI
  -> datos de pantalla o acción operativa
  -> API route Next cuando aplica
  -> servicio server-side
  -> repositorio Prisma
  -> Prisma client / dependencia externa canónica
```

Cuando participa sync:

```text
Evento / payload operativo
  -> /api/sync/ingest o /api/backoffice/sync/ingest
  -> sync-ingest.service.ts
  -> sync-event-contract.ts
  -> outbox / conflicts / tri-db services
```

## Navegación y superficies visibles

Las rutas confirmadas provienen de `analysis/routes_and_apis.json` y `app/**/page.tsx`.

| Grupo | Rutas confirmadas |
|---|---|
| Gobierno/guía | `/`, `/gobierno`, `/glosario`, `/referencia-visual` |
| Dashboard/operación | `/dashboard`, `/alertas-ejecutivas`, `/alertas-operativas`, `/metricas-dia`, `/scorecards-negocio`, `/tablero-kpi`, `/vistas-ejecutivas` |
| Catálogo/calidad | `/catalog`, `/catalogo-activo`, `/existencias-criticas`, `/integridad-barcodes`, `/salud-barcodes`, `/politica-precios`, `/validacion-catalogo` |
| Inventario/conteos | `/stock`, `/movements`, `/counts`, `/auditoria-inventario`, `/conteos-operativos`, `/sync-operativo`, `/outbox-operativo` |
| Compras/recepción/reabasto | `/purchasing`, `/receiving`, `/replenishment`, `/ordenes-compra`, `/recepcion-proveedor`, `/incidencias-recepcion`, `/forecast-basico`, `/senal-reabasto` |
| Proveedores | `/proveedores` |
| Sync | `/sync` |
| Settings/licencia | `/settings`, `/settings/license` |
| Reportes/detalle | `/exportables`, `/contratos-reporte`, `/detalle-registros`, `/tablas-operativas` |
| UX/filtros/estado | `/filtros-avanzados`, `/filtros-fecha`, `/estados-operativos`, `/acciones-masivas`, `/ajustes-inventario` |

## Interacción API confirmada

| Familia API | Rutas |
|---|---|
| Backoffice | `/api/backoffice/audit/recent`, `/api/backoffice/audit`, `/api/backoffice/catalog`, `/api/backoffice/counts`, `/api/backoffice/dashboard`, `/api/backoffice/movements`, `/api/backoffice/purchasing`, `/api/backoffice/receiving`, `/api/backoffice/replenishment`, `/api/backoffice/stock` |
| Backoffice sync | `/api/backoffice/sync/conflicts`, `/api/backoffice/sync/ingest`, `/api/backoffice/sync` |
| Licencia | `/api/license/features/[key]`, `/api/license/features`, `/api/license/refresh`, `/api/license/refresh/status`, `/api/license/status` |
| Proveedores | `/api/proveedores/auditoria`, `/api/proveedores/calendario`, `/api/proveedores/calidad-datos`, `/api/proveedores/compra-inteligente/crear-pedido`, `/api/proveedores/compra-inteligente`, `/api/proveedores/compra-inteligente/simular`, `/api/proveedores/cuentas-pagar/registrar-pago`, `/api/proveedores/cuentas-pagar`, `/api/proveedores/exportables`, `/api/proveedores/inventario`, `/api/proveedores/operacion`, `/api/proveedores/pedidos`, `/api/proveedores/qa/escenarios`, `/api/proveedores/recepciones/confirmar`, `/api/proveedores/recepciones`, `/api/proveedores/senales` |
| Sync / tri-db | `/api/sync/ingest`, `/api/sync/tri-db/run` |

## Interacciones por dominio

### Catálogo

```text
/catalog y pantallas de calidad catálogo
  -> components/catalog + UI cards/tables
  -> /api/backoffice/catalog
  -> catalog.service.ts
  -> catalog.repository.ts / barcode-repository.prisma.ts / product-repository.prisma.ts
  -> Prisma externo/canónico
```

### Inventario, stock, movimientos y conteos

```text
/stock /movements /counts /auditoria-inventario
  -> inventory workspace / backoffice overview
  -> /api/backoffice/stock | movements | counts | audit
  -> inventory-ledger.service.ts
  -> inventory.repository.ts / stock-repository.prisma.ts / audit-repository.prisma.ts
```

### Compras, recepción y reabasto

```text
/purchasing /receiving /replenishment
  -> procurement screen data
  -> /api/backoffice/purchasing | receiving | replenishment
  -> operation-control.service.ts y repositories de operation/purchase-order
```

### Proveedores

```text
/proveedores
  -> components/suppliers + src/lib/suppliers/**
  -> /api/proveedores/**
  -> lifecycle, data quality, smart purchase, recepciones, cuentas por pagar y señales
```

### Sync y tri-db

```text
/sync /sync-operativo /outbox-operativo
  -> /api/backoffice/sync* o /api/sync/ingest
  -> sync-ingest.service.ts / sync-release.service.ts
  -> outbox-repository.prisma.ts
  -> tri-db-command.service.ts / tri-db-status.service.ts cuando aplica
```

Tri-db se mantiene como dependencia externa/global.

### Licencia/settings

```text
/settings /settings/license
  -> /api/license/*
  -> src/server/licensing/**
  -> shared/licensing como dependencia externa
```

## Validaciones e interacción segura

| Área | Validación confirmada |
|---|---|
| Catálogo | `src/server/validators/catalog-quality.ts` |
| Inventario | `src/server/validators/inventory-integrity.ts` |
| Procurement | `src/server/validators/procurement-integrity.ts` |
| Sync events | `src/server/validators/sync-event-contract.ts` |
| Package | `tools/validate_package.py` |

## Límites

No se puede confirmar desde el ZIP:

- Autenticación real.
- Permisos efectivos por usuario.
- Estado de sesión.
- Ejecución real de mutaciones con DB completa.
- Disponibilidad de shared dependencies en runtime.
- CI o build final.

## Resumen

PC interactúa como tablero de control administrativo: rutas densas, shell común, API routes de backoffice/proveedores/licencia/sync, servicios server, repositorios Prisma y motores de proveedores/sync. Los contratos globales son la tubería del edificio, PC solo marca qué llaves abre y dónde mide presión.