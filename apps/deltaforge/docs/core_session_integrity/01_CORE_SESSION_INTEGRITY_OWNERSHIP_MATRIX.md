# Core Session Integrity | Ownership Matrix

## Regla madre
La verdad operativa vive en la **sesión sobre un scope**.

| Dato / señal | Owner | Lectores | Únicos mutadores legales | Fuentes de verdad prohibidas |
|---|---|---|---|---|
| `scope` | `SessionWorkspace` | panes, facade/controller, policies de sesión, adapter cuando requiera contexto | creación de sesión, cambio explícito de scope desde application | panes, widgets, `main_window`, watcher, strings sueltos, helpers de UI |
| `ops_document` | `SessionWorkspace` | left ops panel, plan/diff/results projections, controller/facade | acciones explícitas de edición/carga/replace del documento desde application | widget/editor, pane state local, cache global, mock adapter |
| `dirty` | `SessionWorkspace` | status bar, tabs, panes, controller/facade, policies | política de sesión al detectar edición semántica de ops o cambios locales pendientes | widgets, watcher directamente, event bus, pane flags, `main_window` |
| `stale` | `SessionWorkspace` | status bar, refresh policy, panes, controller/facade | política de sesión cuando entra señal externa relevante o invalidación semántica | watcher como source of truth final, UI, event bus, buffers globales |
| `busy` | `SessionWorkspace` | panes, status bar, command gating, controller/facade | acciones transaccionales de application al iniciar/terminar validate/plan/apply/rollback/refresh | spinner local de widget, diálogos, `main_window`, adapter fuera del flujo |
| `event_feed_visible` | `SessionWorkspace` como proyección session-scoped | bottom events panel, debug surfaces, status summaries | la sesión anexa eventos relevantes de su lifecycle; el bus solo entrega | event bus como storage, buffer global compartido, pane local, logger de UI |
| `refresh_requested` | `SessionWorkspace` o transición registrada en application | refresh policy, controller/facade, status surfaces | acciones explícitas de usuario o invalidación que levante intención formal de refresh vía application | botón del pane como truth source, watcher directo, `main_window`, flags locales de UI |
| `refresh_completed` | `SessionWorkspace` como resultado de transición | panes, status bar, policies, controller/facade | flujo de refresh al cerrar reconciliación de sesión | callback de widget, adapter suelto, watcher, event bus |
| `session_state` | `SessionWorkspace` | tabs, panes, status bar, controller/facade | state machine / session actions en application | widgets, busy dialogs, watcher, adapter directo |
| `validation_result` / `plan_result` / `apply_result` / `rollback_result` | `SessionWorkspace` | bottom tabs, right detail, center views, status summaries | flujos de application al completar operación correspondiente | pane cache, global singleton, adapter reteniendo verdad |
| `external_change_signal` | watcher de infrastructure, solo como señal | stale policy, session actions, event translation layer | watcher emite señal; no decide `dirty`/`stale` final | panes, domain, callbacks de UI, event bus como reinterpretador libre |
| `engine_response_raw` | `EngineAdapter` / infraestructura transitoria | application mientras traduce | adapter durante la llamada concreta | UI, `SessionWorkspace` como storage crudo, panes |
| `engine_result_normalized` | application flow antes de persistir en sesión | `SessionWorkspace`, panes vía proyección | controller/session actions al normalizar respuesta | widgets, adapter crudo, globals |
| `active_session_id` | `SessionManager` | `main_window`, tabs, facade/controller, panes vía proyección | acciones de selección/creación/cierre de sesión | panes locales, widgets, globals |
| `session_collection` | `SessionManager` | `main_window`, session tabs, facade/controller | create/clone/close actions | panes, widgets, persistence store como verdad viva |
| `pane_layout_state` | UI/window layer o persistence de layout | `main_window`, widgets contenedores | `main_window` / layout restore flows | domain, session core, watcher, engine |
| `settings` persistibles | settings store + modelo de settings | bootstrap, UI theme/system, config surfaces | flujos explícitos de carga/guardado | panes como verdad, `SessionWorkspace`, globals mágicos |

## Foco rojo inmediato
- `bottom_events_panel` leyendo buffer global
- editor de ops marcando `dirty` directo
- watcher escribiendo estado de sesión
- `main_window` resolviendo negocio
- `refresh` limpiando o degradando sin transición formal
- `scope` como string/path sin tipo explícito
