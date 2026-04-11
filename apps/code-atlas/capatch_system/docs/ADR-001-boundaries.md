# ADR-001: Boundaries and Contracts for the Capatch Workspace

- **Status:** accepted
- **Date:** 2026-04-10
- **Owners:** capatch workspace maintainers

## Context

`capatch` ya opera como workspace modular dentro de `code-atlas`, con responsabilidades bien distribuidas entre CLI, engine, filesystem, contracts, runtime, verify, policy, diagnostics, audit, tooling y tests.

El objetivo de este ADR es formalizar una arquitectura bonita, mantenible y operativamente clara para que el sistema siga creciendo con buen gusto técnico: contratos explícitos, ownership por frente y una semántica de éxito sustentada por evidencia.

## Decision

### 1. Entrypoint y experiencia de uso
- `capatch.py` se mantiene como **entrada estable del workspace**.
- El entrypoint operativo del CLI vive en `capatch_cli.main`.
- Esta combinación permite continuidad de uso y una frontera clara para la experiencia diaria.

### 2. Fronteras del sistema
- `capatch_cli/` es dueño de parseo, dispatch y comandos.
- `capatch_engine/` es dueño del patch pipeline público: parse, preflight, preview, apply, verify y lifecycle transaccional.
- `capatch_fs/` es dueño de IO atómico, hashing, guards, snapshots, locks y checkpoints de filesystem.
- `capatch_ops/` es dueño del catálogo de operaciones declarativas.
- `capatch_diagnostics/` es dueño de targeting, bundles, reporting y runtime diagnóstico.
- `capatch_plugins/` es dueño del runtime de plugins, metadata, registry y estado operativo.
- `capatch_policy/` es dueño de riesgo, confidence, verification floors, intervention gates y auto rollback.
- `capatch_audit/` es dueño de patch runs, manifests, rollback, baselines e historial.
- `capatch_verify/` es dueño del registry de verificadores, packs y built-ins.
- `capatch_runtime/` es dueño de environment guard, readiness gate e higiene operativa del workspace.
- `tests/`, `fixtures/` y `tooling/` sostienen QA, smoke, benchmark y operación asistida.

### 3. Contratos y versionado
Los contratos versionados viven en `capatch_contracts/` y sus schemas en `capatch_contracts/schemas/`.

Contratos mínimos canónicos:
- `operation.schema.json`
- `patch_run.schema.json`
- `plugin_payload.schema.json`
- `verification_result.schema.json`
- `telemetry_artifact.schema.json`

Además:
- `capatch_contracts/plugin_runtime.py` es la fuente de verdad contractual del runtime de plugins.
- la versión contractual y la versión efectiva del runtime deben permanecer alineadas y visibles.

### 4. Regla de integración
Los módulos se integran **solo por APIs públicas y contratos versionados**.
No se deben usar helpers privados de otro frente como atajo informal.

### 5. Semántica de éxito
Se distinguen dos niveles útiles:

- `patch_success`: el motor pudo aplicar o resolver el resultado del patch
- `system_success`: el sistema quedó en estado aceptable según verify, policy, runtime y evidencia operativa

Vocabulario común esperado:
- `applied`
- `noop`
- `skipped`
- `failed`
- `verified`
- `rolled_back`
- `degraded`
- `promotable`
- `blocked`

### 6. Audit, rollback y baselines
`capatch_audit/` consume salidas públicas del engine y produce evidencia operativa.
Además de checkpoints técnicos, el workspace reconoce baselines oficiales como puntos sanos promocionables, comparables y restaurables.

### 7. Runtime diagnóstico y plugins
El runtime diagnóstico usa al engine como brazo ejecutor vía interfaces públicas.
Los plugins se integran por contracts, capabilities y registry, sin contaminar la frontera del engine.

### 8. Telemetry y readiness
La telemetry forma parte del contrato operativo del workspace.
El readiness gate consolida salud del runtime, evidence, reports, contracts y señales críticas para decidir promoción.

### 9. Documentación canónica
- `docs/WORKSPACE_README.md` describe estructura observable y operación diaria.
- `docs/OPERATING_GUIDE.md` guía operación, cierre y promoción.
- `docs/TROUBLESHOOTING.md` documenta señales comunes y su interpretación útil.
- `docs/CAPATCH_CLOSURE_REPORT.md` resume el estado final y las capacidades del workspace.
- `docs/CHANGELOG_WORKSPACE.md` registra hitos relevantes del workspace.

## Consequences

### Positivas
- ownership claro por carpeta y por frente
- menos acoplamiento accidental
- contracts y schemas más fáciles de mantener
- verificación más expresiva y más confiable
- mejor trazabilidad entre engine, runtime, policy, verify, audit y telemetry
- una operación diaria más legible, con mejores herramientas de promoción y recuperación

### Costos aceptados
- más disciplina en integración
- más atención a compatibilidad contractual
- más valor puesto en readiness, evidence y observabilidad operativa

## Acceptance criteria

Se considera alineado con este ADR cuando:
1. `capatch.py` sigue siendo la entrada estable del workspace.
2. `capatch_cli.main` sigue siendo el entrypoint operativo del CLI.
3. Los schemas versionados siguen presentes en `capatch_contracts/schemas/`.
4. `capatch_contracts/plugin_runtime.py` sigue siendo la fuente de verdad contractual del runtime.
5. El patch pipeline conserva preflight, transacción, verify y rollback integrados.
6. El readiness gate y la telemetry operan como parte del modelo oficial del workspace.
7. Los baselines siguen siendo entidades promocionables y restaurables de primera clase.
