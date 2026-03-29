# 01_FORGEOS_MASTER_BLUEPRINT.md

Este es el blueprint maestro para reconstruir ForgeOS con gobierno de sistema.  
La evidencia viene del bundle legado, en particular:

- `main.py`
- `app/gui_qt/main_window.py`
- `app/gui_qt/event_bus.py`
- `app/gui_qt/command_dispatcher.py`
- `app/gui_qt/services/service_container.py`
- `app/gui_qt/shell/*`
- `app/gui_qt/tools/catalog.py`
- `app/backend/analyzer_backend.py`
- `app/gui_qt/plugins/*`
- pruebas bajo `app/gui_qt/tests/*`
- documentos del handoff obligatorios

La regla rectora es simple: **el código actual es evidencia de cómo se rompió el sistema, no un molde del target**.

## 1. Mapa de capas

### Hechos
- `main.py` solo levanta `QApplication` y delega la composición real a `RepoAnalyzerMainWindow`.
- `app/gui_qt/main_window.py` concentra bootstrap, servicios, controllers, shell, plugin loading, UI build y cierre.
- El handoff ya señaló mezcla de al menos cinco zonas: analyzer core, shell Qt, runtime/context/tools, plugin platform y productos embebidos.
- `app/backend/analyzer_backend.py` contiene un dominio claro de análisis de repositorio, pero hoy está acoplado al host.
- `plugins/cloudflare_guardian` y `plugins/orchestrator_bridge` son productos o proto-productos incrustados dentro del host.
- `preferences/*` y parte de diagnostics muestran material reusable, pero hoy viven dentro del árbol del host.

### Supuestos
- ForgeOS debe sostener más de un producto en el tiempo.
- La primera reconstrucción puede conservar una forma de host de escritorio, pero la doctrina de capas debe seguir siendo independiente del toolkit.
- No existe obligación de mantener compatibilidad binaria con la arquitectura de plugins legacy.

### Inferencias
- El target correcto no es “host + plugins libres”; es **Kernel + Commons + Products**.
- Lo reusable debe salir del host y entrar a Forge Commons solo si es neutral al dominio.
- El dominio `repo analyzer` debe existir como producto y dejar de vivir disperso entre backend y shell.

### Decisión operativa

```text
ForgeOS
├─ Forge Kernel
│  ├─ bootstrap y session orchestration
│  ├─ host shell domain-agnostic
│  ├─ contract runtime
│  ├─ lifecycle authority
│  ├─ state authority registry
│  ├─ extension registry
│  ├─ observability y failure isolation
│  └─ packaging / compatibility gates
├─ Forge Commons
│  ├─ config_policy
│  ├─ diagnostics
│  ├─ process_execution
│  ├─ history_runs
│  └─ export_artifacts
└─ Forge Products
   ├─ repo_analyzer        (inferido por evidencia)
   ├─ cloudflare_guardian
   └─ orchestrator_bridge
```

---

## 2. Inventario de subsistemas

### Hechos
- **Composición raíz**: `main.py` + `app/gui_qt/main_window.py`.
- **Infraestructura string-based**: `event_bus.py`, `command_dispatcher.py`, `services/service_container.py`.
- **Shell y runtime**: `layout_manager.py`, `dock_manager.py`, `toolbar_controller.py`, `shell/tool_workspace.py`, `shell/context_bridge.py`, `shell/group_shell.py`, `shell/status_strip.py`.
- **Catálogo y launcher**: `tools/catalog.py`, `shell/tool_launcher.py`.
- **Preferencias/política**: `preferences/runtime.py`, `preferences/policy.py`, `preferences/applicator.py`.
- **Dominio repo analyzer**: `app/backend/analyzer_backend.py`, `tree_controller.py`, `search_controller.py`, `preview_controller.py`, `navigation_controller.py`, `shell/workspace_runtime.py`.
- **Plataforma de extensiones actual**: `plugins/plugin_manager.py`, `plugins/plugin_manifest.py`, `ui_contribution_registry.py`.
- **Productos incrustados**:
  - `plugins/cloudflare_guardian/*`
  - `plugins/orchestrator_bridge/*`
- **Artefactos y residuos no portables**:
  - `__pycache__`
  - `.pytest_cache`
  - `.repo_analyzer_settings.json`
  - loaders legacy `*_plugin.py`

### Supuestos
- Los productos iniciales de la primera ola son `repo_analyzer`, `cloudflare_guardian` y `orchestrator_bridge`.
- Los plugins `failure_injection`, `mi_plugin`, `demo_ui_validation` y los single-file legacy loaders no forman parte del baseline de plataforma limpia.

