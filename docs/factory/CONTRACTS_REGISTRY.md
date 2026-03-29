# Contracts Registry

STATUS: LAW

## Authority

- Contract registry source of truth: `tools/codex/contracts/factory/contracts_registry.json`
- Schema payload source of truth: `tools/codex/schemas/`

## Required Graph Schema Keys

`contracts_registry.json` must map:

- `gravity_report`
- `protected_nodes`
- `impact_cone_report`
- `dependency_diff`
- `dispatch_recommendations`

## Runtime Wiring

Current wiring points:

- schema lookup index: `tools/codex/factory/schemas.py` (`SCHEMA_INDEX`)
- bundle validation: `tools/codex/factory/contracts.py`

## Validation Reality

- `python tools/codex/factory_cli.py contracts-check` validates schema loading/registry integrity in supported environments.
- run-level canonical JSON validation is enforced in bundle validation/integration paths.

## Compatibility and Versioning

Graph-analysis schemas use semantic `schema_version` plus compatibility metadata:

- `compatibility_mode`
- `minimum_reader_version`
- `breaking_change`

Breaking changes must be documented and recorded in `docs/factory/CHANGES.md`.
