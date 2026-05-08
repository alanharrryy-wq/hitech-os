# ATLAS PC INTERACTION - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance de interacción

Este documento describe cómo interactúan las pantallas PC, navegación, API routes, servicios, sync y validaciones confirmadas dentro del ZIP. No documenta Tablet, Mobile ni Shared Core como propiedad PC.

## Modelo de interacción confirmado

PC funciona como backoffice administrativo. La interacción dominante es:

```text
Página Next / componente UI
  -> cliente o acción de pantalla
  -> API route Next
  -> servicio server-side
  -> repositorio Prisma
  -> dependencia externa o base canónica cuando aplica
```

Cuando participa sync:

```text
Evento / payload operativo
  -> API sync o ingest
  -> clasificación/validación
  -> cola, duplicados, conflictos o rejected
  -> persistencia/reconciliación
```

## Navegación

`components/layout/app-shell.tsx` y `src/composition/module-registry.ts` forman el centro de navegación de backoffice. Las rutas visibles existen como `app/**/page.tsx`; varias páginas importan `AppShell` para entrar al patrón administrativo.

### Grupos funcionales de navegación

| Grupo | Rutas confirmadas |
|---|---|
| Inicio | `/`, `/dashboard` |
| Catálogo | `/catalogo`, `/catalogo-global`, `/catalogo-global-v2`, `/catalogo-multisucursal` |
| Inventario | `/inventario`, `/stock`, `/stock-historial`, `/stock-sucursal`, `/ajustes-inventario` |
| Compras/Recepción | `/compras`, `/compras-inteligentes`, `/recepcion`, `/reabasto`, `/ordenes`, `/transferencias` |
| Auditoría | `/auditoria`, `/auditoria-operativa`, `/conteos`, `/conteos-ciclicos`, `/historial-conteos` |
| Operación | `/operacion`, `/operacion-dashboard`, `/operaciones`, `/acciones-masivas`, `/cortes-caja`, `/mermas` |
| Sync | `/sync`, `/sync-health` |
| Proveedores | `/proveedores`, `/proveedores-analytics`, `/proveedores-calidad`, `/proveedores-compras`, `/proveedores-eventos`, `/proveedores-historial`, `/proveedores-lifecycle`, `/proveedores-lista`, `/proveedores-matriz`, `/proveedores-recepcion`, `/proveedores-reconciliacion`, `/proveedores-reportes`, `/proveedores-sugerencias` |
| Admin | `/settings`, `/licencias`, `/roles-permisos`, `/usuarios-sesiones`, `/notificaciones` |
| Reportes/KPIs | `/kpis`, `/reportes-exportables`, `/vistas-globales`, `/alertas-ejecutivas` |

## Patrón page -> shell -> componentes

### Confirmado

- Las páginas son `page.tsx` en `app/**`.
- El shell principal se importa desde `@components/layout/app-shell`.
- Componentes UI se agrupan por dominio (`catalog`, `inventory`, `operations`, `suppliers`, `sync`, `license`, `ui`).
- Algunas páginas usan datasets/constructores desde `src/lib/**`.

### Pendiente

- No se puede confirmar comportamiento real de usuario sin ejecutar la app completa.
- No se puede confirmar routing efectivo en navegador sin dependencias externas.

## Interacción API

Se confirman 36 API routes. La mayoría corresponden a lectura de workspace/resumen; algunas soportan `POST` para ingest, importación, simulación o mutaciones operativas.

| Familia API | Función de interacción |
|---|---|
| `/api/dashboard/*` | Resumen ejecutivo y KPIs |
| `/api/catalog/*` | Catálogo, calidad, exportación, marcas/categorías/tags |
| `/api/inventory/*` | Snapshots, movimientos, conteos, ajustes, reorder |
| `/api/purchases/*` | Órdenes y recepciones |
| `/api/reorder/*` | Sugerencias de reabasto |
| `/api/sync/*` | Status, queue, conflicts, duplicates, rejected e ingest |
| `/api/settings/*` | Configuración, usuarios, licencias |
| `/api/suppliers/*` | Proveedores, recomendaciones, órdenes, recepción, pagos, import/export y simulación |
| `/api/backoffice/*` | Endpoints agregados de backoffice |

