# Diagnostic Session diag_20260410_172442

- started_at: `2026-04-10T17:24:42-06:00`
- finished_at: `2026-04-10T17:24:42-06:00`
- execution_mode: `support-bundle`
- target_path: `F:\repos\hitech-os\apps\code-atlas\capatch_system`
- app_kind: `unknown`
- enabled_plugins: `4`
- runtime_profile: `diagnostic`

## Environment summary

- **app_kind**: `"unknown"`
- **base_dir**: `"F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system"`
- **cwd**: `"F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system"`
- **env_flags**: `{"VIRTUAL_ENV": null, "PYTHONPATH": null, "NODE_ENV": null}`
- **environment_guard**: `{"payload": {"cwd": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "base_dir": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "target_path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "base_dir_name": "capatch_system", "target_exists": true, "target_is_dir": true, "hostname": "DESKTOP-H8EVT6Q", "platform": {"system": "Windows", "release": "11", "version": "10.0.26100", "machine": "AMD64", "python_version": "3.13.12"}, "python": {"executable": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", "prefix": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313", "base_prefix": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313", "version_info": [3, 13, 12], "venv_active": false}, "executables": {"python": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", "git": "C:\\Program Files\\Git\\cmd\\git.EXE", "node": "C:\\Program Files\\nodejs\\node.EXE", "npm": "C:\\Program Files\\nodejs\\npm.CMD", "pnpm": "C:\\Users\\alanh\\AppData\\Roaming\\npm\\pnpm.CMD", "yarn": null}, "env_flags": {"VIRTUAL_ENV": null, "PYTHONPATH": null, "NODE_ENV": null, "CAPATCH_WINDOWS_SMOKE_REQUIRED_PLUGINS": null}, "sys_path": ["F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\python313.zip", "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\DLLs", "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\Lib", "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313", "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages"], "workspace_markers": {"has_git": false, "has_package_json": false, "has_pyproject": false, "has_requirements": false, "has_reports_dir": true, "has_plugins_dir": true, "has_docker_compose": false, "has_dockerfile": false}, "registry_hash": "dd765800f015dcac2568da9ef522bb192b080a85a7139a0a652c5f8f0bd5945a", "plugin_runtime": {"runtime_version": "6.0.0", "runtime_status": {"status": "healthy", "runtime_version": "6.0.0", "active_plugins": 4, "rejected_plugins": 0, "disabled_plugins": 0, "duplicate_plugins": 0, "essential_plugins": {"status": "healthy", "runtime_version": "6.0.0", "essential_plugin_ids": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "active": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "missing": [], "rejected": [], "disabled": [], "duplicate": [], "healthy": true, "required_capabilities": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "capability_status": {"fixer.safe-runtime-actions": {"required": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "declared": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "missing": [], "satisfied": true}, "recommender.safe-fix-plan": {"required": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "declared": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "missing": [], "satisfied": true}, "verifier.post-fix-verifier": {"required": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "declared": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "missing": [], "satisfied": true}}, "missing_capabilities": []}, "all_declared_capabilities": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"], "load_summary": {"discovered": 4, "active": 4, "rejected": 0, "disabled": 0, "duplicate_ids": 0}}, "capability_map": {"runtime_version": "6.0.0", "active_plugin_ids": ["fixer.safe-runtime-actions", "guard.bloquear-cambios-riesgosos", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "phase_coverage": {"resolve-target": ["guard.bloquear-cambios-riesgosos"], "fix": ["fixer.safe-runtime-actions"], "verify": ["verifier.post-fix-verifier"], "export": [], "collect": [], "enrich": [], "analyze": [], "recommend": ["recommender.safe-fix-plan"]}, "kind_coverage": {"guard": ["guard.bloquear-cambios-riesgosos"], "target-detector": [], "context-enricher": [], "collector": [], "analyzer": [], "recommender": ["recommender.safe-fix-plan"], "fixer": ["fixer.safe-runtime-actions"], "verifier": ["verifier.post-fix-verifier"], "exporter": []}, "hook_totals": {"guards": 1, "before_apply": 1, "after_apply": 1, "support_resolvers": 0, "target_detectors": 0, "collectors": 0, "context_enrichers": 0, "analyzers": 0, "recommenders": 1, "fixers": 1, "verifiers": 1, "exporters": 0}, "load_summary": {"discovered": 4, "active": 4, "rejected": 0, "disabled": 0, "duplicate_ids": 0}, "disabled_plugin_ids": [], "rejected_plugin_ids": [], "duplicate_plugin_ids": [], "declared_capabilities_by_plugin": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "guard.bloquear-cambios-riesgosos": [], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "all_declared_capabilities": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"], "supports_fix_pipeline": true, "supports_verify_pipeline": true, "supports_export_pipeline": false}}, "expected_root_names": ["capatch_system"], "environment_fingerprint": "45c3a7d15929411154385e1f3e15ea47c4f6937c16f491ca2433219f30f9d1fb"}, "evaluation": {"status": "healthy", "reasons": [], "warnings": [], "environment_fingerprint": "45c3a7d15929411154385e1f3e15ea47c4f6937c16f491ca2433219f30f9d1fb"}}`
- **executables**: `{"python": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", "git": "C:\\Program Files\\Git\\cmd\\git.EXE", "node": "C:\\Program Files\\nodejs\\node.EXE", "npm": "C:\\Program Files\\nodejs\\npm.CMD", "pnpm": "C:\\Users\\alanh\\AppData\\Roaming\\npm\\pnpm.CMD", "yarn": null}`
- **hostname**: `"DESKTOP-H8EVT6Q"`
- **platform**: `{"system": "Windows", "release": "11", "version": "10.0.26100", "machine": "AMD64", "python_version": "3.13.12"}`
- **plugin_runtime**: `{"runtime_status": {"status": "healthy", "runtime_version": "6.0.0", "active_plugins": 4, "rejected_plugins": 0, "disabled_plugins": 0, "duplicate_plugins": 0, "essential_plugins": {"status": "healthy", "runtime_version": "6.0.0", "essential_plugin_ids": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "active": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "missing": [], "rejected": [], "disabled": [], "duplicate": [], "healthy": true, "required_capabilities": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "capability_status": {"fixer.safe-runtime-actions": {"required": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "declared": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "missing": [], "satisfied": true}, "recommender.safe-fix-plan": {"required": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "declared": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "missing": [], "satisfied": true}, "verifier.post-fix-verifier": {"required": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "declared": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "missing": [], "satisfied": true}}, "missing_capabilities": []}, "all_declared_capabilities": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"], "load_summary": {"discovered": 4, "active": 4, "rejected": 0, "disabled": 0, "duplicate_ids": 0}}, "capability_map": {"runtime_version": "6.0.0", "active_plugin_ids": ["fixer.safe-runtime-actions", "guard.bloquear-cambios-riesgosos", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "phase_coverage": {"resolve-target": ["guard.bloquear-cambios-riesgosos"], "fix": ["fixer.safe-runtime-actions"], "verify": ["verifier.post-fix-verifier"], "export": [], "collect": [], "enrich": [], "analyze": [], "recommend": ["recommender.safe-fix-plan"]}, "kind_coverage": {"guard": ["guard.bloquear-cambios-riesgosos"], "target-detector": [], "context-enricher": [], "collector": [], "analyzer": [], "recommender": ["recommender.safe-fix-plan"], "fixer": ["fixer.safe-runtime-actions"], "verifier": ["verifier.post-fix-verifier"], "exporter": []}, "hook_totals": {"guards": 1, "before_apply": 1, "after_apply": 1, "support_resolvers": 0, "target_detectors": 0, "collectors": 0, "context_enrichers": 0, "analyzers": 0, "recommenders": 1, "fixers": 1, "verifiers": 1, "exporters": 0}, "load_summary": {"discovered": 4, "active": 4, "rejected": 0, "disabled": 0, "duplicate_ids": 0}, "disabled_plugin_ids": [], "rejected_plugin_ids": [], "duplicate_plugin_ids": [], "declared_capabilities_by_plugin": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "guard.bloquear-cambios-riesgosos": [], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "all_declared_capabilities": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"], "supports_fix_pipeline": true, "supports_verify_pipeline": true, "supports_export_pipeline": false}}`
- **target_exists**: `true`
- **target_is_dir**: `true`
- **target_path**: `"F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system"`
- **workspace_markers**: `{"has_git": false, "has_package_json": false, "has_pyproject": false, "has_requirements": false, "has_reports_dir": true, "has_plugins_dir": true, "has_docker_compose": false, "has_dockerfile": false}`

