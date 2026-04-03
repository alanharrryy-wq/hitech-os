# Executive Summary

La base del `shared/pyside6_glass` está bien separada por capas, pero trae varias grietas donde el contrato escrito promete más de lo que el runtime realmente amarra.

## Hallazgos centrales

- **La autorización actual en integración es débil por defecto**. El cliente puede declarar sus propias `capabilities`, y `IntegrationService` las toma como base para autorizar salvo que un consumidor externo inyecte un `access_hook`.
- **`state.save` y `state.load` exponen control de ruta desde el payload**. El bridge termina leyendo o escribiendo en filesystem con rutas aportadas por el caller.
- **Hay contratos descritos pero no realmente ejecutados**. `expected_version`, `idempotency_key`, `workspace_id`, `max_retries`, `jitter_ms`, y varias garantías documentales existen, pero varias están a medio amarre.
- **La observabilidad de fallos es parcial**. Los comandos emiten eventos de fallo, pero queries y snapshots no siempre dejan una traza equivalente. El backlog de eventos también puede truncarse sin una señal de pérdida.
- **El sistema normaliza entradas inválidas en vez de rechazarlas**. Estados desconocidos acaban como `visible` o `ready`, lo cual es cómodo para demo, pero peligroso para integridad operativa.

## Recomendación principal

No hace falta rediseñar el producto. La mejor jugada es **blindar la frontera de integración y endurecer la ejecución real de los contratos externos**, sin mover el corazón visual del framework.

## Orden recomendado

1. Cerrar spoofing de privilegios y rutas arbitrarias de persistencia.
2. Volver reales `expected_version`, idempotency, y trazabilidad de eventos.
3. Endurecer validación de estado externo/persistido e invariantes de paneles.
4. Mejorar persistencia, pruebas, packaging/documentación y claridad operativa.

## Enfoque

Este paquete deja los entregables en el formato previsto para vivir bajo:

```text
shared/docs/remediation/
```

La intención es que un pase de implementación pueda arrancar desde aquí sin tener que redescubrir el sistema desde cero.


---

# Inferred System Map for `shared/pyside6_glass`

## Purpose of the shared layer

`pyside6_glass` es un framework reusable de UI para apps estilo workstation en PySide6. No es lógica de producto. El paquete junta:

- contratos visuales y de configuración
- shell de workspace con tabs y panels
- runtime de preset/layout/persistencia
- catálogo y workbench demo
- subsistema neutral de data dashboards
- boundary de integración neutral para clientes externos
- release gate y prueba UX basada en sesiones doradas

## Major subsystems/modules

### 1. Framework core

Archivos clave:

- `contracts.py`
- `config.py`
- `theme.py`
- `icons.py`
- `template.py`
- `runtime.py`
- `diagnostics.py`
- `primitives.py`
- `assets.py`
- `controls.py`
- `charts.py`

Responsabilidad:

- tokens visuales
- dataclasses de configuración
- layout shell
- widgets y activos reusables
- aplicación de tema/densidad/tipografía
- snapshots de runtime

### 2. Catalog and workbench layer

Archivos clave:

- `catalog.py`
- `examples/catalog_shell.py`
- `examples/catalog_builtin.py`
- `examples/catalog_dashboard_entries.py`
- `examples/catalog_assets_entries.py`

Responsabilidad:

- registro de entradas
- browsing/search por categoría/tag
- preview/workspace launch
- composer/editor no destructivo
- clone/reset/save clone
- enforcement de budgets de paneles pesados y widgets live data

### 3. Data/dashboard subsystem

Archivos clave:

- `data.py`
- `data_providers.py`
- `dashboard.py`

Responsabilidad:

- contrato neutral de consultas y resultados
- registry de providers
- providers built-in in-memory y SQLite local
- surface reusable que renderiza métricas, tabla, feed, payload y diagnostics

### 4. Integration boundary

Archivos clave:

- `integration/contracts.py`
- `integration/service.py`
- `integration/adapters.py`
- `integration/runtime_bridge.py`
- `integration/reference_workspace.py`

Responsabilidad:

- envelopes de command/query/snapshot
- responses/errors/events estructurados
- registro y dispatch de endpoints
- polling de eventos
- adapter in-process
- adapter HTTP local
- bridge de runtime desktop hacia contratos neutrales

### 5. Persistence and serialization

Archivos clave:

- `persistence.py`
- `runtime.py`
- `template.py`

Responsabilidad:

- serializar workspace state v2
- migrar schema v1 -> v2
- guardar/cargar layout, tabs, panel states, preferencias visuales
- exportar y aplicar estado del workspace

### 6. Release proof / release gate

Archivos clave:

- `release_gate.py`
- `UX_RELEASE_PROOF.md`
- `SACRED_CAPABILITIES_CONTRACT.md`
- `ux_flight_recorder/*`
- `contracts/premium_capability_matrix_v1.json`
- `golden_sessions/golden_sessions_v1.json`

Responsabilidad:

- validar contrato de 40 blockers y 100 premium capabilities
- correr compile checks, tests críticos y proof runner
- generar evidencia JSON y bundles de proof

## Key contracts/types/schemas

### UI/runtime contracts

- `GlassTemplateConfig` y subconfigs en `config.py`
- `GlassResolvedConfig` con provenance por campo
- `GlassWorkspaceTabSpec` y `GlassPanelSpec` en `template.py`
- `GlassRuntimeContext`, `GlassVisibilityRule`, `GlassVisibilityPolicy` en `runtime.py`

### State and persistence contracts

- `GlassWorkspaceState` schema v2 en `persistence.py`

Payload principal:

- `layout`
- `selected_layout_preset`
- `tab_states`
- `tab_order`
- `active_tab_id`
- `panel_states`
- `panel_visibility`
- `theme_id`
- `density`
- `typography_scale`
- `metadata`

### Data contracts

- `RefreshPolicy`
- `DataQuery`
- `DataResult`
- `DataError`
- `DataProviderMeta`
- `DashboardDataProvider`

### Integration contracts

