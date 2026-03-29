# 09_RECONSTRUCTION_ORDER.md

Este es el orden oficial de reconstrucción. No es opcional.

La regla es simple: **no se migra nada de producto antes de fijar kernel, contratos y capabilities compartidos.**

## Phase 0: truth capture

- **Objetivo**: Congelar evidencia y clasificar todo el legado por owner y destino antes de tocar implementación.
- **Inputs**: bundle de handoff, `source_artifacts/repo_analizer.zip`, pathologies catalog, matrices iniciales
- **Outputs**: inventario legado clasificado, catálogos de patologías, mapping legacy->target, log de supuestos
- **Done criteria**: cada subsistema legacy tiene destino: kernel, commons, product, quarantine o delete
- **Riesgos**: empezar a diseñar UI o mover archivos antes de entender ownership
- **Anti-patterns**: codificar, renombrar carpetas del legado, asumir compatibilidad por parecido
- **Qué no debe empezar todavía**: no reconstruir host; no migrar productos

---

## Phase 1: kernel definition

- **Objetivo**: Definir y scaffoldar Forge Kernel con límites duros y host shell domain-agnostic.
- **Inputs**: constitución, blueprint, kernel boundaries, decision log
- **Outputs**: repo skeleton de kernel, slot model, lifecycle authority, state authority registry, packaging gate base
- **Done criteria**: kernel compila y su árbol no contiene nombres ni semántica de producto
- **Riesgos**: meter features del primer producto en el kernel por comodidad
- **Anti-patterns**: recrear `main_window.py` con otro nombre; meter controllers legacy intactos
- **Qué no debe empezar todavía**: no extraer commons; no migrar UI de productos

---

## Phase 2: contract system

- **Objetivo**: Construir el runtime contractual antes de mover features.
- **Inputs**: catalog of contracts, kernel skeleton
- **Outputs**: registry contractual, validation rules, error envelopes, observability hooks, contract indexes base
- **Done criteria**: toda interacción cross-layer prevista tiene familia, owner, version y validation path
- **Riesgos**: permitir escapes temporales por string o callbacks directos
- **Anti-patterns**: portar `EventBus` o `CommandDispatcher` como solución final
- **Qué no debe empezar todavía**: no activar productos reales; no portar process runtimes todavía

---

## Phase 3: shared capabilities definition

- **Objetivo**: Extraer y estabilizar solo las capacidades realmente compartidas.
- **Inputs**: shared capabilities catalog, contract system
- **Outputs**: commons packages para config_policy, diagnostics, process_execution, history_runs y export_artifacts
- **Done criteria**: cada capability tiene owner, contract, lifecycle, state authority y packaging propios
- **Riesgos**: subir demasiado a commons y crear un basurero reusable de mentira
- **Anti-patterns**: promover `AnalyzerBackend` o graph UI solo porque ya existen
- **Qué no debe empezar todavía**: no migrar productos completos; no polish visual

---

## Phase 4: host shell rebuild

- **Objetivo**: Reconstruir un host shell limpio que pueda vivir con cero productos y renderizar contributions contractuales.
- **Inputs**: kernel definido, contract runtime, commons base
- **Outputs**: host shell domain-agnostic, slot manager, contribution renderer, fault isolation y timeout wiring
- **Done criteria**: el host arranca, se observa, acepta un producto dummy y no contiene branching product-specific
- **Riesgos**: volver a meter semantics de Repo Analyzer dentro del host
- **Anti-patterns**: reusar `group_shell.py`, `tool_workspace.py` o `tools/catalog.py` sin reescritura
- **Qué no debe empezar todavía**: no portar visual system premium ni products reales

---

## Phase 5: product skeleton establishment

- **Objetivo**: Instalar el skeleton canónico de Forge Products y validarlo en el repo nuevo.
- **Inputs**: product skeleton template, host integration spec, packaging spec
- **Outputs**: template clonable, producto dummy de referencia, gates de skeleton
- **Done criteria**: un producto vacío pero válido puede instalarse, activarse, suspenderse y disponerse
- **Riesgos**: dejar el skeleton como papel y no como estructura operable
- **Anti-patterns**: crear productos sin manifests, sin contract index o sin teardown
- **Qué no debe empezar todavía**: no migrar producto legacy todavía

---

## Phase 6: product migrations

- **Objetivo**: Migrar productos uno por uno, en orden fijo, usando el skeleton y contracts ya establecidos.
- **Inputs**: kernel, commons, host shell, skeleton validado
- **Outputs**: productos migrados y aislados; legacy quarantine acotado
- **Done criteria**: cada producto vive aislado, sin tocar internals del host, con contracts y teardown completos
- **Riesgos**: reintroducir atajos del legado por presión de paridad funcional
- **Anti-patterns**: migrar dos productos a la vez; dejar adapters de host scraping dentro del producto
- **Qué no debe empezar todavía**: no harden packaging global ni hacer polish visual final

---

## Phase 7: packaging hardening

- **Objetivo**: Cerrar installation, upgrade, rollback, integrity y compatibility de forma verificable.
- **Inputs**: packages kernel/commons/products ya migrados
- **Outputs**: manifests completos, BOMs, release notes, rollback plans, compatibility matrix de release
- **Done criteria**: install/upgrade/rollback dry runs son repetibles y con evidencia
- **Riesgos**: tratar packaging como post-proceso cosmético
- **Anti-patterns**: armar bundles sin manifiestos o sin migraciones
- **Qué no debe empezar todavía**: no gastar tiempo en polish visual fuera de correcciones de gate

---

## Phase 8: visual/system polish

- **Objetivo**: Mejorar ergonomía, skins, motion y detalles del sistema sin tocar fronteras.
- **Inputs**: sistema ya gobernado, empaquetado y con productos migrados
- **Outputs**: polish visual, afinaciones de UX, tokens y motion dentro de límites limpios
- **Done criteria**: el sistema luce mejor sin reabrir contaminación arquitectónica
- **Riesgos**: volver a colar coupling desde visual runtime o shortcut UI
- **Anti-patterns**: usar el polish como excusa para meter lógica de negocio al host
- **Qué no debe empezar todavía**: no redefinir contratos base ni mover otra vez ownership

---


## Orden interno obligatorio dentro de Phase 6

La migración de productos se hace en este orden y en este orden nada más:

1. **`repo_analyzer`**  
   Porque hoy su dominio está disperso en el host y es la principal fuente de contaminación del shell.

2. **`cloudflare_guardian`**  
   Porque hoy contamina contexto global y raspa internals del host.

3. **`orchestrator_bridge`**  
   Porque depende de process execution e history/runs, que ya deben existir como Commons.

4. **Dev/demo/legacy tools**  
   Se reevalúan. El default es quarantine o delete, no migración automática.

## Regla de paso entre fases

Ninguna fase avanza si la anterior no dejó evidencia suficiente para gates de:

- boundary cleanliness;
- contract completeness;
- state authority;
- teardown;
- compatibility.

## Regla final

El orden existe para evitar que el legado vuelva a colarse por una puerta lateral.  
Moverlo por ansiedad funcional es exactamente cómo se reconstruye el mismo problema con pintura fresca.