## Plugin runtime

- **status**: `"healthy"`
- **active_plugins**: `4`
- **rejected_plugins**: `0`
- **disabled_plugins**: `0`
- **duplicate_plugins**: `0`

### Capability map

- `resolve-target`: guard.bloquear-cambios-riesgosos
- `fix`: fixer.safe-runtime-actions
- `verify`: verifier.post-fix-verifier
- `export`: -
- `collect`: -
- `enrich`: -
- `analyze`: -
- `recommend`: recommender.safe-fix-plan

## Artifacts

- `runtime.environment-summary` [diagnostics] via `runtime` | Resumen inicial del host, target y herramientas disponibles.
- `runtime.plugin-capability-map` [diagnostics] via `runtime` | Mapa real de capacidades del runtime y coverage por fase.
- `runtime.plugin-runtime-status` [diagnostics] via `runtime` | Estado real del loader de plugins: activos, rechazados, duplicados y disabled.
- `runtime.target-topology` [system] via `runtime` | Primer vistazo del target path con archivos/carpetas relevantes.
- `runtime.log-candidates` [logs] via `runtime` | Candidatos de logs detectados por heurística base.
- `runtime.log-tail-sample` [logs] via `runtime` -> `F:\repos\hitech-os\apps\code-atlas\capatch_system\reports\migration_report.json` | Tail base del log detectado: migration_report.json

## Findings

- No findings.

## Recommendations

- `runtime.next-step` Construir collectors y analyzers base
  - action: Agregar collectors y analyzers faltantes de acuerdo con el spec.
  - action: Usar --support-bundle para revisar el bundle fundacional generado por esta ronda.
  - action: Conectar capatch_policy cuando la subparte E materialice sus APIs públicas.

## Fix proposals

- No fix proposals.

## Verification

- No verification results.

## Execution records

- `recommend` / `recommender.safe-fix-plan` -> ok in 3 ms | Autofix Bridge no encontró propuestas aplicables todavía.

## Artifacts by phase

- `collect`: runtime.environment-summary, runtime.target-topology, runtime.log-candidates, runtime.log-tail-sample
- `resolve-target`: runtime.plugin-capability-map, runtime.plugin-runtime-status

## Warnings

- Diagnostic Runtime v6 scaffold activo, pero aún no hay collectors especializados registrados.