- `IntegrationEnvelopeMeta`
- `IntegrationClientContext`
- `IntegrationCommandEnvelope`
- `IntegrationQueryEnvelope`
- `IntegrationSnapshotRequest`
- `IntegrationResponse`
- `IntegrationError`
- `IntegrationEvent`

## Runtime boundaries and assumptions

- El core visual asume consumo **in-process y confiable**.
- La capa `integration` intenta abrir el runtime a clientes ligeros externos sin acoplar widgets directos.
- El workbench/examples funcionan como referencia operativa y también como superficie real de validación UX.
- Hay fuertes suposiciones de layout de repo:
  - varios docs, tests y scripts asumen ruta `forgeos/shared/pyside6_glass`
  - `release_gate.py` y `data_providers.py` derivan `REPO_ROOT` con `parents[3]`
  - varios defaults apuntan a `tools/_local/...`

## Trust model and security-relevant assumptions

### Trust model real observado

- No hay autenticación nativa en shared.
- No hay firma ni source-of-truth criptográfico para `capabilities`.
- `IntegrationService` confía en `context.capabilities` enviados por el cliente, salvo que un consumidor inyecte `access_hook`.
- `LocalHttpIntegrationAdapter` expone ese modelo sobre HTTP local.
- `workspace_id` existe en el contrato, pero el bridge no lo usa para target enforcement.
- `state.save` y `state.load` aceptan `path` desde el payload.

### Conclusión

El trust model real no es “authenticated external client”. Es más bien **trusted caller or consumer discipline**.

## Dispatch/sync/retry/idempotency mechanisms

### Dispatch

- `IntegrationService` registra commands, queries y snapshots con `IntegrationEndpointSpec`.
- Dispatch centralizado:
  - `dispatch_command`
  - `dispatch_query`
  - `dispatch_snapshot`

### Events

- Eventos guardados en `deque(maxlen=max_events)`.
- Polling por secuencia:
  - `poll_events(since_sequence, limit)`
- SSE solo de un frame en `LocalHttpIntegrationAdapter`.

### Idempotency

- Solo para commands.
- Key actual:
  - `client_id:command:idempotency_key`
- No incluye payload hash ni `expected_version`.
- Cache en memoria, no duradera, sin TTL semántico.

### Versioning / optimistic concurrency

- `expected_version` existe en `IntegrationCommandEnvelope`.
- Solo se valida si el servicio fue creado con `version_hook`.
- Los bridges y servicios de ejemplo no lo amarran por default.

### Retry

- `RefreshPolicy` declara `max_retries` y `jitter_ms`.
- Providers built-in devuelven policies con retry intent.
- `execute_data_query` no implementa loop de retry.
- `DashboardDataSurface` tampoco.

## Validation and enforcement model

### Lo que sí se valida

- presencia de nombres no vacíos en varios contracts
- shape de mappings/lists en algunos payloads
- version de protocolo soportada
- nombres de endpoint normalizados
- existencia de provider de data
- algunas entradas semánticas mínimas en handlers

### Lo que no se valida o se degrada silenciosamente

- autenticidad de `capabilities`
- target `workspace_id`
- version conflict si no hay `version_hook`
- estados desconocidos de panel/tab/data, que se normalizan a defaults (`visible` / `ready`)
- consistencia entre `panelState` y `visible`
- path safety para save/load de state
- retry semantics prometidas por `RefreshPolicy`

## Test landscape

Cobertura observada:

- 11 archivos de tests
- bastante foco en:
  - catálogo/workbench
  - estados de data
  - registry de providers
  - charts/controls/theme
  - release gate
  - ux flight recorder

Huecos claros:

- no hay suite dedicada para `integration/service.py`
- no hay suite dedicada para `integration/adapters.py`
- no hay suite dedicada para `integration/runtime_bridge.py`
- no hay suite dedicada para `persistence.py`

No se observó cobertura directa para:

- capability spoofing
- `expected_version` conflict
- idempotency payload mismatch
- event backlog overflow
- invalid `since/limit` HTTP parsing
- path restriction en `state.save`

## Documentation landscape

Docs disponibles y abundantes:

- `README.md`
- `ARCHITECTURE.md`
- `INTEGRATION.md`
- `DATA_DASHBOARD.md`
- `SACRED_CAPABILITIES_CONTRACT.md`
- `UX_RELEASE_PROOF.md`

### Fortaleza

La intención del sistema está bien explicada.

### Debilidad

En varios puntos los docs describen una postura más fuerte que la que runtime realmente garantiza, sobre todo en integración, retry y observabilidad.

## Known limitations and confidence notes

### Alta confianza

- trust gap en `integration`
- path write risk en `state.save`
- retry contract inerte
- fallback normalization permisiva
- huecos de pruebas en integration/persistence

### Confianza media

- severidad real de algunos riesgos depende de cómo consumidores externos monten `access_hook`, `version_hook` o si exponen HTTP local en producción
- el empaquetado `forgeos.shared...` vs `pyside6_glass` puede estar resuelto en el repo completo, pero dentro del zip sí aparece como dependencia fuerte de layout

### Limitaciones del análisis

- inspección estática del zip
- no se corrieron GUI tests ni release gate por falta de `PySide6` en este entorno
- el zip contiene `shared/`, no el repo completo, así que ciertos supuestos de repo-root no se pudieron validar en ejecución


---

# Risk-Prioritized Remediation Plan for `shared/pyside6_glass`

## Scope and non-goals

### Scope

- hardening de `integration`
- integridad de contratos runtime
- confiabilidad de dispatch/events/retry
- persistencia y serialización
- cobertura de pruebas y precisión documental
- UX/operator clarity solo donde afecta confianza o completitud

### Non-goals

- no rediseñar el producto
- no reescribir el framework visual
- no inventar nuevas features de negocio
- no reemplazar PySide6 ni el workbench
- no abrir nuevos transportes ni nuevos modos de cliente

## What was analyzed

Se inspeccionaron estáticamente:

- core framework modules
- integration boundary completa
- persistence/runtime/template state flow
- data subsystem
- release gate y UX proof
- docs top-level
- suite de tests
- artifacts versionados de UX proof

