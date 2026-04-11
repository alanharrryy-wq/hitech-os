# contract_validator

Purpose: Validate schema, references, and policy without rewriting canonical registries.

Stage: `validate`
Reads: `module_registry, boundary_registry, contract_registry, switch_registry, switch_resolutions, query_index`
Writes: `validation_report`

Forbidden moves:
- do not write outside declared ownership
- do not invent new states
- do not alter system or kernel without explicit review