## Interacciones por dominio

### Catálogo

Flujo confirmado:

```text
Pantallas catálogo
  -> componentes catálogo/UI
  -> /api/catalog/* o /api/backoffice/catalog
  -> catalog.service.ts
  -> catalog.repository.ts
  -> Prisma externo/canónico
```

Responsabilidades PC:

- Administración de catálogo.
- Calidad de catálogo.
- Exportación/consulta.

No responsabilidad PC:

- Contrato global de eventos o schema canónico.

### Inventario

Flujo confirmado:

```text
Pantallas inventario/stock/conteos
  -> /api/inventory/*
  -> inventory-ledger.service.ts
  -> inventory.repository.ts
  -> modelos Prisma externos/canónicos
```

Responsabilidades PC:

- Snapshots.
- Movimientos.
- Conteos.
- Ajustes y reorder.

### Compras, recepción y reabasto

Flujo confirmado:

```text
Compras / recepción / reabasto
  -> /api/purchases/* y /api/reorder/suggestions
  -> purchase.service.ts / purchase.repository.ts
  -> motores de sugerencia y datos operativos
```

### Sync

Flujo confirmado:

```text
Sync UI / ingest payload
  -> /api/sync/status | queue | conflicts | duplicates | rejected | ingest
  -> src/server/sync/** y src/lib/sync-ingest/**
  -> validación, clasificación, persistencia o rechazo
```

El contrato de eventos/sync global se documenta como dependencia externa.

### Proveedores

Flujo confirmado:

```text
Pantallas proveedores
  -> components/suppliers + src/lib/suppliers
  -> /api/suppliers/*
  -> motores de recomendaciones, recepción, órdenes, pagos, import/export, health y simulación
```

La carpeta `src/lib/suppliers/**` contiene motores funcionales ricos: lifecycle, policy, validator, reducer, repository contract, in-memory repository, data quality, export contracts y escenarios.

### Settings/licencias

Flujo confirmado:

```text
/settings / licencias
  -> /api/settings/*
  -> settings.repository.ts
  -> src/server/licensing/**
  -> shared/licensing como dependencia externa
```

PC puede tener gates UI/operativos, pero la política/licensing core queda externa.

## Interacción con Prisma

La interacción con base de datos se canaliza por repositorios y `src/server/prisma/client.ts`. El ZIP indica que el schema local `products/pc/app/prisma/schema.prisma` es un stub/transicional y apunta a un schema canónico externo. Por eso:

- PC usa Prisma.
- PC tiene repositorios Prisma.
- El schema canónico no se declara propiedad PC.
- Migraciones/generadores canónicos quedan pendientes de repo completo.

## Estados de error y validación

Se detectan validadores en `src/server/validators/**`, además de contratos globales en `global_context/docs/contracts/**`.

| Área | Validación confirmada |
|---|---|
| Catálogo | calidad de catálogo |
| Inventario | integridad de inventario |
| Sync | clasificación de conflictos/duplicados/rejected |
| Proveedores | data quality, lifecycle validator y policy |
| Package | `tools/validate_package.py` |

## Interacciones no confirmables desde el ZIP

- Autenticación real y permisos efectivos en runtime.
- Estado de sesión en navegador.
- Resultado de mutaciones con base real.
- Disponibilidad de dependencias externas en repo completo.
- Comportamiento real de CI.

## Resumen

PC interactúa como tablero de control administrativo: páginas densas, shell común, API routes, servicios, repositorios Prisma y motores de dominio. Shared Core, contratos globales, Visual OS global y Prisma canónico son la tubería del edificio, no el departamento de PC. PC abre las llaves y mide presión, pero no se adjudica la compañía de agua.