### Inferencias
- El inventario del target debe reescribirse por ownership, no por carpeta heredada.
- Varios subsistemas del shell actual deben dividirse: una parte va al kernel, otra a commons, otra a productos.
- La categoría “tool” del sistema actual es insuficiente; hay que distinguir producto, capability, contribution y surface.

### Inventario de target por owner

| Subsistema target | Owner target | Capa | Origen de evidencia | Decisión |
| --- | --- | --- | --- | --- |
| Bootstrap y session orchestration | Forge Kernel | Kernel | `main.py`, `main_window.py` | Reescribir |
| Contract runtime | Forge Kernel | Kernel | `event_bus.py`, `command_dispatcher.py` | Reemplazar |
| Extension registry | Forge Kernel | Kernel | `plugin_manager.py` | Reescribir sin legacy loader |
| Host shell | Forge Kernel | Kernel | `dock_manager.py`, `layout_manager.py`, `tool_workspace.py` | Reescribir |
| Config & policy capability | Forge Commons | Commons | `preferences/*` | Extraer |
| Diagnostics capability | Forge Commons | Commons | startup/plugin diagnostics | Extraer |
| Process execution capability | Forge Commons | Commons | `process_session_controller.py`, timeouts bridge | Extraer parcial |
| History & runs capability | Forge Commons | Commons | `bridge_history.py`, session manifests | Extraer |
| Repo Analyzer product | Forge Products | Product | `AnalyzerBackend` + controllers | Migrar como producto |
| Cloudflare Guardian product | Forge Products | Product | `plugins/cloudflare_guardian/*` | Migrar como producto |
| Orchestrator Bridge product | Forge Products | Product | `plugins/orchestrator_bridge/*` | Migrar como producto |
| Legacy shims y loaders | Nadie | Delete | compatibilidad legacy dispersa | Eliminar |

---

## 3. Fuente de verdad por dominio

### Hechos
- El host usa `QSettings` para geometry, window state, splitter sizes, último repo, preview y estado de tools.
- `AnalyzerBackend` persiste `.repo_analyzer_settings.json` en el project root.
- `plugins/orchestrator_bridge/bridge_config.py` y `bridge_history.py` persisten configuración e historial propios.
- `ToolWorkspaceCoordinator` persiste snapshot de restore y active tool por separado en `QSettings`.
- `WorkstationContextRuntime` intenta ser contexto global, pero mezcla estado de shell con campos Cloudflare product-specific.
- Gran parte del estado efectivo también vive duplicado en atributos de `main_window` y controllers.

### Supuestos
- Ningún store actual debe heredarse sin antes asignarlo a un owner del target.
- La reconstrucción no tiene por qué conservar las keys ni archivos de persistencia legacy.

### Inferencias
- Hoy no existe una sola “fuente de verdad”; existe una constelación de autoridades débiles.
- La primera corrección fuerte es partir el state por dueño y por capa.
- El contexto kernel debe ser mínimo y neutral; el resto se publica desde productos o capabilities.

### Mapa de autoridad de verdad

| Dominio | Evidencia legacy | Authority target | Capa target | Nota |
| --- | --- | --- | --- | --- |
| Sesión de plataforma | `main_window` + `WorkstationContextRuntime` | Kernel Session Store | Kernel | Sin campos de producto |
| Layout y chrome del host | `QSettings` vía `layout_manager.py` y `main_window.py` | Kernel Host Layout Store | Kernel | Solo layout y preferencias de shell |
| Política runtime global | `preferences/runtime.py` | Commons Config & Policy Store | Commons | Perfiles y overrides autorizados |
| Índice / búsqueda / preview de repositorio | `AnalyzerBackend` + controllers | Repo Analyzer Store | Product | No pertenece al host |
| Contexto diagnóstico Cloudflare | `guardian_contract.py` + contexto contaminado | Cloudflare Guardian Store | Product | El host solo ve published context aprobado |
| Run sessions y payloads de ejecución | `orchestrator_bridge/plugin.py` + history | Orchestrator Bridge Store + Commons History/Runs | Product + Commons | Separar request state de run ledger |
| Telemetría de proceso | evento `PROCESS_SESSION_STATE_CHANGED` y state machine del bridge | Commons Process Execution Runtime | Commons | Neutral al dominio |
| Registro de paquetes instalados | No existe de forma limpia hoy | Kernel Packaging Registry | Kernel | Nuevo |

---

## 4. Contratos entre capas

