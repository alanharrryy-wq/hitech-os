# Ownership and Write Paths

Single-writer law:
- `signals` -> scanner
- `module_registry` -> registry_builder
- `boundary_registry` -> registry_builder
- `contract_registry` -> registry_builder
- `switch_registry` -> registry_builder
- `switch_resolutions` -> switch_engine
- `validation_report` -> contract_validator
- `annotations` -> ai_annotator
- `query_index` -> registry_builder
- `snapshots`, `deltas` -> registry_builder

Readers are declared but writers are sovereign and exclusive.
