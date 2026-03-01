# Architecture

## Roles

- `A_worker`: primary domain changes
- `B_worker`: secondary surface and UX (default visual baseline owner)
- `C_worker`: tooling and infrastructure
- `D_worker`: validation and hardening
- `Z_integrator`: merge + consistency + report only

## Guarantees

- Worktrees isolate each worker.
- Scope locks prevent overlap.
- Z blocks integration on conflict.
- Run ledger tracks all runs.
- Z watch/ledger visibility is enabled by default.
