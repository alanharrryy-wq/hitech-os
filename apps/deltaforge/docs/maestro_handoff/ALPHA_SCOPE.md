# DeltaForge · Alpha Scope

## Dueño
Core de `domain/*` y `application/*` no UI.

## Ownership explícito
- `deltaforge/application/selection_service.py` es **owner de Alpha**.
- Ningún otro lane puede modificar `selection_service.py`.

## Archivos propios
- `deltaforge/domain/*`
- `deltaforge/domain/models/*`
- `deltaforge/application/state_machine.py`
- `deltaforge/application/stale_policy.py`
- `deltaforge/application/refresh_policy.py`
- `deltaforge/application/session_actions.py`
- `deltaforge/application/workspace_facade.py`
- `deltaforge/application/session_manager.py`
- `deltaforge/application/selection_service.py`
- `deltaforge/application/controllers/*.py` sin UI directa

## Prohibido
- `ui/*`
- `bootstrap/*`
- `infrastructure/*`
- tocar archivos ley congelados sin reapertura de gate

## Entregables
- verdad de sesión cerrada
- mutación legal por `session_actions`
- `WorkspaceFacade` readonly
- state machine coherente
- políticas de stale/refresh cerradas

## Anti-scope
- no temas
- no widgets
- no watchers concretos
- no engine concreto
