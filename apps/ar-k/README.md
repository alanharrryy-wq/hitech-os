# Ar-k

Ar-k now ships as a governed System + Kernel + Contracts platform with five engines running on one constitution: scanner discovers, registry_builder consolidates, switch_engine resolves, contract_validator protects, and ai_annotator suggests without mutating canonical truth.

## What is in this delivery

- `pya/system/`: sovereign rules, compatibility, ownership, state model, determinism policy, admission rules
- `pya/kernel/`: runtime context, governed storage, event bus, pipeline coordinator, barriers, loader, contract checks
- `pya/contracts/`: canonical shapes and validators for signals, registries, switches, validation, annotations, artifacts, snapshots, engine manifests, events, indices
- `pya/engines/`: the five governed engines with manifest, entrypoint, internal README, useful iteration-1 behavior, a frontend observation slice that can inspect TS/JS/JSON/HTML/CSS surfaces, and path-classification policy that keeps non-product classes observable but non-canonical
- `docs/`: constitution, admission, contracts, ownership, integration, parallel development, and per-engine operating notes
- `installer/install_ar_k_integration.py`: controlled installer with dry-run, apply, verify, rollback, backup, auto-rollback, one main log target, and payload filtering that excludes generated runtime state such as `reports/`, `.ark_install/`, and `__pycache__/`

## Canonical stage order

1. `scan`
2. `registry`
3. `switch`
4. `validate`
5. `annotate`

## Deterministic execution invariants

- stable iteration order over files, manifests, registries, and switches
- stable JSON serialization with sorted keys
- deterministic ids from canonical hashes and normalized relative paths
- no dependency on current working directory
- one execution timestamp propagated through the whole run
- typed failures for admission, ownership, pipeline, and contracts

## Canonical promotion policy (current)

- scanner always observes files, but marks each path with `canonical_source` and optional `non_product_class`
- registry_builder promotes only canonical product/runtime module candidates
- non-product classes stay observed but non-canonical by default:
  - `docs`, `reports`, `_dependency_graphs`
  - `tests`, `tools`, `scripts`, `fixtures`, `examples`
  - history/rollback/patch/artifact/backups/hidden paths
- skipped promotion decisions are explicit in `artifacts/metrics/registry_build_summary.json`

## Developing the 5 engines in parallel

### A. Qué motor hace qué

- **Scanner** descubre estructura real, emite `signal`, y ahora también observa superficies frontend, rutas y boundaries sin canonicalizar por su cuenta.
- **Registry Builder** consolida señales en registries canónicos, snapshots, deltas y query index.
- **Switch Engine** resuelve el estado efectivo de switches con precedencia auditable.
- **Contract Validator** protege la forma, referencias y política.
- **AI Annotator** anota desde evidencia sin tocar verdad canónica.

### B. Qué NO puede hacer cada motor

- **Scanner** no puede canonicalizar, resolver switches, validar formalmente ni anotar.
- **Registry Builder** no puede resolver estado efectivo, publicar veredictos de validación ni promover anotaciones.
- **Switch Engine** no puede reescribir registries canónicos ni inventar contexto silencioso.
- **Contract Validator** no puede corregir por decreto, reescribir truth registries ni producir anotaciones.
- **AI Annotator** no puede mutar identidad oficial, canonicidad, validación formal ni resolución de switches.

### C. Qué contratos consume cada motor

- **Scanner** produce `signal`, consume `event` y `execution_summary`.
- **Registry Builder** consume `signal` y produce `module_registry_entry`, `boundary_entry`, `contract_registry_entry`, `switch_registry_entry`, `query_index`, `snapshot`, `delta`, `registry_build_summary`.
- **Switch Engine** consume `switch_registry_entry` y produce `switch_resolution`.
- **Contract Validator** consume registries, `switch_resolution`, `query_index` y produce `validation_violation` + `contract_health_summary` dentro de `validation_report`.
- **AI Annotator** consume registries + validation outputs y produce `annotation`.

### D. Qué registries puede leer/escribir cada motor

- **Scanner** escribe `signals`.
- **Registry Builder** lee `signals` y escribe `module_registry`, `boundary_registry`, `contract_registry`, `switch_registry`, `query_index`, `snapshots`, `deltas`.
- **Switch Engine** lee `module_registry`, `switch_registry` y escribe `switch_resolutions`.
- **Contract Validator** lee `module_registry`, `boundary_registry`, `contract_registry`, `switch_registry`, `switch_resolutions`, `query_index` y escribe `validation_report`.
- **AI Annotator** lee `module_registry`, `boundary_registry`, `validation_report`, `switch_resolutions` y escribe `annotations`.

