# DeltaForge · Projection Payload Mapping 1:1

## Objetivo

Aterrizar, con tabla de campo por campo, cómo salen hoy los payloads desde `WorkspaceFacade` y dónde deben consumirse en la nueva shell glass, sin perder semántica, sin rebautizar llaves críticas y sin meter transformación opaca en widgets.

## Base observada

Rutas inspeccionadas en los paquetes descomprimidos:

- `deltaforge/application/workspace_facade.py`
- `deltaforge/ui/window/main_window.py`
- `deltaforge/ui/widgets/session_tabs.py`
- `deltaforge/ui/widgets/command_bar.py`
- `deltaforge/ui/widgets/session_workspace.py`
- `deltaforge/ui/widgets/status_widgets.py`
- `deltaforge/ui/widgets/bottom_results_tabs.py`
- `deltaforge/ui/widgets/target_list.py`
- `deltaforge/ui/widgets/ops_list.py`
- `deltaforge/ui/widgets/detail_stack.py`
- `deltaforge/ui/widgets/plan_diff_stack.py`

---

## Regla madre

El adapter nuevo debe traducir **proyecciones** a **specs/panel payloads**.

No debe:

- leer `SessionManager` directo
- inferir negocio fuera de `WorkspaceFacade`
- cambiar nombres de llaves que ya son parte del contrato práctico actual

---

## 1. Mapa general de proyecciones

| Proyección fuente | Método actual | Consumidor actual | Consumidor nuevo | Tipo de adaptación |
| --- | --- | --- | --- | --- |
| Session tabs | `get_session_tabs_projection()` | `SessionTabs.set_tabs()` | `GlassWorkspaceTabs.add_workspace_tab()` | proyección -> `GlassWorkspaceTabSpec` |
| Active session | `get_active_session_id()` | `SessionTabs.set_tabs(...active_session_id=...)` | `GlassWorkspaceTabs.set_active_tab()` | id -> selección de tab |
| Command bar | `get_command_bar_projection()` | `CommandBar.set_state()` | hero/toolbar/quick actions | dict -> action model |
| Workspace | `get_workspace_projection()` | `SessionWorkspace.set_projection()` | panel registry / workspace host | dict -> panel payloads |
| Status | `get_status_projection()` | `StatusStrip.set_summary()` | footer/status panel | dict -> status summary |

---

## 2. Session tabs projection -> Glass workspace tabs

## 2.1 Payload fuente observado

Cada elemento de `get_session_tabs_projection()` contiene:

- `id`
- `session_id`
- `title`
- `name`
- `badge`
- `state`
- `dirty`
- `stale`
- `tooltip`
- `current`
- `closable`

## 2.2 Consumo actual

`SessionTabs.set_tabs()` usa hoy:

- `session_id` o `id`
- `title` o `name`
- `state`
- `dirty`
- `stale`

`badge`, `tooltip`, `current`, `closable` existen en la proyección pero el widget actual casi no los explota.

## 2.3 Mapeo 1:1 recomendado

| Campo fuente | Obligatorio | Uso actual | Uso nuevo recomendado | Regla |
| --- | --- | --- | --- | --- |
| `session_id` | sí | id interno del tab | `GlassWorkspaceTabSpec.tab_id` | nunca inventar otro id |
| `title` | sí | texto visible | `GlassWorkspaceTabSpec.title` | preferir `title` sobre `name` |
| `badge` | no | casi sin uso | `GlassWorkspaceTabSpec.badge` | conservar `busy/dirty/stale` |
| `state` | sí | texto en tab actual | estado visual normalizado | traducir `IDLE`, `DIRTY_OR_STALE`, etc. a estado visual sin volverlo dueño del negocio |
| `tooltip` | no | no explotado del todo | `GlassWorkspaceTabSpec.tooltip` | pasar root dir o estado |
| `current` | sí | define activa | `set_active_tab(session_id)` | no duplicar en runtime |
| `closable` | no | hoy implícito | política del tab bar | si el framework lo permite, respetarlo |
| `dirty` / `stale` | sí | se incrustan en texto | metadata visual / badge / warning | ya no concatenar texto feo si el shell soporta badge/estado |

## 2.4 Traducción de estado visual recomendada

| Estado motor | dirty | stale | badge | estado visual tab sugerido |
| --- | --- | --- | --- | --- |
| `IDLE` | false | false | vacío | `visible` |
| `DIRTY_OR_STALE` | true | false | `dirty` | `hold` |
| `DIRTY_OR_STALE` | false | true | `stale` | `attention` |
| `VALIDATING` | cualquiera | cualquiera | `busy` | `visible` |
| `PLANNING` | cualquiera | cualquiera | `busy` | `visible` |
| `APPLYING` | cualquiera | cualquiera | `busy` | `visible` |
| `ROLLING_BACK` | cualquiera | cualquiera | `busy` | `visible` |
| `REFRESHING` | cualquiera | cualquiera | `busy` | `visible` |
| `FAILED` | cualquiera | cualquiera | `error` **INFERRED** | `attention` |
| `CLOSED` | cualquiera | cualquiera | vacío | `hidden` o removido |

