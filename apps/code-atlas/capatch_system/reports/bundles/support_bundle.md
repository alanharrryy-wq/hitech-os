# Support Bundle

- session_id: `diag_20260504_151732`
- target_path: `F:\repos\hitech-os\apps\code-atlas\capatch_system`
- app_kind: `unknown`
- execution_mode: `support-bundle`

## Runtime status

- **status**: `"healthy"`
- **runtime_version**: `"6.0.0"`
- **active_plugins**: `3`
- **rejected_plugins**: `0`
- **disabled_plugins**: `0`
- **duplicate_plugins**: `0`
- **essential_plugins**: `{"status": "healthy", "runtime_version": "6.0.0", "essential_plugin_ids": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "active": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "missing": [], "rejected": [], "disabled": [], "duplicate": [], "healthy": true, "required_capabilities": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "capability_status": {"fixer.safe-runtime-actions": {"required": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "declared": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "missing": [], "satisfied": true}, "recommender.safe-fix-plan": {"required": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "declared": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "missing": [], "satisfied": true}, "verifier.post-fix-verifier": {"required": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "declared": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "missing": [], "satisfied": true}}, "missing_capabilities": []}`
- **all_declared_capabilities**: `["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"]`
- **load_summary**: `{"discovered": 3, "active": 3, "rejected": 0, "disabled": 0, "duplicate_ids": 0}`

## Priority findings

- No findings collected yet.

## Recommended next steps

- Construir collectors y analyzers base
  - Agregar collectors y analyzers faltantes de acuerdo con el spec.
  - Usar --support-bundle para revisar el bundle fundacional generado por esta ronda.
  - Conectar capatch_policy cuando la subparte E materialice sus APIs públicas.

## Artifact index

- `runtime.environment-summary` | diagnostics | inline
- `runtime.plugin-capability-map` | diagnostics | inline
- `runtime.plugin-runtime-status` | diagnostics | inline
- `runtime.target-topology` | system | inline
- `runtime.log-candidates` | logs | inline
- `runtime.log-tail-sample` | logs | F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_logs\fix_capatch_warn.log

## Evidence excerpts

### runtime.environment-summary

- category: `diagnostics`
- source_plugin: `runtime`

```
{"cwd": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "base_dir": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "target_path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "target_exists": true, "target_is_dir": true, "app_kind": "unknown", "hostname": "DESKTOP-H8EVT6Q", "platform": {"system": "Windows", "release": "11", "version": "10.0.26100", "machine": "AMD64", "python_version": "3.13.12"}, "executables": {"python": "C:\\Users\\alanh\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", "git": "C:\\Program Files\\Git\\cmd\\git.EXE", "node": "C:\\Program Files\\nodejs\\node.EXE", "npm": "C:\\Program Files\\nodejs\\npm.CMD", "pnpm": "C:\\Users\\alanh\\AppData\\Roaming\\npm\\pnpm.CMD", "yarn": null}, "workspace_markers": {"has_git": false, "has_package_json": false, "has_pyproject": false, "has_requirements": false, "has_reports_dir": true, "has_plugins_dir": true, "has_docker_compose": false, "has_dockerfile": false}, "env_flags": {"VIRTUAL_ENV": null, "PYTHONPATH": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system;F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "NODE_ENV": null}, "environment_guard": {"payload": {"cwd": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "base_dir": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "target_path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system", "base_dir_name": "capatch_system", "target_exists": true, "target_is_di
```

### runtime.plugin-capability-map

- category: `diagnostics`
- source_plugin: `runtime`

```
{"runtime_version": "6.0.0", "active_plugin_ids": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "phase_coverage": {"resolve-target": [], "fix": ["fixer.safe-runtime-actions"], "verify": ["verifier.post-fix-verifier"], "export": [], "collect": [], "enrich": [], "analyze": [], "recommend": ["recommender.safe-fix-plan"]}, "kind_coverage": {"guard": [], "target-detector": [], "context-enricher": [], "collector": [], "analyzer": [], "recommender": ["recommender.safe-fix-plan"], "fixer": ["fixer.safe-runtime-actions"], "verifier": ["verifier.post-fix-verifier"], "exporter": []}, "hook_totals": {"guards": 0, "before_apply": 0, "after_apply": 0, "support_resolvers": 0, "target_detectors": 0, "collectors": 0, "context_enrichers": 0, "analyzers": 0, "recommenders": 1, "fixers": 1, "verifiers": 1, "exporters": 0}, "load_summary": {"discovered": 3, "active": 3, "rejected": 0, "disabled": 0, "duplicate_ids": 0}, "disabled_plugin_ids": [], "rejected_plugin_ids": [], "duplicate_plugin_ids": [], "declared_capabilities_by_plugin": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "all_declared_capabilities": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware", "recommend.outputs.fix-proposal-v2", "recommend.safe-fix-plan", "verify.outputs.lifecycle-summary", "verify.post-fix"], "supports_fix_pipeline": true, "supports_verify_pipeline": true, "supports_export_pipeline": false}
```

### runtime.plugin-runtime-status

- category: `diagnostics`
- source_plugin: `runtime`

