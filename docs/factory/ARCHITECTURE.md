# Architecture

## Roles

- `A_core`: primary domain changes
- `B_tooling`: tooling, pipelines, guardrails, runtime automation, and infra-facing support
- `C_features`: product/features and operator/user surface ownership (UI/UX + visual behavior)
- `D_validation`: validation and hardening
- `Z_aggregator`: merge + consistency + report only

## Guarantees

- Worktrees isolate each worker.
- Scope locks prevent overlap.
- Z blocks integration on conflict.
- Run ledger tracks all runs.
- Z watch/ledger visibility is enabled by default.

