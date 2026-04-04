# DeltaForge · UI Signal Wiring Matrix 1:1

## Objetivo

Documentar, con nivel quirúrgico, el cableado actual de señales UI en DeltaForge y definir su equivalente exacto en la nueva shell basada en `pyside6_glass`, sin crear rutas paralelas de mutación ni dobles refrescos.

## Base observada

Este documento está aterrizado a los archivos **observados en los zips** descomprimidos:

- `deltaforge/ui/window/main_window.py`
- `deltaforge/ui/window/interop.py`
- `deltaforge/ui/widgets/command_bar.py`
- `deltaforge/ui/widgets/session_tabs.py`
- `deltaforge/ui/widgets/session_workspace.py`
- `deltaforge/ui/widgets/target_list.py`
- `deltaforge/ui/widgets/ops_list.py`
- `deltaforge/application/controllers/ui_command_controller.py`

> Nota de ruta: el blueprint previo habla de `apps/deltaforge/...`, pero en el paquete subido las rutas observadas cuelgan de `deltaforge/...`. Para este documento se toma como referencia la estructura realmente inspeccionada en el zip.

---

## Regla madre

Toda señal de UI debe seguir este circuito:

```text
Widget/Tab/Botón
  -> señal Qt
  -> DeltaForgeMainWindow._wire_signals()
  -> ControllerBridge
  -> UiCommandController
  -> SessionActions / SessionManager
  -> refresh_from_projection()
  -> WorkspaceFacadeBridge
  -> widgets repintados
```

La shell nueva puede cambiar el cascarón visual, pero **no** la ruta legal de mutación.

---

## Mapa 1:1 de señales actuales

## 1. Señales de tabs de sesión

| Origen actual | Señal Qt | Emisor real | Receptor actual | Acción legal | Efecto de motor | Refresh posterior | Destino equivalente en shell nueva |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SessionTabs.new_button` | `createRequested` | `ui/widgets/session_tabs.py` | `DeltaForgeMainWindow._wire_signals()` | `create_session()` | crea sesión y la puede activar | sí, vía `_call()` | acción de “new tab/session” del `GlassPanelTemplate` o toolbar superior |
| `QTabBar` actual | `closeRequested(str)` | `SessionTabs._emit_close()` | `DeltaForgeMainWindow._wire_signals()` | `close_session(session_id)` | cierra sesión; si no queda activa, controller recrea una | sí | close de `GlassWorkspaceTabs` top-level |
| `QTabBar` actual | `currentChanged(str)` | `SessionTabs._emit_current()` | `DeltaForgeMainWindow._wire_signals()` | `select_session(session_id)` | cambia `active_session_id` | sí | selección de tab activa en `GlassWorkspaceTabs` |

### Reglas duras

- El `tab_id` visual nuevo debe seguir siendo el `session_id` del motor.
- La shell nueva **no** puede guardar su propia sesión activa como verdad primaria.
- El close visual no puede destruir tabs sin antes pasar por `close_session(session_id)`.

---

## 2. Señales de command bar

| Origen actual | Señal Qt | Receptor actual | Acción legal | Cambios esperados en motor | Refresh posterior | Equivalente en shell nueva |
| --- | --- | --- | --- | --- | --- | --- |
| `browse_button` | `browseRequested` | `DeltaForgeMainWindow` | `browse_root_dir()` | crea `ScopeSelection`, actualiza scope y selección | sí | acción hero/toolbar `browse_root_dir` |
| `validate_button` | `validateRequested` | `DeltaForgeMainWindow` | `validate_active()` | `start_run(VALIDATING)` + `complete_run(surface='validation')` | sí | botón primary/secondary del hero bar |
| `plan_button` | `planRequested` | `DeltaForgeMainWindow` | `plan_active()` | `start_run(PLANNING)` + `complete_run(surface='plan')` | sí | botón hero |
| `apply_button` | `applyRequested` | `DeltaForgeMainWindow` | `apply_active()` | `start_run(APPLYING)` + `complete_run(surface='apply')` | sí | botón hero |
| `rollback_button` | `rollbackRequested` | `DeltaForgeMainWindow` | `rollback_active()` | `start_run(ROLLING_BACK)` + `complete_run(surface='rollback')` | sí | botón hero |
| `refresh_button` | `refreshRequested` | `DeltaForgeMainWindow` | `refresh_active()` | `begin_refresh()` + `finish_refresh()` | sí | botón hero o status action |

### Observación crítica

`CommandBar.set_state()` hoy **solo** usa:

- `root_dir`
- `mode_label`
- `busy`

Pero la `WorkspaceFacade` ya expone `actions.*.enabled`. Eso significa que el widget actual está más simple que la proyección disponible. La shell nueva debe **elevarse al nivel de la proyección**, no quedarse en el gating minimalista actual.

---

## 3. Señales de selección dentro del workspace

| Origen actual | Señal Qt | Payload emitido | Receptor actual | Acción legal | Superficie elegida | Refresh posterior | Equivalente en shell nueva |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `TargetList` | `selectionChangedByUser` | `dict` o `None` | `SessionWorkspace.targetSelected` -> `DeltaForgeMainWindow` | `select_target(payload)` | `events` | sí | panel `scope_ops` o panel lateral de targets |
| `OpsList` | `selectionChangedByUser` | `dict` o `None` | `SessionWorkspace.opSelected` -> `DeltaForgeMainWindow` | `select_op(payload)` | `plan` | sí | panel `scope_ops` o panel lateral de ops |

### Normalización actual del payload

`UiCommandController.select_target()` normaliza targets usando, en orden:

- `path`
- `label`
- `name`
- `id`
- `str(payload)`

Eso obliga a que el adapter nuevo **preserve esas llaves** al construir items para `TargetList` o sus equivalentes.

---

## 4. Wiring actual exacto por archivo

## `ui/window/main_window.py`

### Señales conectadas hoy

```python
self.session_tabs.createRequested.connect(lambda: self._call(controller, 'create_session'))
self.session_tabs.closeRequested.connect(lambda session_id: self._call(controller, 'close_session', session_id))
self.session_tabs.currentChanged.connect(lambda session_id: self._call(controller, 'select_session', session_id))

