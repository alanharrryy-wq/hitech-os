# Phase 1 V3 Calibration

V2 installed the PQOS foundation successfully, but the first `quality:commit` showed two expected calibration issues:

1. Boundary gates treated Tablet tools, verifiers and fixtures as runtime Tablet code.
2. Q13 flagged its own destructive-command regular expressions as dangerous commands.

V3 keeps Tablet Sovereignty strict for runtime files while downgrading tooling/doc/fixture references to evidence-only context.

Runtime Tablet files remain guarded under S0/S1. The following areas are non-blocking context unless a future policy explicitly marks them operational:

- `products/tablet/app/tools/**`
- `products/tablet/app/tools/fixtures/**`
- `products/tablet/app/docs/**`
- tests and verifier files

This is not weakening PQOS. It is separating the witness from the suspect.