## Source of truth and evidence method

Fuente de verdad: el contenido real de `shared.zip`, usando el `.txt` subido como brief operativo autoritativo.

Método:

- lectura estructural de módulos y exports
- comparación docs vs runtime
- lectura de tests para detectar lo realmente cubierto
- rastreo de flujos:
  - inbound contract -> service -> bridge/runtime/template
  - provider -> execute_data_query -> dashboard surface
  - export/apply workspace state
  - release_gate -> proof runner -> artifacts

## Reconstructed current-state summary

El paquete está bien separado por capas y tiene un kernel reusable bastante ordenado. El problema no es arquitectura gruesa. El problema está en que **las fronteras externas más sensibles son demasiado permisivas**, y varias garantías viven más en el contrato escrito que en el enforcement real.

## Risk framing assumptions

### Hechos

- `LocalHttpIntegrationAdapter` existe y despacha directo a `IntegrationService`.
- write endpoints pueden quedar protegidos solo por `required_capabilities`.
- `capabilities` vienen del payload del cliente.
- `state.save` acepta `path` desde el payload.
- `expected_version` no sirve si nadie enchufa `version_hook`.
- `RefreshPolicy.max_retries` y `jitter_ms` no se usan para retry real.

### Supuestos

- shared puede ser consumido por apps internas con distintos niveles de disciplina.
- no conviene asumir que todos los consumers van a meter hooks correctos.
- el boundary debe ser seguro por default, no solo “si el integrador se porta bien”.

### Apuestas

- si el HTTP adapter jamás se expone fuera de procesos totalmente confiables, baja blast radius de P0, pero no desaparece el gap de diseño
- si ya existe un consumer externo con `access_hook/version_hook`, parte de P1 puede bajar de urgencia en ese consumer, pero no en el shared layer

## Priority summary table

| Priority | Count | Theme |
|---|---:|---|
| P0 | 2 | trust boundary rota y write surface peligrosa |
| P1 | 6 | concurrencia, eventos, contrato-runtime mismatch, retry, workspace targeting |
| P2 | 4 | persistencia durable, pruebas, packaging/path assumptions, docs accuracy |
| P3 | 1 | polish operacional menor |

## Detailed backlog by P0

### SHARED-REM-P0-01 | Replace caller-asserted capabilities with trusted authorization input

- **Category:** Security / trust model
- **Why it exists:** `IntegrationService` toma decisiones de acceso con `context.has_capabilities(...)`, pero `context.capabilities` viene del payload del cliente.
- **Current behavior:** un cliente puede mandar `{"capabilities": ["workspace.write"]}` y pasar la primera capa de autorización. `create_reference_workspace_service()` no inyecta `access_hook`, y `examples/integration_demo.py` demuestra exactamente este patrón.
- **Risk / impact:** spoofing de privilegios para commands write sobre runtime/reference workspace. En combinación con HTTP local, cualquier caller local puede mutar estado si conoce el endpoint.
- **Recommended remediation:** mover el source of truth de authorization fuera del payload. El shared layer debe:
  - ignorar `context.capabilities` para decisiones de acceso por default, o
  - tratarlas como hints no confiables hasta que un `access_hook`/resolver confiable las confirme.
- **Concrete scope boundaries:** solo `integration/contracts.py`, `integration/service.py`, `integration/reference_workspace.py`, `integration/runtime_bridge.py`, `examples/integration_demo.py`, docs de integración.
- **Acceptance criteria:**
  - un payload no puede autoescalar permisos solo por declarar capabilities
  - write endpoints fallan por default sin source de autorización confiable
  - la policy de trusted caller queda documentada de forma explícita
  - existe test que pruebe capability spoofing denial
- **Dependencies:** definición explícita del threat model para callers locales
- **Tradeoffs:** un poco más de fricción para demos rápidos; a cambio se quita una ilusión de seguridad que ahorita está bien tramposa
- **Unknowns:** no se puede confirmar desde el zip si algún app consumer ya mete un `access_hook` fuerte
- **Quick wins:** hacer que `IntegrationService` requiera `access_hook` para cualquier endpoint con `required_capabilities`
- **Suggested owner type:** framework/integration owner
- **Likely affected modules/files/surfaces:** `integration/contracts.py`, `integration/service.py`, `integration/reference_workspace.py`, `integration/runtime_bridge.py`, `examples/integration_demo.py`, `INTEGRATION.md`
- **Classification:** remediation required now

### SHARED-REM-P0-02 | Remove arbitrary filesystem path control from integration state persistence commands

- **Category:** Security / trust model
- **Why it exists:** `workspace.state.save` y `workspace.state.load` aceptan `path` desde `IntegrationCommandEnvelope.payload`.
- **Current behavior:** `_command_save_state()` pasa `path` a `GlassWorkspaceRuntime.save_workspace_state()`, que lo convierte en `Path(path)` y `persistence.save_workspace_state()` crea directorios y escribe el JSON directo.
- **Risk / impact:** primitive de escritura arbitraria dentro del scope de permisos del proceso. Aunque sea local-only, sigue siendo una write surface fea.
- **Recommended remediation:** eliminar el `path` libre del contrato externo. Permitir solo:
  - ruta configurada interna, o
  - rutas bajo una allowlist/root configurado, validadas y canonicalizadas.
- **Concrete scope boundaries:** `integration/runtime_bridge.py`, `runtime.py`, `persistence.py`, docs y tests de integración.
- **Acceptance criteria:**
  - `state.save` no acepta rutas arbitrarias
  - cualquier override de path queda restringido a un root seguro y auditado
  - rutas fuera de política fallan con error estructurado
  - test de path traversal / out-of-root denial
- **Dependencies:** definición del storage root permitido
- **Tradeoffs:** se sacrifica flexibilidad de tooling ad hoc, pero se elimina una superficie de daño bien innecesaria
- **Unknowns:** si existe tooling legítimo que dependa de `path` libre
- **Quick wins:** desactivar ya el payload `path` en el bridge y usar solo `config.persistence.storage_path`
- **Suggested owner type:** integration/runtime owner
- **Likely affected modules/files/surfaces:** `integration/runtime_bridge.py`, `runtime.py`, `persistence.py`, `README.md`, `INTEGRATION.md`
- **Classification:** remediation required now