### Hechos
- `EventBus` usa strings libres y payloads sin esquema.
- `CommandDispatcher` registra y ejecuta comandos por string.
- `UIContributionRegistry` guarda contribuciones declarativas, pero sin versionado contractual.
- `ShellContributionBridge` deriva `tool_id` cortando strings de `contribution_id`.
- `PluginManager` expone aliases públicos `get_all_tools`, `enable_tool`, `disable_tool`, mezclando plugin y product language.
- Las pruebas y el runtime actual legitiman contratos implícitos por naming y convenciones.

### Supuestos
- Todo intercambio cross-layer del target debe ser auditable, versionable y validable antes de ejecutar.
- El runtime futuro debe poder negar activaciones o contributions incompatibles antes de renderizar nada.

### Inferencias
- El bus y el dispatcher actuales no deben sobrevivir como surface oficial.
- ForgeOS necesita familias contractuales claras: lifecycle, state, command, event, contribution, capability service, persistence, packaging y compatibility.
- Los contratos deben vivir antes que los productos migrados.

### Sistema contractual target

| Familia contractual | Problema legacy que corrige | Dueño target | Dirección típica |
| --- | --- | --- | --- |
| Lifecycle | Constructores que se autoconectan y cierres incompletos | Forge Kernel | Kernel -> capability/producto |
| State | State duplicado y sin autoridad | Dueño del state slice | Owner <-> consumidor autorizado |
| Command | Acciones por string sin SLA | Owner de la acción | Host/producto -> owner |
| Event | Pub/sub sin schema ni versionado | Owner del hecho | Producer -> subscribers |
| Contribution | UI hooks ambiguos y derivados por naming | Producto + Kernel | Producto -> Host |
| Capability Service | Reach-through al container | Forge Commons capability owner | Producto/Kernel -> Commons |
| Persistence | Stores dispersos y opacos | Owner del store | Owner -> storage |
| Packaging | Empaquetado implícito | Kernel Packaging | Package -> installer/runtime |
| Compatibility | Compatibilidad asumida | Package owner | Package -> install/release gate |

---

## 5. Lifecycle

### Hechos
- `ToolWorkspaceCoordinator` define operaciones `activate`, `deactivate`, `hide`, `close`, `unload`, `destroy`, `reopen_last_active_tool`, `set_tool_enabled`.
- El documento `ARCHITECTURE_WORKSTATION.md` declara close no destructivo y un solo active tool.
- `PluginManager` tiene `initialize_all()`, `shutdown_plugin()` y `shutdown_all()`.
- `main_window.closeEvent()` dispone algunos runtimes, pero no llama `plugin_manager.shutdown_all()`.
- El `ToolWorkspaceCoordinator` intenta suscribirse al contexto global en el constructor, antes de que exista `event_bus` en el startup real.
- Productos y capabilities no comparten una máquina de estados canónica.

### Supuestos
- ForgeOS debe conservar un modelo de activación/suspensión explícito porque varios productos tendrán superficies y recursos costosos.
- El host puede manejar un **primary product slot** activo a la vez como default inicial, pero sin hardcodear productos.

### Inferencias
- El lifecycle no puede depender del orden casual de construcción de objetos.
- El kernel debe ser la autoridad de discover/register/prepare/activate/suspend/dispose.
- Todo paquete debe tener teardown declarativo y verificable.

### Modelo target de lifecycle

| Entidad | Estados target | Autoridad | Teardown esperado |
| --- | --- | --- | --- |
| Producto | discovered -> registered -> prepared -> active -> suspended -> faulted -> disposing -> disposed | Forge Kernel Lifecycle | subscriptions, views, tasks, stores locales |
| Capability | declared -> validated -> ready -> serving -> degraded -> disposing -> disposed | Kernel + capability owner | workers, pipes, stores, caches |
| Surface de host | unbound -> bound -> visible -> hidden -> disposing -> disposed | Host shell | widgets y bindings del slot |
| Proceso externo | requested -> spawned -> streaming -> finished|timed_out|killed -> reaped | Commons Process Execution | kill, drain, logs, temp dirs |
| Sesión de plataforma | booting -> running -> shutting_down -> stopped | Forge Kernel | dispose ordenado de kernel, commons y products |

---

## 6. Dependencias duras vs blandas

### Hechos
- Métrica local sobre la fuente: `workspace_runtime.py` usa `self.main` 148 veces; `preview_controller.py` y `toolbar_controller.py` 111; `search_controller.py` 102; `layout_manager.py` 100.
- Métrica local: `plugins/orchestrator_bridge/plugin.py` hace 93 service lookups; `cloudflare_guardian/state_adapter.py` 56.
- `cloudflare_guardian/state_adapter.py` resuelve `main_window` y raspa internals del host.
- `ShellGroupRuntime` y `ToolCatalogService` toman decisiones con strings de producto.
- `PluginContext` da acceso a `event_bus`, `dispatcher`, `container` y por esa vía al `main_window`.

