# Wave 3 Batch Manifest

## Scope
This batch contains the runtime launcher core for the one-button motor v1.2.
It intentionally excludes lock handling, idempotency ledger reuse, canonical
ZIP export publication, and acceptance/export guardrails because those concerns
belong to wave 4.

## Included files
- tools/one_button.ps1
- tools/execution_framework/one_button_session.py
- tools/execution_framework/lib/session_cli.py
- tools/execution_framework/lib/session_flow.py
- tools/execution_framework/lib/session_state.py
- tools/execution_framework/lib/session_paths.py

## Behavioral guarantees
- Supports `existing_project` and `new_project`
- Supports policies `resume_latest_round`, `open_new_round`, and `upgrade`
- Supports `--dry-run` and `--non-interactive`
- Emits clear JSON status payloads with resolved paths
- Propagates Python exit codes through the PowerShell wrapper

## Known deferrals to wave 4
- project lock acquisition and stale detection
- idempotency key generation and ledger reuse
- canonical ZIP creation and sidecars
- session export validation and handoff copy publication