### E. Qué artifacts debe emitir cada motor

- **Scanner**: `artifacts/inventory/scanner_inventory.json`, `artifacts/routes/route_candidates.json`, `artifacts/boundaries/boundary_candidates.json`, `artifacts/graph/dependency_graph.json`, `artifacts/metrics/scanner_metrics.json`
- **Registry Builder**: `artifacts/metrics/registry_build_summary.json`, `snapshots/registry_bundle_<execution>.json`, `deltas/registry_bundle_<execution>.json`
- **Switch Engine**: `artifacts/decision_trace/switch_decision_trace.json`
- **Contract Validator**: `artifacts/validation_report/validation_report.json`
- **AI Annotator**: `artifacts/annotations/annotations.json`

### F. Qué eventos debe emitir cada motor

- **Scanner**: `scanner.started`, `scanner.parse_warning`, `scanner.completed`
- **Registry Builder**: `registry_builder.started`, `registry_builder.completed`
- **Switch Engine**: `switch_engine.started`, `switch_engine.override_warning`, `switch_engine.completed`
- **Contract Validator**: `contract_validator.started`, `contract_validator.completed`
- **AI Annotator**: `ai_annotator.started`, `ai_annotator.completed`

### G. Cómo desarrollar cada motor en paralelo sin romper el kernel

- no cambiar contratos canónicos por cuenta propia
- no inventar nuevos states
- no escribir fuera del dominio declarado
- no mutar canonicidad sin pasar por `registry_builder`
- no tocar `system/` o `kernel/` sin revisión explícita
- no alterar `ownership_policy`
- no crear writes clandestinos en paths no declarados

### H. Cómo integrar un motor terminado

1. validar `manifest.json`
2. validar compatibilidad con kernel y contratos
3. correr tests del motor
4. correr smoke del kernel
5. correr integración en `examples/sample_app`
6. confirmar artefactos mínimos
7. confirmar que no rompe query index, registries, validation ni ownership

### I. Comandos exactos

```powershell
$root = "F:\repos\hitech-os\apps\Ar-k"
$payload = "F:\descargasf\ark_governed_payload.zip"
$installer = "F:\descargasf\install_ar_k_integration.py"
$env:PYTHONPATH = $root

python -m compileall "$root\pya"
python -m pya.tools.pya doctor --root $root
python -m unittest tests.test_smoke
python -m unittest tests.test_system_kernel_contracts tests.test_engine_admission_contracts
python -m unittest tests.test_scanner_engine tests.test_registry_builder_engine tests.test_switch_engine tests.test_contract_validator_engine tests.test_ai_annotator_engine
python -m pya.tools.pya run --root $root --target "$root\examples\sample_app" --out "$root\reports"
python $installer --dry-run --root $root --payload $payload
python $installer --apply --root $root --payload $payload
python $installer --verify --root $root --payload $payload
python $installer --rollback --root $root --payload $payload
```

## Core validation commands

```powershell
$root = "F:\repos\hitech-os\apps\Ar-k"
$env:PYTHONPATH = $root

python -m compileall "$root\pya"
python -m pya.tools.pya doctor --root $root
python -m pya.tools.pya run --root $root --target "$root\examples\sample_app" --out "$root\reports"
python -m unittest discover -s "$root\tests" -v
```

## Real target validation (current)

```powershell
$root = "F:\repos\hitech-os\apps\Ar-k"
$target = "F:\repos\hitech-os\apps\external_interaction_template"
$out = "$root\reports_real"
$env:PYTHONPATH = $root

python -m pya.tools.pya run --root $root --target $target --out $out
```

## Docs map

- `docs/platform_constitution.md`
- `docs/engine_admission.md`
- `docs/execution_plane.md`
- `docs/contracts_reference.md`
- `docs/contract_evolution_policy.md`
- `docs/canonical_promotion_policy.md`
- `docs/ownership_and_write_paths.md`
- `docs/integration_of_five_motors.md`
- `docs/parallel_development_guide.md`
- `docs/*_engine_spec.md`
