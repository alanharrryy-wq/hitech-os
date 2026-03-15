# Architecture Target

## Goal

Split the flat legacy package into domain folders with a clear rule:

- `core/` owns orchestration
- `scanning/` owns repo scanning and artifact detection
- `security/` owns secrets and scanner quality
- `learning/` owns historical memory
- `analysis/` owns prediction and scoring
- `remediation/` owns cleanup and repair
- `operations/` owns scheduling and runtime control
- `reporting/` owns alerts, reports and serialized outputs
- `app/` owns dashboard, CLI and presentation
- `shared/` owns config, git helpers and cross-cutting utilities

## Migration order

1. Freeze the live runtime and keep using `tools/hos/git_sentinel` as source of truth.
2. Move shared contracts first: config, git helpers, utils, telemetry, false positives.
3. Move scanners and security modules.
4. Move learning and prediction.
5. Move cleanup/repair behind explicit guards.
6. Move dashboard last, after interfaces are stable.

## Definition of done per module

- public inputs/outputs documented
- side effects documented
- unit test placeholders replaced with real tests
- compatibility shim added if the legacy runtime still imports it
- CLI and dashboard paths still work in scan-only mode