## Detailed backlog by P1

### SHARED-REM-P1-01 | Make `expected_version` and idempotency semantics real

- **Category:** Contracts / runtime behavior
- **Why it exists:** el contrato ofrece `expected_version` e `idempotency_key`, pero la implementación real es parcial.
- **Current behavior:** `expected_version` solo se chequea si existe `version_hook`. Los servicios/bridges por default no lo usan. La deduplicación solo usa `client_id:command:idempotency_key`, sin amarrarse al payload.
- **Risk / impact:** lost updates, replay ambiguo, dedupe falsa para payloads distintos con la misma key, contrato optimista engañoso.
- **Recommended remediation:**
  - exigir versión actual para endpoints mutantes donde importa integridad
  - ligar idempotency a fingerprint de payload semántico y endpoint
  - documentar cuándo aplica idempotency y cuándo no
- **Concrete scope boundaries:** `integration/service.py`, `integration/contracts.py`, `integration/reference_workspace.py`, `integration/runtime_bridge.py`
- **Acceptance criteria:**
  - write endpoints críticos rechazan `expected_version` conflict con 409 verificable
  - misma key + payload distinto no reutiliza response vieja
  - existe test de conflict, dedupe válida y dedupe inválida
- **Dependencies:** decisión de qué entidad/version se usa por endpoint
- **Tradeoffs:** más complejidad de contrato; muchísimo mejor integridad
- **Unknowns:** cuáles consumers realmente necesitan optimistic concurrency ya
- **Quick wins:** empezar por `reference_workspace` y runtime state-changing commands
- **Suggested owner type:** integration owner
- **Likely affected modules/files/surfaces:** `integration/service.py`, `integration/reference_workspace.py`, `integration/runtime_bridge.py`
- **Classification:** remediation required now

### SHARED-REM-P1-02 | Close event reliability and failure-observability gaps

- **Category:** Sync / dispatch / reliability hardening
- **Why it exists:** el sistema emite eventos, pero no garantiza trazabilidad completa ni detección de pérdida.
- **Current behavior:**
  - `deque(maxlen=500)` puede truncar backlog sin marker
  - `dispatch_query` y `dispatch_snapshot` no emiten eventos de fallo
  - parseo de `since` y `limit` en HTTP GET puede explotar con `ValueError`
- **Risk / impact:** clientes creen tener timeline completo y no lo tienen; debugging y replay se ponen turbios; polling puede fallar feo por input malo.
- **Recommended remediation:**
  - emitir failure events también para query/snapshot
  - introducir señal de overflow/gap de backlog
  - validar query params HTTP y responder 400 estructurado
- **Concrete scope boundaries:** `integration/service.py`, `integration/adapters.py`, docs
- **Acceptance criteria:**
  - todos los fallos de dispatch relevantes dejan traza estructurada
  - pollers pueden detectar cuando perdieron eventos por truncado
  - `/v1/events` y `/v1/events/stream` responden 400 para `since/limit` inválidos
- **Dependencies:** ninguna dura
- **Tradeoffs:** un poquito más de ruido en eventos; mucha mejor operabilidad
- **Unknowns:** si algún consumer depende del silencio actual para queries fallidas
- **Quick wins:** validar `since/limit` y emitir failure events primero
- **Suggested owner type:** integration/ops owner
- **Likely affected modules/files/surfaces:** `integration/service.py`, `integration/adapters.py`, `INTEGRATION.md`
- **Classification:** remediation required now

### SHARED-REM-P1-03 | Replace silent fallback normalization on external and persisted state

- **Category:** Contracts / runtime behavior
- **Why it exists:** estados inválidos o desconocidos se degradan a defaults seguros para render, pero inseguros para integridad.
- **Current behavior:**
  - `DataState.normalize("UNKNOWN") -> ready`
  - tab/panel states inválidos -> `visible`
  - `GlassWorkspaceState.from_payload()` preserva strings arbitrarias y luego el template las normaliza silenciosamente
  - tests incluso fijan este comportamiento
- **Risk / impact:** payloads corruptos o consumidores equivocados producen UI activa en vez de error explícito; se ocultan bugs de integración y drift de schema.
- **Recommended remediation:**
  - distinguir inputs internos tolerantes vs inputs externos/persistidos estrictos
  - validar y rechazar states inválidos en boundary/persistence restore
  - conservar compatibilidad interna solo donde se justifique
- **Concrete scope boundaries:** `data.py`, `template.py`, `persistence.py`, tests relacionados
- **Acceptance criteria:**
  - restore/load y endpoints externos no aceptan states desconocidos sin error explícito
  - se documenta qué inputs son strict y cuáles lenient
  - tests se actualizan para reflejar enforcement real
- **Dependencies:** decisión de compatibilidad hacia atrás para payloads ya guardados
- **Tradeoffs:** pueden aflorar errores antes ocultos; eso está bien
- **Unknowns:** cuántos snapshots viejos dependen del fallback
- **Quick wins:** strict validation en persistence restore y integration commands primero
- **Suggested owner type:** framework contract owner
- **Likely affected modules/files/surfaces:** `data.py`, `template.py`, `persistence.py`, `tests/test_data_result_states.py`
- **Classification:** remediation required now

### SHARED-REM-P1-04 | Unify panel state and visibility invariants

- **Category:** Contracts / runtime behavior
- **Why it exists:** panel state y visible son dos fuentes de verdad separadas sin invariant fuerte.
- **Current behavior:**
  - `set_panel_state("hidden")` puede luego quedar visible si alguien llama `set_panel_visible(True)`
  - `export_workspace_state()` persiste ambos
  - `apply_workspace_state()` aplica primero state y luego visible, pudiendo reactivar estados lógicamente ocultos
- **Risk / impact:** snapshots inconsistentes, comportamiento sorprendente para integradores, traces difíciles de explicar a operador.
- **Recommended remediation:** definir invariant explícito:
  - o `panelState` manda sobre `visible`
  - o `visible` deja de ser contrato público independiente y se deriva
