# DeltaForge · Merge Gates

## Gates obligatorios antes de abrir lanes

| Gate | Qué valida | Evidencia mínima |
|---|---|---|
| `contracts_frozen` | contratos y eventos estables | `FROZEN_CONTRACTS.md` actualizado |
| `domain_models_frozen` | scope/session/ops/plan/diff/results cerrados | hashes + smoke básico |
| `session_truth_frozen` | `SessionWorkspace` contiene la verdad visible | checklist firmada |
| `state_machine_frozen` | transiciones inválidas levantan error controlado | unit/smoke |
| `theme_frozen` | tokens y roles semánticos definidos | `tokens.py` + `semantic_roles.py` |
| `canonical_paths_frozen` | una sola ruta canónica por concepto | `CANONICAL_PATHS.md` + grep de shims |
| `legacy_policy_enforced` | shims sin lógica nueva y sin imports nuevos a legacy | diff + grep |
| `import_gates_green` | sin violaciones de capa | `rg`/inspección documentada |
| `wiring_smoke_green` | arranque sin import/runtime error | log de arranque |

## Checklist de apertura de lanes
- [ ] `main_window.py` es ruta canónica activa
- [ ] no hay ruta canónica activa `*_alt.py`
- [ ] command bar y session tabs tienen ownership único en `ui/widgets/*`
- [ ] settings store tiene ownership único en `infrastructure/settings_store.py`
- [ ] chip/section_card/separator tienen ownership único
- [ ] shims legacy existen solo como forward/re-export
- [ ] ningún import nuevo apunta a legacy paths
- [ ] law files congelados y ownership firmado
- [ ] estructura de tests normalizada: `tests/unit`, `tests/contracts`, `tests/smoke`

## Legacy / shim policy (gate rule)
1. Legacy files solo pueden vivir como shims temporales.
2. Ningún shim puede añadir reglas de negocio, UI behavior o lógica de estado.
3. Cualquier cambio funcional en un shim bloquea merge.
4. Toda implementación nueva debe aterrizar en ruta canónica.

## Gate de cierre por lane
Cada lane entrega:
1. archivos tocados
2. archivos nuevos
3. compatibilidad/risks
4. blockers reales
5. handoff corto
6. validación de que no tocó law files
