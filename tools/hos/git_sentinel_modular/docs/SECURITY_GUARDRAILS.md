# Security Guardrails

## Non-negotiables

1. Do not delete or rewrite the legacy package as part of the initial modularization pass.
2. Do not switch production or daily runtime imports to the modular package until scan-only parity exists.
3. Cleanup and repair flows must remain opt-in and behind explicit flags.
4. Any future `.gitignore` mutation logic must live behind contracts and tests.
5. Any function that can move, quarantine or delete files must document its path constraints.

## Safe first moves

- isolate pure functions
- isolate config parsing
- isolate git helpers
- isolate report serialization
- isolate prediction logic that does not mutate state

## Unsafe first moves

- dashboard rewiring before core interfaces stabilize
- automatic import rewrites across the repo
- changing cleanup defaults during the same pass as file moves
