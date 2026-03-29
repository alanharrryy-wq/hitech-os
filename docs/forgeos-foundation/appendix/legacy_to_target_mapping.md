# legacy_to_target_mapping.md

Mapa de traducción entre evidencia legacy y el target ForgeOS.

| Legado | Rol actual observado | Target ForgeOS | Acción | Nota |
| --- | --- | --- | --- | --- |
| `main.py` | launcher mínimo | Forge Kernel / process bootstrap | rebuild | Mantener launcher delgado; sacar composición a kernel boot. |
| `app/gui_qt/main_window.py` | god object de host | Separar en Forge Kernel bootstrap + Host Shell Runtime + Extension Registry | rebuild | No portar archivo ni responsabilidad agregada. |
| `app/gui_qt/event_bus.py` | bus string-based | Forge Kernel Contract Runtime / event contracts | rebuild | Sin strings libres como surface final. |
| `app/gui_qt/command_dispatcher.py` | dispatcher string-based | Forge Kernel Contract Runtime / command contracts | rebuild | Con timeout, validation y ownership. |
| `app/gui_qt/services/service_container.py` | service locator global | Eliminar; sustituir por capability broker y public APIs acotadas | delete | No migrar como API pública. |
| `app/gui_qt/ui_contribution_registry.py` | registro de contribuciones | Forge Kernel Extension Registry | refactor/rebuild | Mantener idea, no implementación informal. |
| `app/gui_qt/shell/group_shell.py` | routing de grupos con heurísticas de producto | Forge Kernel Host Shell slots + contribution contracts | delete/rebuild | Eliminar mapeos graph/run a productos concretos. |
| `app/gui_qt/shell/tool_workspace.py` | workspace lifecycle difuso | Forge Kernel Host Shell + product lifecycle contracts | rebuild | Sin suscripción temprana ni side effects en constructor. |
| `app/gui_qt/shell/context_bridge.py` | bridge contextual | Kernel published-context bridge | rebuild | Solo contract-aware. |
| `app/gui_qt/shell/workstation_context.py` | contexto de host contaminado | Kernel session context mínimo + published contexts de productos | split/delete | Campos product-specific salen del host. |
| `app/gui_qt/tools/catalog.py` | catálogo con semántica de producto | Forge Kernel contribution index | rebuild | Clasificación por manifest, no por strings. |
| `app/backend/analyzer_backend.py` | backend de análisis de repositorio | Forge Product `repo_analyzer` | extract | Mantener dominio, mover fuera del host. |
| `app/gui_qt/search_controller.py` | búsqueda de repo analyzer mezclada con host | Product `repo_analyzer` application/views | extract | No promover a commons todavía. |
| `app/gui_qt/preview_controller.py` | preview con legacy shims | Product `repo_analyzer` views/adapters | extract/rewrite | Eliminar compat shim salvo requirement explícito. |
| `app/gui_qt/layout_manager.py` | layout control del host acoplado a main | Forge Kernel Host Shell Runtime | rebuild | UI shell domain-agnostic. |
| `app/gui_qt/dock_manager.py` | dock orchestration | Forge Kernel Host Shell Runtime | rebuild | No conoce productos. |
| `app/gui_qt/toolbar_controller.py` | toolbar con acoplamiento alto | Kernel host action surfaces | rebuild | Acciones vía contribution contracts. |
| `app/gui_qt/preferences/runtime.py` | runtime preferences | Forge Commons Config & Policy | promote | Capacidad reusable. |
| `app/gui_qt/preferences/policy.py` | policy rules | Forge Commons Config & Policy | promote | Governance transversal. |
| `app/gui_qt/preferences/applicator.py` | aplicación de preferencias | Forge Commons Config & Policy + kernel integration adapter | promote/split | Separar UI adapter de lógica policy. |
| `app/gui_qt/plugins/plugin_manager.py` | extensibilidad + compat legacy | Forge Kernel Package/Extension Runtime | rebuild | Sin single-file plugins ni aliases tool/plugin. |
| `app/gui_qt/plugins/plugin_manifest.py` | manifiesto de plugin | Forge Product/Commons package manifests | evolve | Reubicar bajo packaging/contracts gobernados. |
| `plugins/cloudflare_guardian/*` | producto incrustado | Forge Product `cloudflare_guardian` | extract | Totalmente fuera del host. |
| `plugins/cloudflare_guardian/state_adapter.py` | host scraping adapter | N/A | delete | No existe equivalente aceptable. |
| `plugins/cloudflare_guardian/guardian_contract.py` | contrato cloudflare-specific | Producto `cloudflare_guardian` | retain-local | Nunca subir al kernel. |
| `plugins/cloudflare_guardian/graph_radar.py` | UI graph específica | Producto `cloudflare_guardian` views | retain-local | No promover a commons. |
| `plugins/orchestrator_bridge/*` | producto incrustado | Forge Product `orchestrator_bridge` | extract | Separar dominio de runtime genérico. |
| `plugins/orchestrator_bridge/process_session_controller.py` | supervisión de procesos semi-genérica | Forge Commons Process Execution | split/promote | Promover solo el runtime genérico. |
| `plugins/orchestrator_bridge/bridge_history.py` | run/history ledger | Forge Commons History & Runs | split/promote | Separar payload de negocio. |
| `bridge_config.json` y config propia del bridge | config de producto | Forge Product `orchestrator_bridge` o Forge Commons Config según scope | split | No mezclar runtime global con config de dominio. |
| `*_plugin.py` legacy single-file loaders | legacy compat loader | N/A | delete | No portarlos al sistema limpio. |
| `__pycache__`, `.pytest_cache`, `.repo_analyzer_settings.json` | residuos locales | N/A | delete | No migrar ni empacar. |
