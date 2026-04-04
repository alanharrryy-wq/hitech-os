# DeltaForge · Refresh and Lifecycle Matrix 1:1

## Objetivo

Cerrar el hueco más traicionero de la migración: documentar el lifecycle exacto de acciones, transiciones, refrescos y repintado visual, para que la nueva shell glass no introduzca estados zombis, refrescos dobles ni UI que “medio funciona”.

## Base observada

Rutas inspeccionadas:

- `deltaforge/ui/window/main_window.py`
- `deltaforge/application/controllers/ui_command_controller.py`
- `deltaforge/application/session_actions.py`
- `deltaforge/application/workspace_facade.py`
- `deltaforge/application/refresh_policy.py`
- `deltaforge/application/state_machine.py`

---

## Regla madre

El lifecycle actual es de tipo:

```text
UI intent
  -> controller action
  -> session action / manager mutation
  -> projection refresh
  -> full repaint from facade
```

La nueva shell debe mantener eso como espina dorsal.

---

## 1. Refresh pipeline actual observado

## 1.1 Disparador

`DeltaForgeMainWindow._call()` invoca una acción del controller y, si el resultado **no** es `False`, llama `refresh_from_projection()`.

## 1.2 Refresh centralizado

`refresh_from_projection()` pide exactamente:

1. `get_session_tabs_projection()`
2. `get_active_session_id()`
3. `get_command_bar_projection()`
4. `get_workspace_projection()`
5. `get_status_projection()`

Y luego repinta:

- `session_tabs`
- `command_bar`
- `workspace`
- `status_strip`

## 1.3 Regla de migración

La shell nueva debe tener un **único refresh coordinator** con ese mismo principio.

---

## 2. Matriz 1:1 por acción

## 2.1 Gestión de sesiones

| Acción UI | Método controller | Mutación legal | Estado esperado | Resultados | Refresh requerido | Cambio visual esperado |
| --- | --- | --- | --- | --- | --- | --- |
| crear sesión | `create_session()` | `SessionActions.create_session(make_active=True)` | sesión nueva, activa | feed agrega `session.created` | total | aparece nueva tab y queda activa |
| cerrar sesión | `close_session(session_id)` | `SessionActions.close_session(session_id)`; si no queda activa, crea otra | sesión cerrada; puede emerger nueva activa | feed agrega `session.closed`; posible `session.created` posterior | total | desaparece tab cerrada y cambia activa |
| seleccionar sesión | `select_session(session_id)` | `SessionActions.activate_session(session_id)` | `active_session_id` cambia | sin surface nueva obligatoria | total | cambia tab activa y todo el workspace asociado |

## 2.2 Scope y selección

| Acción UI | Método controller | Mutación legal | Estado esperado | Resultados | Refresh requerido | Cambio visual esperado |
| --- | --- | --- | --- | --- | --- | --- |
| browse root | `browse_root_dir()` | `set_scope()` + `update_selection(...surface='events')` | scope nuevo en sesión activa | feed agrega `session.scope.updated` y `session.selection.changed` | total | root dir cambia, targets cambian, detail cambia |
| seleccionar target | `select_target(payload)` | `update_selection(targets=..., detail=payload, surface='events')` | selección cambia | no necesariamente cambia `results` | total | detail refleja target; results pueden seguir en events |
| seleccionar op | `select_op(payload)` | `update_selection(op=payload, detail=payload, surface='plan')` | selección cambia | no necesariamente cambia `results` | total | detail refleja op; foco lógico queda en plan |

## 2.3 Runs operativos

