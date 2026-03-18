# 58_MUTATION_CLIENT_PACKAGE_DECISIONS

## Decisions
1. Keep mutation-client separate from the bridge.
2. Keep adapter routing explicit instead of magical registry-only resolution.
3. Model preview sessions as named state, not incidental UI memory.
4. Keep commit, discard, and revert as separate pathways.
5. Emit diagnostics for both success and failure.
6. Prefer a small typed mutation surface over a giant universal payload.
