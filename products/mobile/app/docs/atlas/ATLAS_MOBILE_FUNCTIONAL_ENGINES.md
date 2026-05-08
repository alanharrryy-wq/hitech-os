# ATLAS MOBILE FUNCTIONAL ENGINES

## 1. Propósito

Este documento mapea los motores funcionales Mobile confirmados desde el ZIP `ATLAS_CHAT_MOBILE.zip`. No declara propiedad sobre Shared Core, Tablet, PC ni servicios externos. Cuando un motor depende de esas piezas, se documenta como dependencia externa.

## 2. Raíz funcional confirmada

Motores Mobile bajo:

`src/lib/prisma-app`

Data plane Mobile bajo:

`src/lib/prisma-app/mobile-data-plane`

## 3. Contratos API

### Responsabilidad

Definir o normalizar la forma de los datos que UI y APIs usan para Mobile.

### Revisión cuando cambie

- route handler correspondiente bajo `app/api/mobile/*/route.ts`
- componente consumer bajo `src/components/prisma-app/*`
- fixtures/corpora/verifiers si existen
- formatters asociados

### Verificación

- typecheck
- build
- verifier específico del dominio si existe

### Rollback

Revertir contrato y consumers juntos. No dejar UI esperando una forma y API entregando otra: eso es servir tacos sin tortilla y culpar al cliente.

## 4. Snapshot/cache engine

### Intención

Permitir que Mobile presente estado operativo incluso con fuentes degradadas o cacheadas.

### Archivos a revisar

- utilities de snapshot/cache bajo `src/lib/prisma-app`
- `/api/mobile/snapshot`
- componentes que muestren stale/offline/degraded

### Dependencias externas

- fuentes Tablet/PC configuradas por origen
- política de stale/retry/timeouts

### Verificación

- API snapshot smoke
- estados stale/degraded
- runtime-error-guard si existe

## 5. Mobile data plane

### Raíz

`src/lib/prisma-app/mobile-data-plane`

### Intención

Orquestar datos desde fuentes externas hacia Mobile sin que la UI tenga que saber si vienen de Tablet, PC o cache.

### Variables observadas

- `PRISMA_MOBILE_TABLET_ORIGIN`
- `PRISMA_MOBILE_PC_ORIGIN`
- `PRISMA_MOBILE_SOURCE_TIMEOUT_MS`
- `PRISMA_MOBILE_RETRY_COUNT`
- `PRISMA_MOBILE_STALE_AFTER_MS`
- `PRISMA_MOBILE_LOW_STOCK_THRESHOLD`
- `PRISMA_MOBILE_OVERSTOCK_THRESHOLD`

### Defaults observados

- Tablet: `http://127.0.0.1:3120`
- PC: `http://127.0.0.1:3130`
- Mobile: `http://127.0.0.1:3140`

### Dependencias externas

Tablet y PC son fuentes externas. No documentar sus internals como propiedad Mobile.

## 6. Summary engine

### API asociada

`/api/mobile/summary`

### Intención

Resumen de alto nivel para dashboard.

### Consumers probables

- `PrismaMobileDashboard.tsx`
- superficies resumen si existen

### Verificación

- response shape estable
- empty/error/stale states

## 7. Sales today engine

### API asociada

`/api/mobile/sales/today`

### Intención

Ventas del día para lectura rápida.

### Revisión

- formato de moneda
- zona horaria
- corte diario
- dependencia de Tablet/PC si aplica

### Pendiente

Confirmar fuente definitiva del dato en repo completo.

## 8. Cash current engine

### API asociada

`/api/mobile/cash/current`

### Intención

Estado actual de caja.

### Revisión

- fuente externa
- moneda
- branch/sucursal
- estado stale

## 9. Inventory watchlist engine

### API asociada

`/api/mobile/inventory/watchlist`

### Intención

Mostrar productos o categorías que requieren atención por bajo stock, sobrestock u otra condición.

### Variables relacionadas

- `PRISMA_MOBILE_LOW_STOCK_THRESHOLD`
- `PRISMA_MOBILE_OVERSTOCK_THRESHOLD`

### Cuidado

No hardcodear thresholds visuales sin revisar engine/variables.

## 10. Alerts engine

### API asociada

`/api/mobile/alerts`

### Intención

Mostrar alertas operativas.

### Revisión

- severidad
- timestamp
- source
- deduplicación
- empty state

## 11. Reports daily engine

### API asociada

`/api/mobile/reports/daily`

### Intención

Reporte diario para supervisión.

### Revisión

- rango temporal
- zona horaria
- formato de totales
- relación con Daily Brief

## 12. Branches engine

### API asociada

`/api/mobile/branches`

### Intención

Listar o contextualizar sucursales/branches para Mobile.

### Pendiente

Confirmar si Mobile permite cambio de branch o solo lectura.

## 13. Health engine

### API asociada

`/api/mobile/health`

### Intención

Estado de salud general o disponibilidad de fuentes.

### Revisión

- status codes
- source states
- degraded/offline semantics

## 14. Command Center engine

### API asociada

`/api/mobile/command-center`

### UI asociada

`PrismaMobileCommandCenter.tsx`

### Intención

Construir señales de mando para decisiones rápidas.

### Verificación

- verifier de command center si está disponible
- schema/typecheck
- render manual

## 15. Action Inbox engine

### API asociada

`/api/mobile/action-inbox`

### UI asociada

`PrismaMobileActionInbox.tsx`

### Intención

Generar o entregar acciones pendientes.

### Verificación

- verifier de action inbox si está disponible
- estados vacíos y priorización

## 16. Daily Brief engine

### API asociada

`/api/mobile/daily-brief`

### UI asociada

`PrismaMobileDailyBrief.tsx`

### Intención

Resumen ejecutivo diario.

### Verificación

- verifier daily brief si existe
- revisión manual de densidad y datos

## 17. Decision Ledger engine

### API asociada

`/api/mobile/decision-ledger`

### UI asociada

`PrismaMobileDecisionLedger.tsx`

### Intención

Bitácora de decisiones o eventos decisionales.

### Verificación

- verifier decision ledger si existe
- orden temporal

## 18. Pulse Timeline engine

### API asociada

`/api/mobile/pulse-timeline`

### UI asociada

`PrismaMobilePulseTimeline.tsx`

### Intención

Línea de tiempo del pulso operativo.

### Verificación

- verifier pulse timeline si existe
- orden y agrupación

## 19. Health Radar engine

### API asociada

`/api/mobile/health-radar`

### UI asociada

`PrismaMobileHealthRadar.tsx`

### Intención

Radar de salud operativa.

### Verificación

- verifier health radar si existe
- severidad y origen de señal

## 20. Formatters

### Intención

Mantener moneda, fechas, números y etiquetas consistentes.

### Cuidado

Cambios de formatter pueden alterar múltiples superficies. Revisar todo dashboard y módulos premium.

## 21. Rollback funcional estándar

1. Revertir engine.
2. Revertir route handler asociado.
3. Revertir componente consumer si cambió shape.
4. Revertir tests/verifiers si se actualizaron.
5. No tocar Tablet/PC/Shared Core salvo cambio coordinado fuera de este atlas.

