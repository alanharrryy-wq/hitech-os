# DeltaForge -> Glass Shell Swap Blueprint

## Documento

**Objetivo:** migrar la carcasa visual de DeltaForge a `pyside6_glass` sin tocar el motor operativo, sin crear doble verdad de estado y sin convertir `shared/integration/*` en dueño del negocio.

**Alcance de este blueprint:**
- archivos exactos a crear y a tocar
- responsabilidades por capa
- orden de ejecución
- criterios de aceptación
- riesgos de integración y reglas de no-regresión

**Decisión central:** la migración correcta es **shell swap por adapter**, no reescritura del motor ni absorción del core por el framework visual.

---

# 1. Resumen ejecutivo

DeltaForge ya trae una separación bastante útil entre:

- **motor operativo**: `application/*`, `domain/*`, `infrastructure/*`
- **frontera de lectura**: `WorkspaceFacade`
- **frontera de comandos**: `UiCommandController`
- **shell visual actual**: `ui/window/main_window.py` + `ui/widgets/*`

`pyside6_glass` ya trae lo que hace falta para convertirse en la carcasa nueva:

- `GlassPanelTemplate` para shell, paneles y slots
- `GlassWorkspaceTabs` para tabs de workspace/sesiones
- `GlassWorkspaceRuntime` para layout, visibilidad y persistencia visual

La jugada buena es:

```text
SessionManager / SessionActions / WorkspaceFacade / UiCommandController
                -> DeltaForge Glass Projection Adapter
                -> GlassPanelTemplate + GlassWorkspaceRuntime
                -> Widgets DeltaForge reutilizados o reemplazados por fases
```

La jugada que NO conviene:

```text
DeltaForge core -> shared/integration/runtime_bridge -> shell nueva -> estado híbrido
```

Eso metería un segundo cerebro y luego valió madre la claridad del sistema.

---

# 2. Principios no negociables

## 2.1 Qué no se toca

Estos módulos siguen siendo dueños del negocio y no se deben rediseñar para acomodar la UI:

- `apps/deltaforge/application/session_actions.py`
- `apps/deltaforge/application/session_manager.py`
- `apps/deltaforge/application/workspace_facade.py`
- `apps/deltaforge/application/state_machine.py`
- `apps/deltaforge/domain/*`
- `apps/deltaforge/infrastructure/*`

## 2.2 Qué sí cambia

Cambia la **shell de presentación**:

- ventana principal
- composición de paneles
- tabs visuales
- status strip
- wiring visual con runtime/layout del framework shared

## 2.3 Qué NO se permite

- widgets mutando `SessionWorkspace` directo
- `pyside6_glass` importando `SessionManager` o `SessionActions`
- `shared/integration/*` como dueño interno del app state
- estado duplicado de sesión en la shell visual
- flags `dirty/stale/busy` calculados localmente por widgets

---

# 3. Mapa del motor que debe preservarse completo

## 3.1 Owners reales

| Dato | Owner real | Lectores | Mutadores legales |
| --- | --- | --- | --- |
| `active_session_id` | `SessionManager` | facade, controller, tabs, shell | `create_session`, `activate_session`, `close_session` |
| `scope` | workspace activo dentro de `SessionManager` | facade, panes, status | `SessionActions.set_scope(...)` |
| `ops_document` | workspace activo | facade, panes | `SessionActions.set_ops_document(...)` |
| `dirty` | workspace activo | status, tabs, policies | `mark_dirty`, `clear_dirty`, `clear_dirty_and_stale` |
| `stale` | workspace activo | status, refresh, panes | `mark_stale`, watcher -> action, `clear_stale`, refresh |
| `busy` | workspace activo | command gating, status | `start_run`, `complete_run`, `fail_run`, refresh |
| `state` | workspace activo | status, tabs, shell | `start_run`, `complete_run`, refresh/state machine |
| `selection` | workspace activo | detail, plan focus, target focus | `update_selection`, `clear_selection` |
| `results` surfaces | workspace activo | bottom tabs, detail, center preview | `complete_run`, refresh |
| `event_feed` | workspace activo | results/events/status/debug | actions + event plumbing |