### Supuestos
- El target debe reducir dependencias duras a vínculos intra-capa o hacia APIs públicas inferiores.
- Todo lo demás debe convertirse en dependencia blanda declarada, validada y observable.

### Inferencias
- `self.main` es la autopista principal del acoplamiento oculto.
- El container global destruye las fronteras porque convierte cualquier dependencia en una string lookup.
- La frontera correcta es: imports públicos limitados + contratos explícitos + adapters.

### Regla target

- **Dependencia dura permitida**
  - dentro del mismo package/layer;
  - hacia APIs públicas del kernel;
  - hacia un capability contratado de Commons;
  - hacia adapters externos declarados.

- **Dependencia blanda permitida**
  - capability opcional con compatibilidad declarada;
  - contribution opt-in del producto;
  - published context consumido por el host bajo contrato.

- **Dependencia prohibida**
  - producto -> internals del host;
  - commons -> producto;
  - kernel -> lógica o strings de producto;
  - producto -> otro producto;
  - cualquier capa -> service locator string-based como mecanismo principal.

---

## 7. Patologías del diseño actual

### Hechos
- El diseño actual presenta patologías sistémicas, no detalles aislados.
- Las más serias son de autoridad, frontera, lifecycle y teardown.

### Supuestos
- Tratar estas patologías como bugs locales condenaría la reconstrucción a repetir el patrón.
- La única salida limpia es cambiar el gobierno del sistema.

### Inferencias
- El repo actual sirve para extraer semántica y evidencias, no para preservar estructura.
- Algunas piezas deben **extraerse**, otras **reescribirse** y varias deben **eliminarse**.

### Catálogo resumido

| ID | Patología | Severidad | Acción target |
| --- | --- | --- | --- |
| P1 | Raíz de composición hipertrofiada | Alta | Reemplazar por bootstrap de Forge Kernel más host shell domain-agnostic. |
| P2 | God object por delegación | Alta | Cortar por contratos y state authority explícita. |
| P3 | Suscripción temprana rota o frágil | Alta | Hacer que lifecycle de registro/suscripción sea autoridad del kernel, no del constructor. |
| P4 | Lifecycle incompleto en cierre | Alta | Teardown ledger obligatorio y cierre gobernado por kernel. |
| P5 | Contaminación de contexto de host | Alta | Crear contexto kernel mínimo y contextos publicados por producto. |
| P6 | Contaminación product-specific del host | Alta | Eliminar heurísticas basadas en strings y usar manifests/contratos. |
| P7 | Acoplamiento oculto por service container global | Alta | Reemplazar por capability broker y handles explícitos. |
| P8 | Scraping de host por producto | Alta | Rehacer como producto aislado con contratos de estado/contexto. |
| P9 | Persistencia fragmentada | Alta | Definir source of truth por dominio y capability. |
| P10 | Compatibilidad legacy pegada al core | Media | Quarantine y luego delete; no portar a ForgeOS. |
| P11 | Contratos string-based sin esquema | Alta | Sistema de contratos versionados y validados. |
| P12 | Pruebas codifican contaminación | Media | Reescribir pruebas sobre contratos y slot model, no nombres de producto. |
| P13 | Residuos de bundle en fuente | Media | Eliminar del target y del pipeline de empaquetado. |

Las descripciones completas viven en `/appendix/legacy_pathologies_catalog.md`.

---

## 8. Orden oficial de reconstrucción

### Hechos
- El handoff ya eligió **reconstrucción por gobierno de sistemas**.
- El sistema actual mezcla host, productos y capabilities en el mismo runtime.
- Si se migran productos antes de fijar kernel y contratos, la contaminación se vuelve a colar.

### Supuestos
- El operador de implementación posterior necesita una secuencia cerrada, no un buffet.
- La primera victoria arquitectónica es lograr un host vacío, limpio y operable.

### Inferencias
- El orden correcto es: verdad -> kernel -> contratos -> commons -> host -> skeleton -> migraciones -> packaging -> polish.
- La migración de productos debe hacerse uno por uno y con gates entre cada paso.

### Orden oficial
1. Truth capture
2. Kernel definition
3. Contract system
4. Shared capabilities definition
5. Host shell rebuild
6. Product skeleton establishment
7. Product migrations
8. Packaging hardening
9. Visual/system polish

El desarrollo detallado de cada fase vive en `09_RECONSTRUCTION_ORDER.md`.