- **Concrete scope boundaries:** `template.py`, `runtime_bridge.py`, persistence docs/tests
- **Acceptance criteria:**
  - existe una sola regla canónica para panel hidden/collapsed/deferred/background/hold
  - export/apply state preserva esa regla sin contradicciones
  - tests cubren combinaciones conflictivas
- **Dependencies:** definición de semantic model para hidden/collapsed/background/hold
- **Tradeoffs:** algo de compatibilidad con snapshots raros puede romperse
- **Unknowns:** si algún consumer usa visibilidad independiente adrede
- **Quick wins:** impedir `panel.visibility.set(true)` cuando el state actual sea `hidden` o `collapsed`
- **Suggested owner type:** framework/runtime owner
- **Likely affected modules/files/surfaces:** `template.py`, `integration/runtime_bridge.py`, `persistence.py`
- **Classification:** remediation required now

### SHARED-REM-P1-05 | Implement actual retry semantics or remove misleading retry fields from public flow

- **Category:** Sync / dispatch / reliability hardening
- **Why it exists:** `RefreshPolicy` y algunos providers anuncian retry intent, pero el runtime no lo ejecuta.
- **Current behavior:** `execute_data_query()` llama una sola vez al provider. `DashboardDataSurface.reload()` también.
- **Risk / impact:** transient failures no reciben el tratamiento que el contrato sugiere; docs y diagnostics pueden inducir confianza falsa.
- **Recommended remediation:** elegir una sola ruta:
  - implementar retry real con backoff/jitter para errores retryable, o
  - retirar `max_retries/jitter_ms` de la superficie pública hasta que exista enforcement
- **Concrete scope boundaries:** `data.py`, `dashboard.py`, `data_providers.py`, `DATA_DASHBOARD.md`
- **Acceptance criteria:**
  - retry behavior está implementado y probado, o
  - los campos no implementados dejan de formar parte de la promesa pública
- **Dependencies:** decisión de si retry vive en engine o en widget layer
- **Tradeoffs:** implementar retry sube complejidad; eliminar la promesa reduce ambición pero sube honestidad
- **Unknowns:** si algún consumer externo ya interpreta esos campos
- **Quick wins:** documentar que hoy son metadata no ejecutada, y luego decidir enforcement
- **Suggested owner type:** data/dashboard owner
- **Likely affected modules/files/surfaces:** `data.py`, `dashboard.py`, `data_providers.py`, `DATA_DASHBOARD.md`
- **Classification:** hardening next

### SHARED-REM-P1-06 | Enforce workspace targeting semantics instead of echoing `workspace_id`

- **Category:** Contracts / runtime behavior
- **Why it exists:** `workspace_id` aparece en el contrato, pero no decide nada.
- **Current behavior:** runtime bridge lo devuelve en diagnostics, pero commands/snapshots no validan target. Reference workspace tampoco amarra mutaciones al `workspace_id`.
- **Risk / impact:** contrato engañoso en escenarios multi-workspace; riesgo de aplicar mutaciones al runtime equivocado.
- **Recommended remediation:** definir y ejecutar semántica:
  - target validation estricta, o
  - remover `workspace_id` del contrato público donde no aplique
- **Concrete scope boundaries:** `integration/contracts.py`, `integration/runtime_bridge.py`, `integration/reference_workspace.py`, docs
- **Acceptance criteria:**
  - `workspace_id` tiene semántica ejecutable y testeada, o sale del contrato
  - mismatch produce error estructurado si se mantiene
- **Dependencies:** decisión de soporte multi-workspace real
- **Tradeoffs:** añadir targeting correcto mete algo de complejidad, pero elimina ambigüedad
- **Unknowns:** si consumers externos ya envían `workspace_id` esperando enforcement
- **Quick wins:** validar mismatch en `reference_workspace` primero
- **Suggested owner type:** integration owner
- **Likely affected modules/files/surfaces:** `integration/contracts.py`, `integration/runtime_bridge.py`, `integration/reference_workspace.py`, `INTEGRATION.md`
- **Classification:** hardening next

## Detailed backlog by P2

### SHARED-REM-P2-01 | Make workspace persistence durable and diagnosable

- **Category:** Operational reliability / UX-operator clarity
- **Why it exists:** la persistencia actual privilegia simplicidad sobre durabilidad y diagnóstico.
- **Current behavior:** save directo con `write_text`; load devuelve `None` ante cualquier error; `state.load` solo responde `loaded: bool`.
- **Risk / impact:** pérdida silenciosa de estado, poca capacidad de distinguir “archivo no existe” de “JSON corrupto” o “schema inválido”.
- **Recommended remediation:**
  - write atómico con temp file + replace
  - códigos de error diferenciados para load/save
  - diagnostics mínimos de causa
- **Concrete scope boundaries:** `persistence.py`, `runtime.py`, `integration/runtime_bridge.py`
- **Acceptance criteria:**
  - save no deja archivos parciales ante fallo
  - load expone causa estructurada de error
  - tests cubren archivo ausente, corrupto y schema inválido
- **Dependencies:** ninguna dura
- **Tradeoffs:** un poco más de plumbing; mejor resiliencia
- **Unknowns:** requirements de compatibilidad con tooling existente
- **Quick wins:** distinguir missing/corrupt/invalid en `load_workspace_state`
- **Suggested owner type:** runtime owner
- **Likely affected modules/files/surfaces:** `persistence.py`, `runtime.py`, `integration/runtime_bridge.py`
- **Classification:** hardening next

### SHARED-REM-P2-02 | Add direct automated coverage for integration and persistence boundaries

- **Category:** Testing gaps
- **Why it exists:** los puntos más sensibles del sistema son justo los menos cubiertos.
- **Current behavior:** tests cubren workbench/data/theme/release proof, pero no hay suite dedicada para service/adapters/runtime_bridge/persistence security cases.
- **Risk / impact:** regresiones graves en trust boundary pueden entrar limpias aunque el resto del framework siga verde.
- **Recommended remediation:** crear suites específicas para:
  - access spoofing denial
  - write path restriction
  - version conflict
  - idempotency collision mismatch
  - event overflow signaling
  - invalid HTTP query params
  - corrupt workspace state load