## 3.2 Entradas legales al motor

Toda acción de UI debe seguir entrando por `UiCommandController`:

- `create_session`
- `close_session`
- `select_session`
- `browse_root_dir`
- `validate_active`
- `plan_active`
- `apply_active`
- `rollback_active`
- `refresh_active`
- `select_op`
- `select_target`

## 3.3 Salidas legales hacia la UI

Toda lectura de UI debe seguir saliendo por `WorkspaceFacade`:

- `get_session_tabs_projection()`
- `get_active_session_id()`
- `get_command_bar_projection()`
- `get_workspace_projection()`
- `get_status_projection()`
- `snapshot()` / `active_snapshot()` para pruebas y parity checks

---

# 4. Arquitectura objetivo del shell swap

## 4.1 Forma objetivo

```text
+---------------------------------------------------------------+
| DeltaForgeGlassMainWindow                                     |
|                                                               |
|  GlassPanelTemplate                                           |
|   - hero                                                      |
|   - workspace tabs (sesiones)                                 |
|   - main slot                                                 |
|   - side slot                                                 |
|   - status slot                                               |
|   - footer/status                                             |
|                                                               |
|  GlassWorkspaceRuntime                                        |
|   - layout presets                                            |
|   - panel visibility                                          |
|   - runtime diagnostics                                       |
|                                                               |
|  DeltaForgeGlassProjectionAdapter                             |
|   - tabs mapping                                              |
|   - command bar mapping                                       |
|   - workspace panel mapping                                   |
|   - status mapping                                            |
|   - runtime context mapping                                   |
|                                                               |
|  Existing DeltaForge widgets reused by slot/panel             |
+---------------------------------------------------------------+
```

## 4.2 Regla clave

El adapter no inventa estado. Solo traduce:

- proyecciones de DeltaForge
- a tabs, panel specs, widgets y señales del shell shared

---

# 5. Blueprint de archivos exactos

## 5.1 Archivos a crear

### A. `apps/deltaforge/ui/adapters/glass_projection_adapter.py`

**Rol:** adapter maestro de proyecciones.

**Responsabilidades:**
- leer `WorkspaceFacadeBridge`
- mapear `get_session_tabs_projection()` a `GlassWorkspaceTabSpec`
- mapear `get_workspace_projection()` a payloads de paneles
- mapear `get_status_projection()` a status/footer text
- producir `GlassRuntimeContext` sin inventar negocio
- exponer helpers puros para testing

**API sugerida:**
- `build_session_tab_specs(...)`
- `build_command_bar_state(...)`
- `build_workspace_panel_payloads(...)`
- `build_status_payload(...)`
- `build_runtime_context(...)`

### B. `apps/deltaforge/ui/window/glass_main_window.py`

**Rol:** nueva ventana principal canonical.

**Responsabilidades:**
- crear `GlassPanelTemplate`
- crear `GlassWorkspaceRuntime`
- crear widgets de panel y montarlos en slots del template
- conectar señales de tabs/acciones al `ControllerBridge`
- refrescar UI desde `WorkspaceFacadeBridge`
- ser la nueva shell oficial de DeltaForge

### C. `apps/deltaforge/ui/window/glass_panel_registry.py`

**Rol:** ensamblaje de paneles para la shell nueva.

**Responsabilidades:**
- declarar panel IDs canónicos
- construir y registrar paneles visuales dentro de `main`, `side`, `status`
- evitar que `glass_main_window.py` se vuelva un changarro kilométrico

**Panel IDs recomendados:**
- `scope_ops`
- `preview`
- `detail`
- `results_stream`
- `status_summary`

### D. `apps/deltaforge/ui/window/glass_workspace_host.py`

**Rol:** widget host que organiza los widgets DeltaForge reutilizados dentro de la shell nueva.

**Responsabilidades:**
- hospedar `TargetList`, `OpsList`, `PlanDiffStack`, `DetailStack`, `BottomResultsTabs`, `CommandBar` si se decide reutilizarlo inicialmente
- exponer setters de payload limpios
- mantener el detalle de composición fuera del adapter

