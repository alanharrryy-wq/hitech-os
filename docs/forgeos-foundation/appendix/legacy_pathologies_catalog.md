# legacy_pathologies_catalog.md

Catálogo de patologías detectadas en la evidencia legacy y cómo deben tratarse en el target ForgeOS.

## LP-01 - God object en la raíz de composición

**Evidencia**: `app/gui_qt/main_window.py` concentra bootstrap, shell, controllers, plugin loading, servicios, UI y cierre.

**Boundary violado**: Kernel / Host shell / Products

**Impacto**: No existe ownership claro del lifecycle ni de la composición. El host se vuelve punto único de acoplamiento.

**Tratamiento target**: Rebuild. Repartir entre Forge Kernel bootstrap, host shell runtime, extension registry y product activators.

## LP-02 - Suscripción temprana rota del workspace

**Evidencia**: `ToolWorkspaceCoordinator` intenta suscribirse a `WORKSTATION_CONTEXT_CHANGED` antes de que `event_bus` exista en el orden real de arranque de `main_window.py`.

**Boundary violado**: Lifecycle / Eventing

**Impacto**: El runtime puede perder cambios de contexto o arrancar en estado inconsistente.

**Tratamiento target**: Delete/rebuild. Ninguna suscripción ocurre antes de `prepare`; el kernel gobierna el orden.

## LP-03 - Lifecycle incompleto de plugins en cierre

**Evidencia**: Existe `PluginManager.shutdown_all()` pero `closeEvent()` no lo invoca.

**Boundary violado**: Lifecycle / Teardown

**Impacto**: Riesgo de recursos vivos, subscriptions colgando y procesos huérfanos.

**Tratamiento target**: Rebuild. Dispose contractual y evidence log obligatorio.

## LP-04 - Contexto del host contaminado por semántica de producto

**Evidencia**: `WorkstationContext` incluye `hostname`, `tunnel_id`, `origin_expected`, `origin_observed`, `config_path`, `last_good_state`, etc.

**Boundary violado**: State ownership / Product isolation

**Impacto**: El host deja de ser domain-agnostic y asume un producto concreto.

**Tratamiento target**: Delete esos campos del kernel. Publicar solo contextos de producto por contrato.

## LP-05 - Heurísticas product-specific dentro del shell

**Evidencia**: `ShellGroupRuntime` mapea `graph -> cloudflare_guardian` y `run -> orchestrator_bridge`; `ToolCatalogService` infiere categorías e íconos por strings de producto.

**Boundary violado**: Host shell / Products

**Impacto**: El host decide comportamiento por nombre, no por contrato.

**Tratamiento target**: Delete. Reemplazar por contribution manifests y slot binding declarativo.

## LP-06 - Event bus string-based sin schema

**Evidencia**: `event_bus.py` usa publish/subscribe por strings libres.

**Boundary violado**: Contracts / Eventing

**Impacto**: No hay validación, versionado ni ownership fuerte del evento.

**Tratamiento target**: Rebuild como contract runtime con schemas y observabilidad.

## LP-07 - Command dispatcher string-based

**Evidencia**: `command_dispatcher.py` registra handlers por strings libres.

**Boundary violado**: Contracts / Commanding

**Impacto**: Commands ambiguos, sin timeout, sin ownership formal y con colisiones potenciales.

**Tratamiento target**: Rebuild con command contracts, envelope y timeout policy.

## LP-08 - Service locator global como API pública de facto

**Evidencia**: `services/service_container.py` expone lookup por string; plugins consumen `main_window`, controllers y otros internals.

**Boundary violado**: Dependency governance

**Impacto**: Acoplamiento oculto, reach-through y dependencia implícita del host.

**Tratamiento target**: Delete como surface pública. Reemplazar por capability broker y contratos de servicio.

## LP-09 - Bridge de contribuciones derivando IDs por strings

**Evidencia**: `shell/contribution_bridge.py` divide `contribution_id` y envuelve callbacks para routing.

**Boundary violado**: Contracts / Host integration

**Impacto**: Los IDs se vuelven contrato informal; alto riesgo de colisión y lógica oculta.

