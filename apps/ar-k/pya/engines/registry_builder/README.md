# registry_builder

Purpose: Consolidate signals into canonical registries, indices, snapshots, and deltas.

Stage: `registry`
Reads: `signals`
Writes: `module_registry, boundary_registry, contract_registry, switch_registry, query_index, snapshots, deltas`

Forbidden moves:
- do not write outside declared ownership
- do not invent new states
- do not alter system or kernel without explicit review