### E. `apps/deltaforge/tests/ui/test_glass_projection_adapter.py`

**Rol:** pruebas unitarias del mapping.

**Debe validar:**
- tabs
- badges
- state normalization
- visibility decisions
- mapping de results surfaces
- no pérdida de `dirty/stale/busy`

### F. `apps/deltaforge/tests/ui/test_glass_main_window_smoke.py`

**Rol:** smoke tests de la shell nueva.

**Debe validar:**
- la ventana construye
- template + runtime levantan
- tabs renderizan sesión activa
- refresh desde proyección no explota

---

## 5.2 Archivos a tocar

### 1. `apps/deltaforge/bootstrap/app_bootstrap.py`

**Cambio:** sustituir la ventana canónica.

**Antes:**
- importa `ui.window.main_window.DeltaForgeMainWindow`

**Después:**
- importar `ui.window.glass_main_window.DeltaForgeGlassMainWindow`
  o dejar `main_window.py` como shim hacia la nueva implementación

**Responsabilidad del cambio:**
- que `run()` siga armando exactamente el mismo motor
- solo cambia la carcasa visual

### 2. `apps/deltaforge/ui/window/main_window.py`

**Cambio recomendado:** convertirlo en shim de compatibilidad.

**Objetivo:**
- evitar romper import paths existentes
- mover la implementación real a `glass_main_window.py`

**Resultado deseado:**
- `DeltaForgeMainWindow` apunta internamente a la nueva shell

### 3. `apps/deltaforge/ui/adapters/glass_framework_adapter.py`

**Cambio:** expandirlo para que deje de ser solo configuración cosmética.

**Agregar:**
- builder del template config para shell swap
- helpers para presets/layout inicial
- opcionalmente named layouts por defecto

**No agregar:**
- lógica de negocio
- lectura directa de `SessionManager`

### 4. `apps/deltaforge/ui/window/interop.py`

**Cambio:** mantener o ampliar si hace falta un bridge más limpio.

**Objetivo:**
- seguir teniendo una capa estable entre shell y controller/facade
- no meter lógica de mapping gordo aquí; eso va en `glass_projection_adapter.py`

### 5. `apps/deltaforge/ui/widgets/session_tabs.py`

**Cambio:** probablemente dejarlo intacto en Fase 1 y marcarlo como legacy.

**Motivo:**
- la shell nueva debe usar `GlassWorkspaceTabs` del template como tabs principales de sesión
- este widget puede quedar solo para fallback o eliminarse en fase posterior

### 6. `apps/deltaforge/ui/widgets/session_workspace.py`

**Cambio:** no usarlo como shell total.

**Opciones permitidas en Fase 1:**
- reutilizar internals parciales
- o desarmar sus piezas y montarlas por panel en `glass_workspace_host.py`

**Decisión recomendada:**
- **no** seguir usándolo como workspace monolítico completo dentro de la nueva shell
- sí reutilizar sus piezas hijas (`TargetList`, `OpsList`, `PlanDiffStack`, `DetailStack`, `BottomResultsTabs`)

### 7. `apps/deltaforge/ui/widgets/command_bar.py`

**Cambio:** reutilizarlo primero, reemplazarlo después.

**Motivo:**
- ya emite bien las señales legales
- permite validar estructura antes de meterse a polish

### 8. `apps/deltaforge/ui/widgets/status_widgets.py`

**Cambio:** reaprovechar o encapsular en panel/footer del template.

**Motivo:**
- el status strip actual ya representa bien el summary
- conviene montarlo en footer/status antes de rediseñarlo

---

## 5.3 Archivos que NO se tocan en esta migración

- `apps/deltaforge/application/*`
- `apps/deltaforge/domain/*`
- `apps/deltaforge/infrastructure/*`
- `shared/pyside6_glass/integration/*`
- `shared/pyside6_glass/contracts.py`
- `shared/pyside6_glass/runtime.py`
- `shared/pyside6_glass/template.py`