> `error` como badge es **INFERRED**: el widget actual no lo emite explícito, pero conviene reservarlo en la shell nueva si se quiere feedback más claro.

---

## 3. Command bar projection -> Hero / toolbar payload

## 3.1 Payload fuente observado

`get_command_bar_projection()` expone:

- `root_dir`
- `mode_label`
- `mode`
- `busy`
- `session_id`
- `session_state`
- `actions.{action_name}.enabled`

## 3.2 Consumo actual

`CommandBar.set_state()` solo usa:

- `root_dir`
- `mode_label`
- `busy`

Ignora por completo `actions.*.enabled`.

## 3.3 Mapeo 1:1 recomendado

| Campo fuente | Consumidor actual | Consumidor nuevo | Regla |
| --- | --- | --- | --- |
| `root_dir` | `root_dir_input` | label/field de scope activo | solo lectura |
| `mode_label` | `mode_label` | chip o pill de modo | no inferir otro modo local |
| `busy` | enable/disable bruto de todos los botones | gating global + feedback de ejecución | se conserva |
| `actions.browse_root_dir.enabled` | ignorado hoy | botón browse | usar enablement fino |
| `actions.validate_active.enabled` | ignorado hoy | botón validate | usar enablement fino |
| `actions.plan_active.enabled` | ignorado hoy | botón plan | usar enablement fino |
| `actions.apply_active.enabled` | ignorado hoy | botón apply | usar enablement fino |
| `actions.rollback_active.enabled` | ignorado hoy | botón rollback | usar enablement fino |
| `actions.refresh_active.enabled` | ignorado hoy | botón refresh | usar enablement fino |
| `session_state` | ignorado hoy | badge/label contextual | lectura pura |

## 3.4 Regla del adapter

El adapter nuevo debe construir un `hero_action_model` con esta forma conceptual:

```yaml
hero_action_model:
  root_dir: <string>
  mode_label: <string>
  session_state: <string>
  busy: <bool>
  actions:
    browse_root_dir: { enabled: <bool> }
    validate_active: { enabled: <bool> }
    plan_active: { enabled: <bool> }
    apply_active: { enabled: <bool> }
    rollback_active: { enabled: <bool> }
    refresh_active: { enabled: <bool> }
```

---

## 4. Workspace projection -> Panel payloads

## 4.1 Payload fuente observado

`get_workspace_projection()` devuelve:

- `targets`
- `ops`
- `grouped_preview`
- `detail`
- `results`
- `status`
- `sessions`
- `command_bar`
- `scope`
- `selection`
- `ops_document`
- `plan`
- `diff`

## 4.2 Consumo actual exacto en `SessionWorkspace.set_projection()`

| Campo fuente | Widget actual | Setter | Forma esperada |
| --- | --- | --- | --- |
| `targets` | `TargetList` | `set_items(...)` | `Iterable[dict | str]` |
| `ops` | `OpsList` | `set_items(...)` | `Iterable[dict | str]` |
| `grouped_preview` | `PlanDiffStack` | `set_groups(...)` | `Iterable[dict]` |
| `detail` | `DetailStack` | `set_detail(...)` | `dict | list | str | None` |
| `results` | `BottomResultsTabs` | `set_payloads(...)` | `dict` |

## 4.3 Mapeo 1:1 recomendado a paneles glass

| Campo fuente | Panel destino | Rol sugerido | Setter/host recomendado | Regla |
| --- | --- | --- | --- | --- |
| `targets` | `scope_ops` | `form` | `TargetList.set_items()` o wrapper equivalente | preservar payload completo |
| `ops` | `scope_ops` | `form` | `OpsList.set_items()` o wrapper equivalente | preservar `content/summary` |
| `grouped_preview` | `preview` | `data` | `PlanDiffStack.set_groups()` | no aplanar grupos |
| `detail` | `detail` | `detail` | `DetailStack.set_detail()` | no convertir todo a string si aún es dict/list |
| `results` | `results_stream` | `summary` | `BottomResultsTabs.set_payloads()` | conservar keys `events/validation/plan/apply/rollback` |
| `status` | `status_summary` | `status` | `StatusStrip.set_summary()` | fuente oficial del footer |
| `scope` | `scope_ops` o metadata panel | `form` | sección lateral secundaria | útil para enriquecer shell sin tocar motor |
| `selection` | runtime context / inspector | `detail` | contexto de selección | solo lectura |
| `ops_document` | panel de ops o editor readonly **INFERRED** | `form` | contenido auxiliar | opcional en fase 1 |
| `plan` / `diff` | `preview` o tabs internas | `data` | vistas enriquecidas **INFERRED** | usar si se reemplaza `PlanDiffStack` luego |

