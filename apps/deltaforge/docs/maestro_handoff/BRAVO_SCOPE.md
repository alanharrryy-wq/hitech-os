# DeltaForge · Bravo Scope

## Dueño
Infraestructura, mock engine, persistence y tests de contrato/infra.

## Archivos propios
- `infrastructure/*`
- `infrastructure/engine/*`
- `infrastructure/persistence/*`
- `infrastructure/system/*`
- `tests/contracts/*`
- `tests/smoke/*` solo smoke de wiring de infra

## Prohibido
- `ui/*`
- lógica de negocio de sesión
- tocar archivos ley congelados
- decidir transiciones de estado
- tocar `application/selection_service.py` (owner Alpha)

## Entregables
- bus en memoria
- watcher desacoplado
- settings/layout stores
- mock engine contra contrato
- pruebas de adapters

## Anti-scope
- no render UI
- no theme
- no business rules