| Acción UI | Método controller | Lifecycle de motor | Estado durante run | Estado final éxito | Surface escrita | Refresh requerido |
| --- | --- | --- | --- | --- | --- | --- |
| validate | `validate_active()` | `start_run('VALIDATING')` -> `complete_run(surface='validation', ...)` | `VALIDATING`, `busy=True` | `IDLE` o `DIRTY_OR_STALE` según flags | `validation` | total |
| plan | `plan_active()` | `start_run('PLANNING')` -> `complete_run(surface='plan', ...)` | `PLANNING`, `busy=True` | `IDLE` o `DIRTY_OR_STALE` | `plan` | total |
| apply | `apply_active()` | `start_run('APPLYING')` -> `complete_run(surface='apply', ...)` | `APPLYING`, `busy=True` | `IDLE` o `DIRTY_OR_STALE` | `apply` | total |
| rollback | `rollback_active()` | `start_run('ROLLING_BACK')` -> `complete_run(surface='rollback', ...)` | `ROLLING_BACK`, `busy=True` | `IDLE` o `DIRTY_OR_STALE` | `rollback` | total |

## 2.4 Refresh operativo

| Acción UI | Método controller | Lifecycle de motor | Estado durante refresh | Estado final éxito | Cambio de flags | Refresh requerido |
| --- | --- | --- | --- | --- | --- | --- |
| refresh | `refresh_active()` | `begin_refresh()` -> `finish_refresh()` | `REFRESHING`, `busy=True` | `IDLE` o `DIRTY_OR_STALE` | `stale=False`, `busy=False`; `dirty` se preserva | total |

---

## 3. Lifecycle detallado por acción crítica

## 3.1 `validate_active()`

### Orden observado

1. controller exige sesión activa
2. `start_run(session_id, 'VALIDATING')`
3. `SessionActions.start_run()`:
   - valida transición legal
   - pone `state='VALIDATING'`
   - pone `busy=True`
   - agrega evento `session.run.started`
4. `complete_run(surface='validation', result=...)`
5. `SessionActions.complete_run()`:
   - escribe `results['validation']`
   - pone `busy=False`
   - deriva estado final con `derive_idle_state(dirty, stale)`
   - agrega evento `session.run.completed`
6. `_call()` dispara refresh total

### Regla para shell nueva

No intercalar refresh visual entre `start_run()` y `complete_run()` a menos que explícitamente se quiera mostrar estado intermedio en runs reales asíncronos. En el código observado, el controller actual lo hace de corrido.

---

## 3.2 `plan_active()`

### Orden observado

1. `start_run('PLANNING')`
2. `complete_run(surface='plan', result={title, summary, groups})`
3. refresh total

### Cambios visuales esperados

- tab de sesión puede reflejar `busy` en badge
- `BottomResultsTabs.plan` recibe payload nuevo
- `PlanDiffStack` puede cambiar si `grouped_preview` se deriva del plan
- enablement de `apply_active` puede pasar a `True` porque depende de `bool(results.get('plan'))`

---

## 3.3 `apply_active()`

### Orden observado

1. `start_run('APPLYING')`
2. `complete_run(surface='apply', result=...)`
3. refresh total

### Cambio clave de gating

Después de apply exitoso, `rollback_active` puede habilitarse porque depende de `bool(results.get('apply'))`.

---

## 3.4 `refresh_active()`

### Orden observado

1. `begin_refresh(session_id)`
2. `build_refresh_decision(current)`
3. si no debe refrescar, regresa sin mutación
4. si sí debe refrescar:
   - `state='REFRESHING'`
   - `busy=True`
   - evento `session.refresh.started`
5. `finish_refresh(session_id)`:
   - opcionalmente reemplaza scope/resultados si se le pasan
   - `busy=False`
   - `stale=False`
   - `state=derive_idle_state(dirty, False)`
   - evento `session.refresh.completed`
6. refresh total

### Regla para shell nueva

La shell no decide si “vale la pena” refrescar. Esa decisión sigue en `build_refresh_decision()`.

---

## 4. Estados transitorios y expectativas visuales

