# Core Session Integrity | Gap Checklist

## Objetivo del pase
Cerrar los gaps del core sin romper la modularidad buena ya existente.

## Gaps aprobados
- `event_feed_visible` debe ser realmente session-scoped
- `dirty` / `stale` deben reaccionar también a edición de ops
- `refresh` no debe degradar el estado de forma excesiva
- `scope` debe ser tipado
- `infrastructure` no debe arrastrar PySide donde no toca

## Checklist de auditoría del repo

### 1. Event scoping
- [ ] el bottom pane consume una proyección de la sesión activa
- [ ] no existe buffer global usado como verdad del panel
- [ ] el event bus solo transporta eventos
- [ ] la sesión decide qué eventos quedan visibles

### 2. Dirty / stale ownership
- [ ] edición de ops cambia estado por policy central
- [ ] watcher no marca `dirty` ni `stale` por decreto
- [ ] no hay flags locales de widgets decidiendo estado del core
- [ ] `dirty` y `stale` no dependen de `main_window`

### 3. Refresh integrity
- [ ] `refresh_requested` existe como intención formal
- [ ] `refresh_completed` existe como cierre formal
- [ ] refresh reconcilia en vez de resetear a ciegas
- [ ] refresh no borra información útil del lifecycle de sesión

### 4. Scope typing
- [ ] existe tipo de scope explícito
- [ ] archivo vs carpeta no se deduce en UI
- [ ] policies y acciones usan el modelo tipado
- [ ] no hay branching distribuido por strings/path sueltos

### 5. Infrastructure purity
- [ ] infrastructure no depende de widgets
- [ ] infrastructure no importa PySide salvo borde estrictamente aislado
- [ ] watcher publica señales puras
- [ ] SessionWorkspace no depende de infraestructura concreta

## Criterio de cierre
El pase queda bien cuando para cada dato crítico puedes responder sin dudar:
- quién es el owner
- quién lo puede mutar legalmente
- quién solo lo observa
