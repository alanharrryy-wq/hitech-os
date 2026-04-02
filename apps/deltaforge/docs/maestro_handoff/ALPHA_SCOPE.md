# DeltaForge · Alpha Scope

## Dueño
Core de `domain/*` y `application/*` no UI.

## Ownership explícito
- `application/selection_service.py` es **owner de Alpha**.
- Ningún otro lane puede modificar `selection_service.py`.

## Archivos propios
- `domain/*`
- `domain/models/*`
- `application/state_machine.py`
- `application/stale_policy.py`
- `application/refresh_policy.py`
- `application/session_actions.py`
- `application/workspace_facade.py`
- `application/session_manager.py`
- `application/selection_service.py`
- `application/controllers/*.py` sin UI directa

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