```
{"status": "healthy", "runtime_version": "6.0.0", "active_plugins": 3, "rejected_plugins": 0, "disabled_plugins": 0, "duplicate_plugins": 0, "essential_plugins": {"status": "healthy", "runtime_version": "6.0.0", "essential_plugin_ids": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "active": ["fixer.safe-runtime-actions", "recommender.safe-fix-plan", "verifier.post-fix-verifier"], "missing": [], "rejected": [], "disabled": [], "duplicate": [], "healthy": true, "required_capabilities": {"fixer.safe-runtime-actions": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "recommender.safe-fix-plan": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "verifier.post-fix-verifier": ["verify.post-fix", "verify.outputs.lifecycle-summary"]}, "capability_status": {"fixer.safe-runtime-actions": {"required": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "declared": ["fix.apply.safe-runtime-actions", "lifecycle.transaction-aware"], "missing": [], "satisfied": true}, "recommender.safe-fix-plan": {"required": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "declared": ["recommend.safe-fix-plan", "recommend.outputs.fix-proposal-v2"], "missing": [], "satisfied": true}, "verifier.post-fix-verifier": {"required": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "declared": ["verify.post-fix", "verify.outputs.lifecycle-summary"], "missing": [], "satisfied": true}}, "missing_capa
```

### runtime.target-topology

- category: `system`
- source_plugin: `runtime`

```
[{"name": ".capatch", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\.capatch", "is_dir": true, "size": null}, {"name": "__pycache__", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\__pycache__", "is_dir": true, "size": null}, {"name": "_chatgpt_fix_backups", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\_chatgpt_fix_backups", "is_dir": true, "size": null}, {"name": "_chatgpt_fix_logs", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\_chatgpt_fix_logs", "is_dir": true, "size": null}, {"name": "_chatgpt_patch_backups", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\_chatgpt_patch_backups", "is_dir": true, "size": null}, {"name": "capatch_audit", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_audit", "is_dir": true, "size": null}, {"name": "capatch_cli", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_cli", "is_dir": true, "size": null}, {"name": "capatch_contracts", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_contracts", "is_dir": true, "size": null}, {"name": "capatch_diagnostics", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_diagnostics", "is_dir": true, "size": null}, {"name": "capatch_engine", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_engine", "is_dir": true, "size": null}, {"name": "capatch_fs", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_fs", "is_dir": true, "size": null}, {"name": "capatch_ops", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_ops", "is_dir": true, "size": null}, {"name": "capatch_plugins", "path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\capatch_plugins"
```

### runtime.log-candidates

- category: `logs`
- source_plugin: `runtime`

```
[{"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\_chatgpt_fix_logs\\fix_capatch_warn.log", "size": 1454}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\_chatgpt_patch_backups\\README.txt", "size": 90}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\bundles\\support_bundle.json", "size": 75506}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\bundles\\support_bundle.md", "size": 13530}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\bundles\\support_bundle_v2.json", "size": 3973}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\bundles\\support_bundle_v2.md", "size": 358}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\checkpoints\\session_20260410_135131.json", "size": 745}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\checkpoints\\session_20260410_135134.json", "size": 747}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\confidence\\confidence_summary.json", "size": 95}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\confidence\\confidence_summary.md", "size": 54}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\decision_ledger\\diag_20260410_003448_decision_ledger.json", "size": 289}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\decision_ledger\\diag_20260410_003448_decision_ledger.md", "size": 358}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\decision_ledger\\diag_20260410_003451_decision_ledger.json", "size": 749}, {"path": "F:\\repos\\hitech-os\\apps\\code-atlas\\capatch_system\\reports\\decision_ledger\\diag_20260410_003
```

### runtime.log-tail-sample

- category: `logs`
- source_plugin: `runtime`
- path: `F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_logs\fix_capatch_warn.log`

```
[INFO] Root: F:\repos\hitech-os\apps\code-atlas\capatch_system
[INFO] Log: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_logs\fix_capatch_warn.log
[INFO] Backup: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_backups\fix_capatch_warn_20260410_161354
[INFO] Backup creado: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_backups\fix_capatch_warn_20260410_161354\capatch_legacy.py
[INFO] Backup creado: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_backups\fix_capatch_warn_20260410_161354\capatch_cli\commands_patch.py
[INFO] changed: F:\repos\hitech-os\apps\code-atlas\capatch_system\capatch_legacy.py :: Se agrego warn() a capatch_legacy.py
[INFO] changed: F:\repos\hitech-os\apps\code-atlas\capatch_system\capatch_cli\commands_patch.py :: Se agrego _legacy_warn(); Se reemplazaron 3 llamada(s) a capatch_legacy.warn
[OK] Syntax OK: F:\repos\hitech-os\apps\code-atlas\capatch_system\capatch_legacy.py
[OK] Syntax OK: F:\repos\hitech-os\apps\code-atlas\capatch_system\capatch_cli\commands_patch.py
[OK] Import OK: capatch_legacy.warn callable
[OK] Import OK: capatch_cli.commands_patch._legacy_warn callable
[OK] Fix aplicado correctamente.
[INFO] Backup disponible en: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_backups\fix_capatch_warn_20260410_161354
[INFO] Log disponible en: F:\repos\hitech-os\apps\code-atlas\capatch_system\_chatgpt_fix_logs\fix_capatch_warn.log
```
