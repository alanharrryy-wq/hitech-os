# Developer Fast Path

## Objetivo
Reducir fricción diaria para cambios en app core y plugins sin reabrir arquitectura.

## Qué se agregó

### 1) Diagnóstico runtime central
- `RuntimeDiagnostics` (`app/gui_qt/dev_diagnostics.py`)
- Resumen de startup con pasos, warnings y estado runtime:
  - `RepoAnalyzerMainWindow.get_developer_diagnostics_snapshot()`
  - `PluginManager.get_diagnostics_report()`
  - `ShellContributionBridge.get_integration_report()`

### 2) Fast-path de integración para plugins
- `PluginContext.register_safe_dock(...)`
- `PluginContext.register_safe_toolbar_action(...)`
- `PluginContext.register_safe_menu_action(...)`

Estos helpers validan entradas, normalizan defaults útiles y agregan marcadores visuales para integración automática.

### 3) Fast-path de paneles core/plugin en docks
- `DockManager.register_feature_panel(...)`

Unifica creación de dock, flags, widget attach, marcadores visuales y paso por runtime visual.

### 4) Self-test ejecutable para dev
- `dev_self_test.py`
- Verifica en una corrida:
  - startup shell
  - indexado
  - búsqueda
  - carga de plugins
  - attach de plugin docks
  - attach explícito de acciones plugin en toolbar
  - attach explícito de acciones plugin en menú
  - integración de contribuciones
  - reproceso idempotente de subárbol visual

### 5) Validación estricta de `plugin.json`
- `PluginManifest.from_dict(...)` ahora valida contrato de forma estricta:
  - `id` con formato estable (`^[a-z][a-z0-9_]{1,63}$`)
  - `version` en formato semver
  - `module` relativo y seguro (sin `..`, solo segmentos válidos)
  - `class_name` válido
  - `enabled` boolean
  - `dependencies` sin duplicados, sin self-dependency e ids válidos
  - `ui` solo con claves soportadas y valores boolean
- `PluginManager` valida también layout de módulo antes de cargar.

### 6) Failure injection determinístico
- Plugin: `app/gui_qt/plugins/failure_injection`
- Env var: `HITECH_QT_FAILURE_INJECTION_MODE`
  - `off` (default)
  - `load`
  - `init`
  - `integration`
- `dev_self_test.py` soporta `--failure-mode` para verificar rutas de error esperadas.

### 7) CI headless en PR
- Workflow: `.github/workflows/repo-analyzer-self-test.yml`
- Ejecuta en cada PR:
  - self-test normal (`failure-mode off`)
  - matriz de failure injection (`load`, `init`, `integration`)
  - validación explícita de contribuciones plugin en dock/toolbar/menu

## Modo debug/trace

Por defecto está silencioso.

Activación:
- variable de entorno: `HITECH_QT_DEV_TRACE=1`
- setting Qt: `developer_debug_mode=true`

Cuando está activo:
- se emiten trazas de startup, plugin integration, dock runtime y skin runtime.

## Happy Path: agregar plugin nuevo

1. Implementa plugin y registra UI por `PluginContext` safe helpers:
   - `register_safe_dock`
   - `register_safe_toolbar_action`
   - `register_safe_menu_action`
2. Evita wiring manual en `main_window.py`.
3. Deja el dock/widget pasar por runtime automático (visual + integración).
4. Corre validación rápida (abajo).

## Happy Path: agregar panel/dock core nuevo

1. Usa `DockManager.register_feature_panel(...)`.
2. Provee `widget_factory` y `object_name` claro.
3. Evita repetir lógica de `QDockWidget` manual en nuevos call-sites.
4. Si agregas subárbol tardío/reconstruido, usa:
   - `main_window.process_visual_subtree(widget, reason='...')`

## Validación rápida recomendada

### Compile
```powershell
python -m py_compile `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\dev_diagnostics.py `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\main_window.py `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\dock_manager.py `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\plugins\plugin_base.py `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\plugins\plugin_manager.py `
  F:\repos\hitech-os\tools\graphviz\repo_analizer\app\gui_qt\shell\contribution_bridge.py
```

### Self-test normal (quiet by default)
```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\dev_self_test.py `
  --repo F:\repos\hitech-os\tools\graphviz\repo_analizer `
  --query plugin `
  --failure-mode off
```

### Self-test con trace
```powershell
$env:HITECH_QT_DEV_TRACE='1'
python F:\repos\hitech-os\tools\graphviz\repo_analizer\dev_self_test.py `
  --repo F:\repos\hitech-os\tools\graphviz\repo_analizer `
  --query plugin `
  --failure-mode off `
  --debug
```

### Self-test failure injection (determinístico)
```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\dev_self_test.py `
  --repo F:\repos\hitech-os\tools\graphviz\repo_analizer `
  --query plugin `
  --failure-mode load
```

```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\dev_self_test.py `
  --repo F:\repos\hitech-os\tools\graphviz\repo_analizer `
  --query plugin `
  --failure-mode init
```

```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\dev_self_test.py `
  --repo F:\repos\hitech-os\tools\graphviz\repo_analizer `
  --query plugin `
  --failure-mode integration
```

## Checklist antes de considerar un cambio “good”

1. `py_compile` limpio en archivos tocados.
2. `dev_self_test.py` en modo normal.
3. `dev_self_test.py --debug` para inspección de trazas si tocaste wiring/runtime.
4. `startup_summary.status == "ok"` o justificar degradación.
5. `plugin_report_counts.load_failures == 0` y `init_failures == 0`.
6. `integration_report_counts.failed == 0`.