---

## 5. Payloads por widget actual

## 5.1 `TargetList.set_items()`

### Contrato observado

Cada item puede ser:

- `str`
- `dict`

Si es `dict`, el texto visible usa:

1. `label`
2. `title`
3. fallback `target`

El payload entero se guarda en `QListWidgetItem.setData(32, payload)`.

### Regla de migración

No convertir targets a strings pelones si luego se necesita round-trip hacia `select_target(payload)`.

---

## 5.2 `OpsList.set_items()`

### Contrato observado

Cada item puede ser:

- `str`
- `dict`

Si es `dict`, el texto visible usa:

1. `label`
2. `title`
3. fallback `item`

### Regla de migración

Mantener:

- `label`
- `summary`
- `content`

si existen, para no reventar futuras vistas de detalle.

---

## 5.3 `PlanDiffStack.set_groups()`

### Contrato observado

Cada grupo esperado:

- `label` o `file`
- `summary`
- `items[]`

Cada item esperado:

- `label` o `title`
- `summary`

### Regla de migración

No aplastar `groups -> files -> items` en un texto largo. Ese árbol ya es un contrato visual útil.

---

## 5.4 `DetailStack.set_detail()`

### Contrato observado

Acepta:

- `None`
- `str`
- `dict`
- `list`

Si no es `str`, serializa a JSON bonito.

### Regla de migración

La shell nueva puede mejorar la presentación, pero debe seguir soportando ese rango de tipos.

---

## 5.5 `BottomResultsTabs.set_payloads()`

### Contrato observado

Espera diccionario con tabs:

- `events`
- `validation`
- `plan`
- `apply`
- `rollback`

Si el payload no es string, lo serializa a JSON.

### Regla de migración

Conservar nombres de superficies tal cual. Nada de renombrar `validation` por `checks` o `apply` por `execution`. Eso luego rompe rastreo y parity.

---

## 6. Campos críticos que no deben perderse

| Campo | De dónde sale | Por qué importa |
| --- | --- | --- |
| `session_id` | session tabs / status | amarra tabs con motor |
| `dirty` | status / tabs / scope metadata | gating y feedback |
| `stale` | status / tabs / scope metadata | refresh policy |
| `busy` | status / command bar / scope metadata | bloquea acciones |
| `selection.surface` | selection | foco lógico del resultado |
| `selection.detail` | selection | inspector |
| `results.events` | results surfaces | feed de eventos |
| `results.plan` | results surfaces | preview y enablement de apply |
| `results.apply` | results surfaces | enablement de rollback |
| `scope.targets[]` | scope projection | lista lateral y selección |

---

## 7. Reglas de transformación permitidas

## Permitidas

- traducir `session_tabs_projection[]` a `GlassWorkspaceTabSpec`
- traducir `status_projection` a footer/status model
- traducir `command_bar_projection.actions` a botones del hero
- agrupar payloads en un `panel_payloads` central

## Prohibidas

- recalcular `dirty/stale/busy` en el adapter
- inferir `active_session_id` desde tab actual visual
- perder llaves de payload al “simplificar” items
- mutar negocio desde el adapter para que la UI se vea bien

---

## 8. Modelo objetivo de salida del adapter

```yaml
adapter_output:
  workspace_tabs:
    - tab_id: <session_id>
      title: <title>
      badge: <badge>
      state: <visual_state>
      tooltip: <tooltip>
      metadata:
        dirty: <bool>
        stale: <bool>
        session_state: <state>

  hero:
    root_dir: <string>
    mode_label: <string>
    session_state: <string>
    busy: <bool>
    actions: {...}

  panels:
    scope_ops:
      targets: [...]
      ops: [...]
      scope: {...}
    preview:
      grouped_preview: [...]
      plan: {...}
      diff: {...}
    detail:
      detail: <payload>
      selection: {...}
    results_stream:
      results: {...}
    status_summary:
      status: {...}
```

---

## 9. Criterios de aceptación

- todos los campos consumidos hoy por widgets siguen disponibles en la shell nueva
- `actions.*.enabled` sí se usa en la UI nueva
- ningún payload crítico se degrada de `dict` a `str` sin justificación
- `results` conserva sus superficies canónicas
- `session_id` sigue siendo el amarre único entre tab visual y sesión real

---

## 10. Definition of done de este documento

El mapping 1:1 queda completo cuando el adapter nuevo puede reconstruir toda la carcasa visual nueva únicamente a partir de `WorkspaceFacade`, sin leer estado directo del core y sin perder semántica de payload en el camino.