| Estado operativo | Qué significa | Qué debe verse en shell nueva | Qué NO debe pasar |
| --- | --- | --- | --- |
| `NEW` | sesión recién creada | tab visible, workspace limpio | inventar wizard extra sin pasar por controller |
| `IDLE` | sesión estable | acciones habilitadas según proyección | marcar `busy` local por spinner residual |
| `DIRTY_OR_STALE` | requiere atención | badge/attention visible | convertirlo en error fatal |
| `VALIDATING` | run en curso | feedback de busy; botones según `actions.*.enabled` | dejar enablement viejo congelado |
| `PLANNING` | run en curso | feedback de busy | esconder resultados previos sin motivo |
| `APPLYING` | run en curso | feedback de busy | permitir doble apply por click local |
| `ROLLING_BACK` | run en curso | feedback de busy | permitir doble rollback |
| `REFRESHING` | reconciliación | feedback de busy y refresh | dejar `stale` igual al terminar éxito |
| `FAILED` | fallo de run/refresh | badge/estado de atención | que la UI parezca “clean” |
| `CLOSED` | terminal | tab removida | mantener widgets colgados como si siguiera viva |

---

## 5. Matriz de refresh parcial vs refresh total

## 5.1 Recomendación operativa

Para la fase de shell swap seguro, usar **refresh total siempre** después de cada acción legal aceptada.

## 5.2 Motivo

Aunque podrían optimizarse refrescos parciales, el sistema actual ya está montado sobre refresh global por proyección. Cambiar eso durante la migración aumenta mucho el riesgo.

## 5.3 Futuro permitido

Solo después de tener paridad demostrada, considerar refresh parcial para:

- status-only
- tab-only
- detail-only

Pero eso va en fase posterior.

---

## 6. Riesgos específicos de lifecycle

## Riesgo A. Double refresh

### Síntoma
Una acción dispara:

- refresh desde handler visual
- refresh adicional desde un callback lateral

### Contención
Un solo `refresh_from_projection()` central en la shell nueva.

## Riesgo B. Estado intermedio fantasma

### Síntoma
UI se queda mostrando `busy` aunque `complete_run()` ya liberó la sesión.

### Contención
Nunca confiar en flags locales de widget. Siempre repintar desde `WorkspaceFacade`.

## Riesgo C. Gating visual desalineado

### Síntoma
El botón aparece habilitado, pero controller ya no lo permite o viceversa.

### Contención
La UI nueva debe leer `command_bar_projection.actions` y no inventar enablement.

## Riesgo D. Colapsar paneles altera negocio

### Síntoma
Ocultar `detail` o `results` “borra” selección o resultados.

### Contención
Panel visibility pertenece a runtime visual. `selection` y `results` siguen en session core.

---

## 7. Checklist de no-regresión por escenario

### Crear sesión
- aparece tab nueva
- queda activa
- status cambia al `session_id` nuevo
- no se hereda payload basura de otra sesión

### Seleccionar sesión
- cambian tabs, status, detail, results y command bar a la sesión correcta
- no queda detalle de sesión anterior

### Browse root
- cambia `root_dir`
- cambia `targets`
- `detail` refleja path o payload asociado

### Plan
- `results.plan` se escribe
- `grouped_preview` puede cambiar
- `apply_active` se recalcula

### Apply
- `results.apply` se escribe
- `rollback_active` se recalcula

### Refresh
- `stale` baja a `False` al éxito
- `dirty` se preserva
- estado final deriva con `derive_idle_state()`

---

## 8. Criterios de aceptación

- toda acción aceptada termina en un refresh projection-driven único
- el orden de repintado es estable y reproducible
- no hay estado visual persistido que compita con `WorkspaceFacade`
- enablement de acciones viene de proyección, no de heurística local
- `FAILED`, `DIRTY_OR_STALE` y `REFRESHING` siguen viéndose distinto en la shell nueva

---

## 9. Definition of done de este documento

El lifecycle queda bien capturado cuando cualquier interacción importante puede seguirse, paso por paso, desde la señal UI hasta la mutación legal y el repintado final, sin zonas grises ni supuestos escondidos.
