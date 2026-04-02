# DeltaForge · Charlie Scope

## Dueño
UI, theme, primitives, panes/widgets, window y bootstrap final.

## Archivos propios
- `ui/*`
- `bootstrap/*`
- `tests/smoke/*`

## Prohibido
- `domain/*` de negocio
- `application/*` core
- `infrastructure/*` interno
- mutar `SessionWorkspace` directo
- tocar archivos ley congelados
- tocar `application/selection_service.py` (owner Alpha)

## Entregables
- theme oficial
- primitives canónicas
- panes/widgets session-scoped
- `main_window.py` canónico
- wiring con `app_bootstrap.py`

## Anti-scope
- no engine real
- no lógica de transición de estado
- no stores/adapters concretos dentro de widgets