self.command_bar.browseRequested.connect(lambda: self._call(controller, 'browse_root_dir'))
self.command_bar.validateRequested.connect(lambda: self._call(controller, 'validate_active'))
self.command_bar.planRequested.connect(lambda: self._call(controller, 'plan_active'))
self.command_bar.applyRequested.connect(lambda: self._call(controller, 'apply_active'))
self.command_bar.rollbackRequested.connect(lambda: self._call(controller, 'rollback_active'))
self.command_bar.refreshRequested.connect(lambda: self._call(controller, 'refresh_active'))

self.workspace.opSelected.connect(lambda payload: self._call(controller, 'select_op', payload))
self.workspace.targetSelected.connect(lambda payload: self._call(controller, 'select_target', payload))
```

### Comportamiento importante de `_call()`

- invoca el callback del controller
- si el resultado **no** es `False`, dispara `refresh_from_projection()`
- si el callback no existe, no hace nada

### Implicación para la nueva shell

La nueva shell debe conservar esta semántica:

- acción válida -> refresh
- acción rechazada -> no refresh innecesario

---

## 5. Contrato 1:1 recomendado para la shell nueva

## 5.1 Capa de eventos

| Capa | Responsabilidad | Prohibido |
| --- | --- | --- |
| `GlassWorkspaceTabs` top-level | emitir intención visual de crear/cerrar/seleccionar sesión | mutar sesiones por su cuenta |
| Hero/toolbar actions | emitir intención de comando | calcular negocio |
| Paneles de scope/ops | emitir selección del usuario | cambiar `selection` directo en workspace |
| `ControllerBridge` | traducir intención visual a acción legal | guardar estado visual como verdad |
| `UiCommandController` | mutar negocio legalmente | conocer detalles del layout glass |

## 5.2 API mínima de wiring a conservar

La nueva `glass_main_window.py` debe mantener, al menos, este contrato de handlers:

- `on_create_session_requested()` -> `controller.create_session()`
- `on_close_session_requested(session_id)` -> `controller.close_session(session_id)`
- `on_session_changed(session_id)` -> `controller.select_session(session_id)`
- `on_browse_requested()` -> `controller.browse_root_dir()`
- `on_validate_requested()` -> `controller.validate_active()`
- `on_plan_requested()` -> `controller.plan_active()`
- `on_apply_requested()` -> `controller.apply_active()`
- `on_rollback_requested()` -> `controller.rollback_active()`
- `on_refresh_requested()` -> `controller.refresh_active()`
- `on_target_selected(payload)` -> `controller.select_target(payload)`
- `on_op_selected(payload)` -> `controller.select_op(payload)`

---

## 6. Orden de refresh recomendado

Para cada señal aceptada:

1. UI emite intención.
2. Controller muta vía `UiCommandController`.
3. Se invoca un refresh centralizado.
4. Se vuelven a pedir estas proyecciones, en este orden:
   1. `get_session_tabs_projection()`
   2. `get_active_session_id()`
   3. `get_command_bar_projection()`
   4. `get_workspace_projection()`
   5. `get_status_projection()`
5. Se repinta la shell.

> El refresh debe seguir siendo **projection-driven**. Nada de parches visuales locales como “ya sé qué cambió, nomás actualizo una esquina”. Eso es caldo para desalineación.

---

## 7. Gaps detectados antes del shell swap

## Gap A. `CommandBar` actual ignora `actions.*.enabled`

### Riesgo
La shell nueva podría replicar un gating incompleto y perder paridad con el motor.

### Acción
El adapter debe leer `command_bar_projection.actions` y gobernar enablement fino por acción.

## Gap B. No existe matriz escrita de doble refresh

### Riesgo
Al migrar a tabs/paneles glass, puede aparecer:

- refresh por señal visual
- refresh por callback interno adicional

### Acción
La shell nueva debe tener **un único punto** de refresh post-acción.

## Gap C. La selección actual depende de payloads con llaves blandas

### Riesgo
Si el adapter renombra `path`/`label`/`name`, `select_target()` puede normalizar mal.

### Acción
Mantener payloads ricos, nunca reducirlos a texto plano si se necesita round-trip.

---

## 8. Criterios de aceptación

- crear sesión desde tabs nuevas llama una sola vez a `create_session()`
- cerrar sesión pasa siempre `session_id` correcto
- cambiar de tab actualiza `active_session_id` y repinta todo
- selección de target termina en `select_target(payload)` con payload intacto
- selección de op termina en `select_op(payload)` con payload intacto
- browse/validate/plan/apply/rollback/refresh siguen entrando por `UiCommandController`
- no existe ninguna señal nueva que mute `SessionWorkspace` directo

---

## 9. Definition of done de este documento

Este wiring matrix está “cerrado” cuando exista un adapter/shell nueva donde cada interacción visual tenga una ruta 1:1 verificable hacia `UiCommandController`, y cada acción aceptada desemboque en un refresh projection-driven centralizado.
