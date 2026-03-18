# 62_MUTATION_CLIENT_MIGRATION_STEPS

## Migration steps
1. route existing mutation-capable UI handlers through typed intent builders
2. introduce preview session state at the mutation-client seam
3. attach adapter routing helpers to actual bridge entrypoints
4. replace ad hoc compare logic with preview diff summaries
5. add rejection-path diagnostics
6. harden with tests around commit/discard/revert boundaries
