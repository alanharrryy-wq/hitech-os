# Python Engines

Reserved workspace for future `.py` engines.

Recommended future modules:

- `governor_inventory_engine.py`
- `route_budget_audit_engine.py`
- `public_leak_sanitizer_engine.py`
- `visual_regression_engine.py`
- `recipe_compiler_engine.py`
- `runtime_adapter_validator.py`

Rules:

- Idempotent.
- Logs to `<OUTPUT_DIR>`.
- No fake green.
- Rollback or read-only by default.
- Protect POS, checkout, DB, package manifests and lockfiles.
