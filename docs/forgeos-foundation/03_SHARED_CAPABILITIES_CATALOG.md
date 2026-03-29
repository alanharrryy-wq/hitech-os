# 03_SHARED_CAPABILITIES_CATALOG.md

## Qué es Forge Commons

**Forge Commons** es la capa de capacidades compartidas de ForgeOS.  
No es el kernel.  
No es un cajón de sastre.  
No es un producto disfrazado.

Una capability entra a Forge Commons solo si puede sostenerse por sí misma en estos ejes:

- contrato público claro;
- owner claro;
- lifecycle claro;
- teardown claro;
- storage claro;
- semántica neutral al dominio;
- valor reusable real.

## Qué cuenta como shared capability

Cuenta como shared capability aquello que:

1. resuelve una necesidad transversal de plataforma o de más de un producto;
2. puede describirse sin vocabulario de un producto concreto;
3. puede empacarse y versionarse de forma independiente;
4. puede fallar, degradarse y disponerse sin romper la identidad del host;
5. no necesita leer internals del host ni de un producto para operar.

## Criterios de calificación para promover algo a Forge Commons

Una propuesta de capability debe pasar **todas** estas pruebas:

1. **Reuso probado o necesidad estructural de plataforma**  
   Dos consumidores reales o necesidad transversal inequívoca.

2. **Lenguaje neutral**  
   El nombre, schema y contrato no deben contener semántica de producto.

3. **Autoridad de estado definida**  
   Debe quedar claro qué guarda, dónde lo guarda y quién puede escribir.

4. **Lifecycle autónomo**  
   Debe poder declararse `ready`, `degraded`, `disposing`, `disposed`.

5. **Teardown explícito**  
   Debe cerrar workers, stores, handles, procesos o caches sin depender del cierre del host.

6. **Packaging independiente**  
   Debe poder entregarse como paquete o módulo con manifest propio.

7. **Observabilidad suficiente**  
   Debe emitir health y fallas con owner, correlation y outcome.

## Criterios de democión: cuándo algo debe quedarse product-local

Algo **no** sube a Forge Commons si ocurre cualquiera de estos puntos:

- solo lo usa un producto;
- el lenguaje público contiene semántica de dominio;
- depende del `main_window`, del host shell o de un controller específico;
- combina infraestructura reusable con payloads o reglas de negocio del producto;
- no tiene store ni owner claros;
- su valor principal es UI product-specific;
- su lifecycle depende del constructor o de side effects del host.

## Capability candidates derivados del código actual

| Capability candidate | Evidencia | Decisión | Owner target | Racional |
| --- | --- | --- | --- | --- |
| Gestión de configuración y política runtime | `app/gui_qt/preferences/runtime.py`, `policy.py`, `applicator.py`, más uso fragmentado de `QSettings` y `.repo_analyzer_settings.json`. | Promover a Forge Commons | Forge Commons Config & Policy | Es transversal, domain-agnostic y hoy ya afecta host, shell y productos. |
| Diagnósticos y health telemetry | diagnósticos de startup y plugin reportes en `main_window.py` y `plugin_manager.py`. | Promover a Forge Commons | Forge Commons Diagnostics | Se necesita en kernel, commons y productos; no depende del dominio del producto. |
| Supervisión de ejecución de procesos | `plugins/orchestrator_bridge/process_session_controller.py`, timeouts en `bridge_config.py`, evento `PROCESS_SESSION_STATE_CHANGED`. | Promover núcleo del capability a Forge Commons | Forge Commons Process Execution | Los timeouts, kill policies, stdout/stderr capture y estados de proceso son reusables. |
| Historial y ledger de runs | `plugins/orchestrator_bridge/bridge_history.py` y artefactos de sesión/manifest en el bundle. | Promover a Forge Commons | Forge Commons History & Runs | La persistencia de ejecuciones y restauración de payloads es reusable en más de un producto operativo. |
| Exportación y emisión de artefactos | El bundle trae manifests, zips, sha256 y el plugin Orchestrator Bridge declara reportes. | Promover mínimo común a Forge Commons | Forge Commons Export | La emisión de artefactos versionados, BOM y reportes es una necesidad transversal de plataforma. |
| Search/Indexing | `app/backend/analyzer_backend.py` y controllers de búsqueda/preview del host actual. | Mantener product-local por ahora | Forge Product `repo_analyzer` (inferido) | La evidencia muestra un solo dominio consumidor y vocabulario de repositorio/código. |
| Graph/Snapshot | `plugins/cloudflare_guardian/*`, `graph_radar.py`, `deck_shell.py`, `guardian_contract.py`. | No promover la visualización; dejar snapshot envelope como candidato futuro | Forge Product `cloudflare_guardian` | La UI, los campos y la semántica son del producto. Solo un envelope de snapshot podría neutralizarse después. |

## Lectura fina por capability

### 1. Search/Indexing
- **Evidencia**: `AnalyzerBackend` concentra indexado, búsqueda, preview y semántica de repositorio.
- **Decisión**: no promover ahora.
- **Motivo**: el vocabulario es de repositorio/código; no existe segundo consumidor probado.
- **Regla**: mantenerlo product-local dentro de `repo_analyzer` hasta que un segundo producto necesite un contrato neutral.