- **Concrete scope boundaries:** carpeta `tests/`
- **Acceptance criteria:**
  - existen tests directos por cada failure mode crítico
  - release gate incluye al menos los nuevos tests de integration/persistence
- **Dependencies:** estabilizar contratos P0/P1 primero
- **Tradeoffs:** más tiempo de suite; mucha menor probabilidad de regresión
- **Unknowns:** disponibilidad de `PySide6` en CI completa
- **Quick wins:** tests puros de `IntegrationService` y `persistence.py` no necesitan GUI
- **Suggested owner type:** QA/automation + framework owner
- **Likely affected modules/files/surfaces:** `tests/`, `release_gate.py`
- **Classification:** hardening next

### SHARED-REM-P2-03 | Resolve packaging and repo-layout assumptions

- **Category:** Contracts / documentation accuracy
- **Why it exists:** el código y docs mezclan identidad standalone (`pyside6_glass`) con identidad repo (`forgeos.shared.pyside6_glass`) y rutas `tools/_local`.
- **Current behavior:** docs, tests y release gate dependen de `forgeos/shared/...`; `pyproject.toml` empaqueta `pyside6_glass` standalone; `data_providers.py` y `release_gate.py` dependen de `parents[3]`.
- **Risk / impact:** integración portable frágil, scripts que fallan fuera del repo esperado, onboarding confuso.
- **Recommended remediation:** declarar oficialmente un solo modelo soportado o dos modos explícitos:
  - repo-integrated
  - standalone package
  con reglas distintas para paths, imports y tooling.
- **Concrete scope boundaries:** `pyproject.toml`, `README.md`, `release_gate.py`, `data_providers.py`, tests/import docs
- **Acceptance criteria:**
  - packaging/import model queda inequívoco
  - defaults de path se vuelven configurables o claramente repo-only
  - docs y tests no prometen un modo que el código no soporte
- **Dependencies:** decisión de distribución real del paquete
- **Tradeoffs:** limpiar esto da hueva, pero evita una bola de soporte tonto
- **Unknowns:** el repo completo quizá ya resuelve parte de esto
- **Quick wins:** etiquetar explícitamente `release_gate.py` y `default_local_dashboard_db_path()` como repo-root dependent
- **Suggested owner type:** platform/package owner
- **Likely affected modules/files/surfaces:** `pyproject.toml`, `release_gate.py`, `data_providers.py`, `README.md`, tests imports
- **Classification:** hardening next

### SHARED-REM-P2-04 | Align docs with runtime truth

- **Category:** Documentation gaps
- **Why it exists:** la documentación es sólida, pero en algunos puntos promete más de lo que runtime garantiza.
- **Current behavior:**
  - integración parece más segura de lo que es
  - retry parece operativo cuando hoy es metadata
  - diagnostics sugieren inspección completa, pero no todos los fallos emiten eventos
- **Risk / impact:** integradores y operadores toman malas decisiones por documentación optimista.
- **Recommended remediation:** actualizar docs para reflejar:
  - trust model actual
  - requirement de hooks confiables
  - semántica real de retry
  - límites de event backlog
  - enforcement real de `workspace_id` y `expected_version`
- **Concrete scope boundaries:** `README.md`, `INTEGRATION.md`, `DATA_DASHBOARD.md`, `ARCHITECTURE.md`
- **Acceptance criteria:**
  - ningún claim de seguridad/confiabilidad excede lo que el código hace
  - threat model queda escrito
  - se distinguen claramente garantías actuales vs preparadas/scaffolded
- **Dependencies:** cerrar al menos P0 y decidir P1
- **Tradeoffs:** docs menos “premium sounding”, pero mucho más honestas
- **Unknowns:** ninguna relevante
- **Quick wins:** nota explícita “client-provided capabilities are not trusted authorization by themselves”
- **Suggested owner type:** framework/docs owner
- **Likely affected modules/files/surfaces:** `README.md`, `INTEGRATION.md`, `DATA_DASHBOARD.md`, `ARCHITECTURE.md`
- **Classification:** hardening next

## Detailed backlog by P3

### SHARED-REM-P3-01 | Improve operator-facing error language around persistence and integration diagnostics

- **Category:** UX / operator polish
- **Why it exists:** algunos surfaces devuelven bools o mensajes demasiado secos para troubleshooting humano.
- **Current behavior:** `loaded: bool`, errores genéricos, poco contexto accionable en save/load y en ciertos diagnostics payloads.
- **Risk / impact:** soporte más lento, revisión menos clara, debugging manual más tardado.
- **Recommended remediation:** enriquecer mensajes y diagnostics payloads solo donde afectan trust/completion.
- **Concrete scope boundaries:** `integration/runtime_bridge.py`, `dashboard.py`, docs menores
- **Acceptance criteria:**
  - save/load failures incluyen reason code y siguiente señal a revisar
  - payloads de diagnostics distinguen missing/corrupt/denied/conflict/invalid
- **Dependencies:** P2-01
- **Tradeoffs:** payloads un poco más verbosos
- **Unknowns:** ninguna relevante
- **Quick wins:** reason codes consistentes
- **Suggested owner type:** operator UX + runtime owner
- **Likely affected modules/files/surfaces:** `integration/runtime_bridge.py`, `dashboard.py`
- **Classification:** defer


---

# Remediation Sequence

## Sequencing principles

1. Primero cerrar las superficies donde un caller no confiable puede causar daño real.
2. Luego corregir contratos mutantes e invariantes para que el runtime deje de “adivinar bonito”.
3. Después endurecer observabilidad, persistencia y pruebas.
4. Al final, alinear docs y packaging con la verdad ya estabilizada.

## Recommended execution waves

