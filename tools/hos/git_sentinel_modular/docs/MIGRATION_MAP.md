# Migration Map

| Legacy file | Target file | Lines | Code-like | Funcs | Classes | Backup |
|---|---|---:|---:|---:|---:|:---:|
| `__init__.py` | `__init__.py` | 6 | 3 | 0 | 0 | no |
| `alerting.py` | `reporting/alerting.py` | 118 | 102 | 3 | 0 | no |
| `artifact_detector.py` | `scanning/artifacts.py` | 151 | 125 | 3 | 0 | no |
| `ci_gate.py` | `operations/ci_gate.py` | 121 | 102 | 3 | 0 | no |
| `cleanup_engine.py` | `remediation/cleanup.py` | 256 | 226 | 6 | 0 | no |
| `cli_sentinel.py` | `app/cli.py` | 253 | 227 | 4 | 0 | no |
| `config.py` | `shared/config.py` | 366 | 342 | 8 | 1 | no |
| `dashboard_app.py` | `app/dashboard.py` | 1652 | 1477 | 22 | 2 | no |
| `dashboard_app_backup_20260314_183939.py` | `legacy/dashboard_app_backup_20260314_183939.py` | 685 | 603 | 10 | 1 | yes |
| `execution_lock.py` | `operations/execution_lock.py` | 118 | 99 | 5 | 1 | no |
| `false_positive.py` | `shared/false_positives.py` | 303 | 263 | 13 | 1 | no |
| `git_utils.py` | `shared/git.py` | 224 | 195 | 13 | 0 | no |
| `ignore_manager.py` | `shared/ignore_rules.py` | 155 | 130 | 5 | 0 | no |
| `learning_engine.py` | `learning/engine.py` | 372 | 327 | 11 | 1 | no |
| `prediction_engine.py` | `analysis/prediction.py` | 226 | 205 | 8 | 1 | no |
| `repair_engine.py` | `remediation/repair.py` | 308 | 278 | 5 | 0 | no |
| `report_generator.py` | `reporting/generator.py` | 341 | 304 | 8 | 0 | no |
| `retention.py` | `shared/retention.py` | 130 | 111 | 4 | 0 | no |
| `scanner.py` | `scanning/repository.py` | 401 | 365 | 9 | 0 | no |
| `scheduler.py` | `operations/scheduler.py` | 165 | 146 | 4 | 1 | no |
| `security_quality.py` | `security/quality.py` | 191 | 162 | 8 | 0 | no |
| `security_scanner.py` | `security/scanner.py` | 238 | 203 | 8 | 0 | no |
| `sentinel.py` | `core/orchestrator.py` | 234 | 209 | 1 | 1 | no |
| `telemetry.py` | `shared/telemetry.py` | 94 | 82 | 3 | 0 | no |
| `utils.py` | `shared/utils.py` | 84 | 59 | 11 | 0 | no |
| `visualization.py` | `app/visualization.py` | 143 | 115 | 6 | 0 | no |

## Notes

- Backup files stay under `legacy/` only as reference.
- The generated stub files are placeholders, not runtime replacements.
- The legacy package can continue operating while migration happens in parallel.