### 2. Process Execution
- **Evidencia**: `process_session_controller.py`, timeouts en `bridge_config.py`, evento `PROCESS_SESSION_STATE_CHANGED`.
- **Decisión**: promover solo el runtime genérico de ejecución, no el dominio Orchestrator.
- **Sube a Commons**:
  - process launch supervision;
  - timeout policy;
  - kill/reap policy;
  - stdout/stderr streaming;
  - estado genérico de ejecución;
  - observabilidad de proceso.
- **Se queda local**:
  - payload de negocio del Orchestrator;
  - semántica de run/round/session de su dominio;
  - UI y affordances del bridge.

### 3. Config Management
- **Evidencia**: `QSettings`, `.repo_analyzer_settings.json`, bridge config y snapshots dispersos.
- **Decisión**: promover.
- **Alcance**:
  - perfiles runtime;
  - settings transversales;
  - schema/version de config;
  - policies de lectura/escritura;
  - validación y migraciones.
- **Límite**:
  - las claves y stores de dominio de producto no se absorben; solo se gobiernan.

### 4. Reporting/Export
- **Evidencia**: bundle con zips, manifests, hashes; Orchestrator declara reportes.
- **Decisión**: promover una capability mínima de export/artifact emission.
- **Sube a Commons**:
  - emisión de artefactos versionados;
  - generación de BOM;
  - manifests de release;
  - políticas de naming, hashes y validación.
- **Se queda local**:
  - narrativa y contenido de reportes de un producto;
  - cualquier deck o vista especializada.

### 5. Diagnostics
- **Evidencia**: startup diagnostics, plugin diagnostics, warnings y reportes dispersos.
- **Decisión**: promover.
- **Sube a Commons**:
  - health model;
  - warning/error ledger;
  - trace envelopes;
  - startup/activation/degradation reporting.
- **Límite**:
  - el capability no dicta copy/UI final de diagnósticos de un producto.

### 6. Graph/Snapshot
- **Evidencia**: `cloudflare_guardian` contiene deck, graph radar, context cards y contratos Cloudflare.
- **Decisión**: la visualización se queda local; solo un envelope de snapshot podría considerarse reusable más adelante.
- **Sube a Commons hoy**: nada de la UI graph.
- **Candidato futuro**:
  - `snapshot envelope` neutral, si dos o más productos lo necesitan.
- **Regla**: nunca promover campos Cloudflare al kernel ni a Commons.

### 7. History/Runs
- **Evidencia**: `bridge_history.py` y manifests de sesión incluidos en el bundle.
- **Decisión**: promover un run ledger genérico.
- **Sube a Commons**:
  - append-only ledger;
  - retención y purge;
  - restore de última ejecución por schema estable;
  - manifest stamping.
- **Se queda local**:
  - interpretación de cada run según el dominio del producto.

## Modelo de ownership de capabilities

Cada capability de Forge Commons debe declarar estos dueños:

- **Capability owner**: responsable funcional del capability.
- **Contract owner**: responsable del surface público.
- **Runtime owner**: responsable de health, perf y degradación.
- **State owner**: responsable de storage, schema y migraciones.
- **Packaging owner**: responsable de manifest, BOM, rollback y compatibilidad.

Si dos o más roles caen en la misma persona/equipo, se permite.  
Si alguno no existe, la capability no está lista.

## Modelo de lifecycle de capabilities

1. **Incubación local**
   - vive dentro de un producto;
   - todavía no entra a Commons.

2. **Propuesta de promoción**
   - se presenta evidencia de reuso;
   - se define contrato neutral;
   - se define owner y store.

3. **Incubación en Commons**
   - capability ya existe como paquete separado;
   - solo consumidores aprobados.

4. **Estable**
   - versionado normal;
   - compatibility ranges claros;
   - gates de aceptación activos.

5. **Deprecado**
   - reemplazo declarado;
   - migration path definido.

6. **Retirado**
   - install gate lo bloquea;
   - storage y rollback documentados.

## Reglas de dependencia para capabilities

- Una capability puede depender de Forge Kernel público.
- Una capability puede depender de otra capability solo si la dependencia está declarada, aprobada y no crea cadena circular.
- Una capability no puede depender de productos.
- Una capability no puede importar internals privados del host.
- Una capability no puede guardar referencias a widgets o controllers del host como parte de su API pública.

## Qué jamás debe promoverse a las capas compartidas

- campos `hostname`, `tunnel_id`, `origin_expected`, `origin_observed` y equivalentes de dominio;
- heurísticas de grupos o categorías basadas en nombres de producto;
- cualquier state adapter que raspe el host;
- cualquier deck, radar, card UI o visualización con semántica Cloudflare;
- payloads de negocio del Orchestrator;
- lógica de análisis de repositorios mientras solo exista ese consumidor;
- shortcuts de compatibilidad legacy.

## Decisión de promoción inicial de Forge Commons

La primera línea oficial de Forge Commons queda así:

1. `config_policy`
2. `diagnostics`
3. `process_execution`
4. `history_runs`
5. `export_artifacts`

Y explícitamente **no** suben en la primera ola:

- `search_indexing`
- `graph_snapshot` visual
- cualquier shim legacy