Si uno de esos se empieza a mover para que “embone la UI”, es señal de que la migración se descarriló feo.

---

# 6. Responsibilities por capa

## 6.1 Core operativo DeltaForge

**Archivos:**
- `application/*`
- `domain/*`
- `infrastructure/*`

**Responsabilidad:**
- sesiones
- transiciones de estado
- dirty/stale/busy
- results surfaces
- selección
- watcher/event bus
- refresh

**Prohibición:**
- no sabe nada de tabs visuales, layout presets ni panel visibility

## 6.2 Facade / Controller boundary

**Archivos:**
- `application/workspace_facade.py`
- `application/controllers/ui_command_controller.py`
- `ui/window/interop.py`

**Responsabilidad:**
- exponer lectura estable a la UI
- recibir comandos desde la UI
- blindar widgets de la lógica de negocio

**Prohibición:**
- no decidir layout visual
- no tener conocimiento del framework shared

## 6.3 DeltaForge App Adapter

**Archivos:**
- `ui/adapters/glass_framework_adapter.py`
- `ui/adapters/glass_projection_adapter.py` **(nuevo)**

**Responsabilidad:**
- adaptar DeltaForge al framework
- registrar icon pack/config/layout defaults
- traducir projections a specs/payloads del shell

**Prohibición:**
- no mutar negocio
- no editar internals de `pyside6_glass`

## 6.4 Shell nueva

**Archivos:**
- `ui/window/glass_main_window.py` **(nuevo)**
- `ui/window/glass_panel_registry.py` **(nuevo)**
- `ui/window/glass_workspace_host.py` **(nuevo)**

**Responsabilidad:**
- montaje del template
- runtime visual
- panel registration
- tab lifecycle visual
- wiring de señales UI
- refresh desde facade

**Prohibición:**
- no calcular verdad operativa
- no guardar `dirty/stale/busy` localmente como fuente principal

## 6.5 Framework Shared

**Archivos:**
- `shared/pyside6_glass/template.py`
- `shared/pyside6_glass/runtime.py`
- `shared/pyside6_glass/icons.py`
- `shared/pyside6_glass/config.py`

**Responsabilidad:**
- primitives
- shell
- tabs
- panel slots
- layout/persistence visual
- theming

**Prohibición:**
- cero lógica DeltaForge

---

# 7. Mapa exacto de paneles objetivo

## 7.1 Tabs principales de sesión

**Widget host:** `GlassPanelTemplate.workspace_tabs`

Cada sesión debe mapearse a un `GlassWorkspaceTabSpec` con:

- `tab_id = session_id`
- `title = title`
- `state = visible | hold | attention` según estado/flags
- `badge = badge actual`
- `tooltip = root_dir o state`

### Regla sugerida de estado visual

| Estado motor | dirty | stale | state visual sugerido |
| --- | --- | --- | --- |
| idle | false | false | `visible` |
| idle | true | false | `hold` |
| idle | false | true | `attention` |
| validating / planning / applying / rolling_back | cualquier | cualquier | `active` o `visible` con badge/runtime status |
| failed | cualquier | cualquier | `attention` |

## 7.2 Paneles dentro de la shell

| Panel ID | Slot | Contenido | Fuente de verdad |
| --- | --- | --- | --- |
| `scope_ops` | `main` | `TargetList` + `OpsList` | `workspace_projection.targets` + `workspace_projection.ops` |
| `preview` | `main` | `PlanDiffStack` | `workspace_projection.grouped_preview` |
| `detail` | `side` | `DetailStack` | `workspace_projection.detail` |
| `results_stream` | `status` | `BottomResultsTabs` | `workspace_projection.results` |
| `status_summary` | `status` o footer | `StatusStrip` | `status_projection` |

## 7.3 Hero / command region

La acción rápida debe vivir arriba del cuerpo del shell y reutilizar en Fase 1 el `CommandBar` actual.

**Source of truth:** `get_command_bar_projection()`

**Objetivo:**
- conservar browse / validate / plan / apply / rollback / refresh
- mantener disablement legal
- evitar duplicar enablement dentro del template