**Tratamiento target**: Rebuild con manifests de contribution y schemas fijos.

## LP-10 - Plugin manager mezclando producto, plugin, tool y compat legacy

**Evidencia**: `plugin_manager.py` soporta manifests y single-file `*_plugin.py`, expone aliases `get_all_tools`, `enable_tool` y tiene `_PRODUCT_PLUGIN_IDS` hard-coded.

**Boundary violado**: Packaging / Extension governance

**Impacto**: Semánticas mezcladas y compatibilidad backward sin gobernanza.

**Tratamiento target**: Delete legacy loader y aliases ambiguos. Definir paquetes claros: kernel, commons, products.

## LP-11 - State adapter de Cloudflare raspando el host

**Evidencia**: `plugins/cloudflare_guardian/state_adapter.py` usa `main_window`, `getattr`, `except Exception` y lee widgets/controllers del host.

**Boundary violado**: Product isolation / State authority

**Impacto**: Violación directa de boundaries; el producto existe pegado a las entrañas del host como hiedra eléctrica.

**Tratamiento target**: Delete outright. Reescribir con published context y service contracts.

## LP-12 - Persistencia fragmentada

**Evidencia**: `QSettings`, `.repo_analyzer_settings.json`, `bridge_config.json`, historial propio del bridge y artefactos de sesión coexisten sin autoridad común.

**Boundary violado**: State ownership / Packaging

**Impacto**: No hay fuente de verdad por dominio ni reglas unificadas de restore/migrate/purge.

**Tratamiento target**: Rebuild con state authority registry y scopes claros kernel/commons/product.

## LP-13 - Legacy compatibility shims dentro del runtime

**Evidencia**: `preview_controller.py` conserva `_legacy_graph_svg_candidate`; plugin manager mantiene loader legacy.

**Boundary violado**: Compatibility / Packaging

**Impacto**: El target hereda deuda opaca y rutas no gobernadas.

**Tratamiento target**: Delete salvo que exista requirement explícito de compatibilidad.

## LP-14 - Cierre tolerante al error pero opaco

**Evidencia**: Uso repetido de `except Exception` en host y productos, sin failure model uniforme.

**Boundary violado**: Failure isolation / Observability

**Impacto**: Las fallas se esconden o se degradan sin contrato ni evidencia suficiente.

**Tratamiento target**: Rebuild con error envelopes, diagnostics y stop-the-line rules.

## LP-15 - Pruebas que normalizan contaminación

**Evidencia**: Tests validan mapeos `graph -> cloudflare_guardian` y `run -> orchestrator_bridge`; otros tests fabrican `event_bus` en orden imposible y ocultan el bug real de arranque.

**Boundary violado**: Governance / Verification

**Impacto**: Los tests protegen el diseño incorrecto.

**Tratamiento target**: Delete or rewrite tests para validar boundaries target, no debt legacy.

## LP-16 - Dependencia masiva de `self.main`

**Evidencia**: Métricas observadas: `workspace_runtime.py` 148 ocurrencias, `preview_controller.py` 111, `toolbar_controller.py` 111, `search_controller.py` 102, `layout_manager.py` 100.

**Boundary violado**: Ownership / Modularity

**Impacto**: Las piezas parecen módulos, pero en realidad orbitan al host como lunas con deuda gravitacional.

**Tratamiento target**: Rebuild con handles acotados y contratos explícitos.

## LP-17 - String contracts y nombres como semántica primaria

**Evidencia**: IDs de tool, event, command y contribution cargan semántica y routing sin schema duro.

**Boundary violado**: Contracts / Governance

**Impacto**: Renombres rompen runtime; versionado y compatibilidad se vuelven adivinanza.

**Tratamiento target**: Rebuild con contract catalog, schemas y políticas de evolución.

## LP-18 - Bundle de trabajo sucio

**Evidencia**: Artefactos locales como `__pycache__`, `.pytest_cache` y `.repo_analyzer_settings.json` están presentes en evidencia.

**Boundary violado**: Packaging hygiene

**Impacto**: Empaquetado contaminado y reproducibilidad débil.

**Tratamiento target**: Delete. BOM e integrity gates obligatorios.