| Wave | Work | Why now |
|---|---|---|
| Wave 0 | decidir threat model, auth source, storage root policy, version authority | evita rework bruto |
| Wave 1 | P0-01, P0-02 | cierra la fuga más fea primero |
| Wave 2 | P1-01, P1-02, P1-03 | arregla integridad de contrato, eventos y validación |
| Wave 3 | P1-04, P1-05, P1-06, P2-01 | consolida semántica de state/retry/workspace y persistencia |
| Wave 4 | P2-02, P2-03, P2-04 | tests, packaging y docs ya sobre contrato estable |
| Wave 5 | P3-01 | polish final |

## Why this order is safer than alternative orders

Porque si empiezas por docs, tests o retry antes de amarrar trust boundary e invariantes, te llevas rework gratis y además puedes congelar comportamiento inseguro en pruebas nuevas. Primero se limpia lo que puede mentir o dañar. Luego ya haces confiable lo demás.

## Dependency chain

- **P0-01** depende de definir si `access_hook` será obligatorio o si habrá un resolver interno de identidad/capabilities.
- **P0-02** depende de definir storage root permitido.
- **P1-01** depende de definir qué representa “version” por endpoint mutante.
- **P1-03** depende de decidir qué payloads viejos se migran y cuáles se rechazan.
- **P1-04** depende de definir la semántica oficial entre `panelState` y `visible`.
- **P2-02** no debe cerrarse hasta saber si el paquete vive como `forgeos.shared...`, standalone, o ambos.
- **P2-04** no debe publicarse hasta que P0/P1 ya estén decididos.

## What must be decided before implementation begins

1. ¿El adapter HTTP local debe asumir callers locales no confiables o confiables?
2. ¿Qué root de filesystem está permitido para persistencia externa?
3. ¿Qué entidad/version se usa para `expected_version`?
4. ¿`workspace_id` será enforcement real o solo metadata?
5. ¿Retry vive en `execute_data_query()` o fuera del shared layer?
6. ¿`panelState` manda sobre `visible` o se elimina la dualidad?

## What can be parallelized

### Se puede paralelizar después de Wave 1

- diseño de tests directos de integration/persistence
- draft de docs corregidas
- refactor de packaging/path assumptions
- trabajo de operator diagnostics

### Se puede paralelizar dentro de Wave 3

- retry semantics
- persistencia durable
- workspace targeting

## What must not begin before P0 items are resolved

- ampliar exposición del HTTP adapter
- documentar integración como “estable y segura”
- agregar más tooling que dependa de `state.save(path=...)`
- congelar suites de regression para contratos aún inseguros

## Explicit answers

### What should happen first?

Cerrar **capability spoofing** y **arbitrary path write**.

### What can happen in parallel?

Una vez cerrados P0:

- tests de integration/persistence
- diseño de versioning/idempotency
- corrección documental

### What should wait?

Packaging/docs finales y polish de operator UX.

### What creates rework if done too early?

- tests de contrato antes de decidir trust model
- docs definitivas antes de fijar semántica de retry/workspace/state
- cualquier refactor de packaging sin decidir modo soportado


---

# Acceptance Checklist

## Ready to start criteria

- [ ] El threat model de integración quedó escrito
- [ ] Existe decisión sobre source of truth de autorización
- [ ] Existe decisión sobre root seguro de persistencia
- [ ] Existe decisión sobre semántica de `expected_version`
- [ ] Existe decisión sobre invariantes `panelState` vs `visible`
- [ ] Se identificaron consumers conocidos del HTTP adapter y de save/load state

## Checklist by remediation block

### P0-01 | Trusted authorization input
- [ ] `required_capabilities` ya no dependen de claims no confiables del payload
- [ ] write endpoints fallan por default sin autorización confiable
- [ ] existe test de capability spoofing denial
- [ ] docs de integración explican el trust model real

### P0-02 | Safe persistence path handling
- [ ] `state.save` ya no acepta ruta arbitraria sin validación
- [ ] `state.load` ya no acepta ruta arbitraria fuera de policy
- [ ] rutas fuera de root permitido regresan error estructurado
- [ ] existe test de out-of-root denial

### P1-01 | Version and idempotency integrity
- [ ] `expected_version` produce 409 real cuando hay conflict
- [ ] dedupe incluye fingerprint de payload o semántica equivalente
- [ ] existe test de same key + different payload
- [ ] reference workspace o runtime bridge tienen version authority definida

### P1-02 | Event reliability
- [ ] query failures emiten eventos o diagnostics equivalentes
- [ ] snapshot failures emiten eventos o diagnostics equivalentes
- [ ] overflow/gap de backlog es detectable por cliente
- [ ] `since/limit` inválidos responden 400, no excepción cruda

### P1-03 | Strict validation on external/persisted state
- [ ] states inválidos externos ya no se normalizan silenciosamente
- [ ] restore de workspace distingue payload inválido
- [ ] tests viejos que fijaban fallback fueron actualizados o segmentados
- [ ] docs separan claramente lenient vs strict inputs

### P1-04 | Panel invariants
- [ ] existe regla única para hidden/collapsed/background/hold/deferred
- [ ] export/apply workspace state preserva la regla
- [ ] `panel.visibility.set` no contradice `panelState`
- [ ] existe test de combinaciones conflictivas

### P1-05 | Retry truthfulness
- [ ] retry está implementado de verdad o eliminado de la promesa pública
- [ ] `max_retries` y `jitter_ms` no quedan como decoración engañosa
- [ ] existe test de transient retry path o docs aclarando ausencia

### P1-06 | Workspace targeting
- [ ] `workspace_id` tiene enforcement real o fue removido del contrato
- [ ] mismatch produce error claro si aplica
- [ ] docs no dejan ambigüedad sobre target semantics

### P2-01 | Durable persistence
- [ ] save usa escritura atómica
- [ ] load distingue missing/corrupt/invalid
- [ ] runtime bridge devuelve reason codes útiles
- [ ] existe test de corrupción de archivo

### P2-02 | Integration and persistence tests
- [ ] existe suite dedicada para `integration/service.py`
- [ ] existe suite dedicada para `integration/adapters.py`
- [ ] existe suite dedicada para `integration/runtime_bridge.py`
- [ ] existe suite dedicada para `persistence.py`
- [ ] release gate incluye coverage nueva crítica