---

# 8. Orden exacto de ejecución

## Fase 0. Preparación

### Paso 0.1
Congelar imports canónicos y decidir que `main_window.py` será shim.

### Paso 0.2
No mover nada de `application/*` ni `domain/*`.

### Entregable de fase
- lista cerrada de archivos a crear/tocar
- acuerdo explícito de no tocar core

---

## Fase 1. Adapter puro

### Paso 1.1
Crear `ui/adapters/glass_projection_adapter.py`.

### Paso 1.2
Modelar funciones puras para:
- session tabs -> tab specs
- workspace projection -> payload por panel
- status projection -> footer/status
- snapshot/status -> runtime context

### Paso 1.3
Cubrir ese adapter con pruebas unitarias.

### Criterio de salida
- el adapter convierte todas las proyecciones actuales a payloads consumibles por el shell nuevo
- no hay imports desde el adapter hacia `SessionManager` o `SessionActions`

---

## Fase 2. Shell nueva mínima viva

### Paso 2.1
Crear `ui/window/glass_main_window.py`.

### Paso 2.2
Levantar:
- `GlassPanelTemplate`
- `GlassWorkspaceRuntime`
- `WorkspaceFacadeBridge`
- `ControllerBridge`
- un refresh inicial desde facade

### Paso 2.3
Conectar tabs de sesión del template a:
- create/select/close por controller

### Criterio de salida
- la ventana abre
- renderiza al menos una sesión
- cambio de sesión refresca sin crash

---

## Fase 3. Host de paneles

### Paso 3.1
Crear `glass_panel_registry.py` y `glass_workspace_host.py`.

### Paso 3.2
Montar widgets existentes por panel:
- `TargetList`
- `OpsList`
- `PlanDiffStack`
- `DetailStack`
- `BottomResultsTabs`
- `StatusStrip`
- `CommandBar` o equivalente encapsulado

### Paso 3.3
Conectar señales de selección:
- target -> `select_target`
- op -> `select_op`

### Criterio de salida
- shell nueva ya reproduce el workspace actual por paneles
- sin usar `SessionWorkspace` como carcasa monolítica

---

## Fase 4. Runtime visual y layouts

### Paso 4.1
Usar `GlassWorkspaceRuntime` para:
- layout inicial
- side/footer/status visibility
- named layout presets

### Paso 4.2
Definir al menos dos layouts:
- `operator_default`
- `results_focus`

### Paso 4.3
Aplicar `GlassRuntimeContext` desde snapshot/status actual.

### Criterio de salida
- layout cambia sin afectar verdad operativa
- colapsar side/footer no rompe selección ni status

---

## Fase 5. Bootstrap canónico

### Paso 5.1
Cambiar `bootstrap/app_bootstrap.py` para usar la shell nueva.

### Paso 5.2
Dejar `ui/window/main_window.py` como shim a la nueva implementación.

### Criterio de salida
- `python .\apps\deltaforge\deltaforge_app.py` levanta la shell nueva
- mismo motor, nueva carcasa

---

## Fase 6. Limpieza y retiro de legacy shell

### Paso 6.1
Marcar como legacy:
- `SessionTabs`
- `SessionWorkspace` como monolito
- wiring visual viejo

### Paso 6.2
Eliminar solo cuando las pruebas de paridad estén verdes.

### Criterio de salida
- no quedan rutas activas que dependan de la shell vieja

---

# 9. Criterios de aceptación

## 9.1 Paridad funcional mínima

Debe cumplirse todo esto:

- abrir app con shell nueva
- crear sesión nueva
- seleccionar sesión
- cerrar sesión
- browse root directory
- seleccionar target
- seleccionar op
- validate
- plan
- apply
- rollback
- refresh
- ver status `dirty/stale/busy/state`
- ver results surfaces `events/validation/plan/apply/rollback`

## 9.2 Paridad de ownership

Debe seguir siendo cierto:

- solo `SessionActions` muta negocio
- solo `WorkspaceFacade` alimenta lectura rica
- la shell nueva no decide `dirty/stale/busy`
- `GlassWorkspaceRuntime` solo gobierna layout/visibilidad

## 9.3 Paridad visual estructural

Debe existir equivalencia visible entre:

| Shell actual | Shell nueva |
| --- | --- |
| session tabs | workspace tabs del template |
| command bar | hero/action region |
| target list + ops list | panel `scope_ops` |
| center preview | panel `preview` |
| detail pane | panel `detail` |
| results tabs | panel `results_stream` |
| status strip | footer/status |

## 9.4 No regresiones duras

No debe pasar ninguna de estas mamadas:

- cerrar sesión borra o desincroniza otra sesión
- cambiar layout cambia datos operativos
- colapsar side panel borra selección
- refresh de shell pisa `results`
- una acción visual cambia `dirty/stale` sin pasar por `SessionActions`

---

# 10. Test plan

## 10.1 Unit tests

### `test_glass_projection_adapter.py`
Validar:
- mapping de `get_session_tabs_projection()`
- mapping de badges/state/tooltip/current
- mapping de `workspace_projection` a payloads de panel
- mapping de status a runtime context

## 10.2 Widget smoke tests

### `test_glass_main_window_smoke.py`
Validar:
- build de ventana
- build de template
- build de runtime
- refresh inicial con una sesión creada
- actualización de tabs al cambiar sesión

## 10.3 Parity tests de acciones

Reusar fakes/mocks del controller y verificar:
- click/trigger de browse llama `browse_root_dir`
- click/trigger de validate llama `validate_active`
- click/trigger de results selection llama `select_op` o `select_target`

## 10.4 Manual smoke checklist

- lanzar app
- cambiar entre sesiones
- browse root
- correr validate/plan/apply/rollback/refresh
- mover layout, colapsar side, volver
- confirmar que los resultados siguen alineados

---

# 11. Riesgos y mitigaciones

## Riesgo 1. Doble verdad entre runtime y session core

**Síntoma:** tabs o paneles muestran estado distinto al facade.

**Mitigación:**
- la shell refresca siempre desde `WorkspaceFacadeBridge`
- runtime solo decide visibilidad/layout, no estado operativo

## Riesgo 2. Meter `shared/integration/*` como shortcut

**Síntoma:** se empieza a usar `runtime_bridge` para leer o mutar el core local.

**Mitigación:**
- prohibirlo en esta migración
- integration queda fuera de scope

## Riesgo 3. `SessionWorkspace` sobrevive como mini-shell dentro de otra shell

**Síntoma:** terminas con shell nueva afuera y shell vieja adentro. Qué hueva y qué deuda.

**Mitigación:**
- reutilizar piezas hijas, no el monolito completo

## Riesgo 4. `main_window.py` se vuelve bodega de adapters y paneles

**Mitigación:**
- separar `glass_main_window.py`, `glass_panel_registry.py`, `glass_workspace_host.py`, `glass_projection_adapter.py`

## Riesgo 5. Cambiar core por culpa de un detalle visual

**Mitigación:**
- cualquier cambio propuesto a `application/*` durante el shell swap debe presumirse incorrecto hasta demostrar lo contrario

---

# 12. Definition of done

La migración se considera bien hecha cuando:

1. DeltaForge arranca con la shell nueva.
2. El motor sigue siendo el mismo.
3. No se tocó `application/*`, `domain/*` ni `infrastructure/*` para acomodar la UI.
4. Las proyecciones actuales alimentan la shell nueva vía adapter.
5. El usuario puede operar sesiones y acciones igual que antes.
6. El runtime shared gobierna layout visual, no estado de negocio.
7. `main_window.py` queda como shim o alias limpio a la nueva implementación.

---

# 13. Secuencia final recomendada, en una sola línea

Primero **adapter**, luego **shell mínima viva**, luego **panel host**, luego **runtime/layout**, luego **bootstrap canónico**, y al final **retiro del legacy visual**.

Esa es la ruta chingona. Todo lo demás huele a retrabajo con esteroides.
