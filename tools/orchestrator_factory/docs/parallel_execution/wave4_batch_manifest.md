# Wave 4 Batch Manifest

This batch implements the operational robustness layer for one-button v1.2.
It introduces lock semantics, idempotency key computation, session ledger reuse,
session manifest construction, canonical ZIP export, optional handoff copy, and
acceptance stub emission aligned to acceptance_result.schema.json.

## Scope
- session_lock.py
- session_idempotency.py
- session_ledger.py
- session_manifest.py
- session_export.py
- acceptance_stub.py
- session_paths.py (modified)
- session_cli.py (modified)
- session_flow.py (modified)
- one_button_session.py (modified)

## Out of Scope
- GUI plugin integration
- new dependencies
- full end-to-end tests (wave 5)