### P2-03 | Packaging and path assumptions
- [ ] modo soportado de packaging quedó declarado
- [ ] defaults repo-root dependent quedaron marcados o abstraídos
- [ ] docs/examples/tests usan import/path model consistente

### P2-04 | Documentation alignment
- [ ] docs no sobreprometen seguridad
- [ ] docs no sobreprometen retry
- [ ] docs no sobreprometen observabilidad total
- [ ] threat model quedó visible para integradores

### P3-01 | Operator clarity
- [ ] errores de save/load incluyen causa útil
- [ ] diagnostics payloads son accionables para operador
- [ ] mensajes distinguen denial/conflict/invalid/corrupt

## Done criteria

- [ ] P0 completo y verificado
- [ ] P1 completo sin contradicción documental
- [ ] P2 suficiente para que regression crítica quede cubierta
- [ ] no hay contrato público importante cuya semántica siga siendo aspiracional
- [ ] release gate y docs ya reflejan la verdad del sistema

## Validation / rollout notes

- Primero validar in-process.
- Luego validar HTTP local.
- Solo después actualizar docs como “estable”.
- No promover consumers externos sobre `integration` hasta cerrar P0 y mínimo P1-01/P1-02.


---

# Gap to Evidence Map

| Finding / gap | Evidence from uploaded zip | Affected module(s) / surface(s) | Likely file / type / runtime touchpoints | Confidence | Contradictions / ambiguity notes |
|---|---|---|---|---|---|
| Caller can self-assert capabilities | `IntegrationClientContext.from_payload()` carga `capabilities` del payload; `IntegrationService._check_access()` usa `context.has_capabilities(...)`; `examples/integration_demo.py` manda `["workspace.write"]` desde el cliente | integration trust boundary | `integration/contracts.py`, `integration/service.py`, `examples/integration_demo.py` | Alta | Si un consumer externo mete `access_hook`, baja blast radius, pero el shared layer sigue permisivo por default |
| Arbitrary save path through integration | `GlassRuntimeIntegrationBridge._command_save_state()` pasa `payload["path"]` a `runtime.save_workspace_state()` y `persistence.save_workspace_state()` escribe directo al path | integration + persistence | `integration/runtime_bridge.py`, `runtime.py`, `persistence.py` | Alta | `state.load` también acepta `path`, aunque no exfiltra contenido directamente |
| `expected_version` exists but is optional-noop | `IntegrationCommandEnvelope.expected_version`; `_check_expected_version()` retorna `None` si no hay `version_hook`; bridges por default usan `IntegrationService()` sin hook | command integrity | `integration/contracts.py`, `integration/service.py`, `integration/runtime_bridge.py`, `integration/reference_workspace.py` | Alta | Puede haber consumers externos con hook real, no visibles aquí |
| Idempotency can dedupe wrong payload | key construida con `client_id:command:idempotency_key`, sin payload fingerprint | command dedupe | `integration/service.py` | Alta | No se observó documentación que restrinja reuse de key por payload |
| Event backlog can drop history silently | `deque(maxlen=max_events)` + `poll_events()` sin señal de overflow/gap | event consistency | `integration/service.py` | Alta | Solo pega si los consumers dependen de historia completa |
| Query/snapshot failures are not inspectable like command failures | command failures emiten `integration.command.failed`; query/snapshot failures regresan failure sin `emit_event()` | observability | `integration/service.py` | Alta | Los docs hablan de diagnostics inspectables más fuertes que esto |
| Invalid HTTP query params can crash request path | `int(since_values[0])` y `int(limit_values[0])` sin guard en adapter HTTP | adapter reliability | `integration/adapters.py` | Alta | Local-only reduce severidad, no corrige bug |
| Invalid states normalize to active defaults | `_normalize_tab_state() -> "visible"`, `_normalize_panel_state() -> "visible"`, `DataState.normalize(..., default=READY)`; test fija `UNKNOWN_STATE -> READY` | contract enforcement | `template.py`, `data.py`, `tests/test_data_result_states.py` | Alta | Útil para demos, mala señal para inputs externos |
| Panel state and visibility can diverge | `set_panel_state()` y `set_panel_visible()` son independientes; `export_workspace_state()` guarda ambos; `apply_workspace_state()` aplica ambos | workspace state integrity | `template.py`, `persistence.py`, `integration/runtime_bridge.py` | Alta | Quizá es intencional para editor/workbench, pero no está especificado como invariant |
| Retry contract is metadata only | `RefreshPolicy` tiene `max_retries/jitter_ms`; providers los llenan; `execute_data_query()` hace un solo intento | data reliability | `data.py`, `data_providers.py`, `dashboard.py` | Alta | Los docs no dejan clarísimo que retry no existe realmente |
| `workspace_id` is descriptive, not enforced | el contrato lo incluye; runtime bridge solo lo ecoa en diagnostics; commands no lo usan | target semantics | `integration/contracts.py`, `integration/runtime_bridge.py`, `integration/reference_workspace.py` | Alta | Si el sistema es siempre single-runtime, severidad baja, pero el contrato sigue ambiguo |
| Persistence hides error cause | `load_workspace_state()` devuelve `None` en missing/parse/non-mapping; bridge devuelve solo `loaded` | operator clarity | `persistence.py`, `runtime.py`, `integration/runtime_bridge.py` | Alta | No es contradicción, pero sí poca visibilidad |
| Repo/layout assumptions are strong | docs/tests usan `forgeos.shared...`; `release_gate.py` y `data_providers.py` usan `parents[3]` y `tools/_local` | packaging / operability | `README.md`, `release_gate.py`, `data_providers.py`, tests | Media | El repo completo podría satisfacer esto; el zip por sí solo no |
| Integration boundary lacks direct automated tests | no se encontraron tests dedicados para service/adapters/runtime_bridge/persistence; solo menciones indirectas en workbench tests | regression risk | `tests/` | Alta | Coverage indirecta no reemplaza pruebas de boundary |
