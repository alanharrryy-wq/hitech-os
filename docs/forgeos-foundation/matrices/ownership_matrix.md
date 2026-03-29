# ownership_matrix.md

Matriz de ownership derivada de la evidencia legacy y del target ForgeOS.

| Activo / dominio | Evidencia legacy | Owner actual efectivo | Owner target | Capa target | Nota |
| --- | --- | --- | --- | --- | --- |
| Bootstrap de proceso | `main.py` | Difuso entre launcher y `RepoAnalyzerMainWindow` | Forge Kernel | Kernel | Crear boot limpio y sin lógica de producto. |
| Host shell y composición de sesión | `app/gui_qt/main_window.py`, `layout_manager.py`, `dock_manager.py` | Host + controllers + plugins | Forge Kernel Host Shell | Kernel | El host es domain-agnostic. |
| Registro de extensiones | `plugin_manager.py`, `plugin_manifest.py` | PluginManager | Forge Kernel Extension Registry | Kernel | Sin legacy loader en target. |
| Estado de sesión del host | `WorkstationContextRuntime`, QSettings de layout | Difuso | Forge Kernel Session State | Kernel | Solo estado de shell y sesión, no dominio. |
| Política runtime / preferencias | `preferences/runtime.py`, `policy.py`, `applicator.py` | Host actual | Forge Commons Config & Policy | Commons | Reutilizable y transversal. |
| Diagnósticos y health | reportes de startup y plugin diagnostics | Host actual | Forge Commons Diagnostics | Commons | Compartido entre capas. |
| Repo analysis domain | `app/backend/analyzer_backend.py`, search/tree/preview controllers | Host actual | Forge Product `repo_analyzer` | Product | Producto inferido a partir de la evidencia. |
| Cloudflare diagnostics domain | `plugins/cloudflare_guardian/*` | Producto pero con fuga al host | Forge Product `cloudflare_guardian` | Product | No entra al kernel. |
| Orchestrator workflows | `plugins/orchestrator_bridge/*` | Producto pero con infraestructura embebida | Forge Product `orchestrator_bridge` | Product | Usará Commons Process Execution. |
| Supervisión de procesos | lógica genérica en Orchestrator Bridge | Producto | Forge Commons Process Execution | Commons | Solo la parte generic runtime. |
| Run ledger / history | `bridge_history.py` y manifests de sesión | Producto + artefactos externos | Forge Commons History & Runs | Commons | No incluye payload de negocio. |
| Exportación de artefactos | zips/manifests/reportes dispersos | Difuso | Forge Commons Export | Commons | BOM y manifests compartidos. |
| Dev/demo plugins | `failure_injection`, `mi_plugin`, `demo_ui_validation`, `*_plugin.py` | PluginManager | Quarantine o delete | Fuera de plataforma base | No son productos de primera ola. |
| Residuos locales | `__pycache__`, `.pytest_cache`, `.repo_analyzer_settings.json` | Nadie | Delete | N/A | No migrar. |
