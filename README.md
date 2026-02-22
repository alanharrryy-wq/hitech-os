# HITECH_OS

Deterministic multi-agent factory monorepo foundation.

## Principles
- Deterministic execution and deterministic artifact ordering.
- No temporal dependencies in factory runtime logic.
- Strict worker isolation and explicit module boundaries.
- Feature flags default OFF.
- Evidence-driven outputs: report, diffs, file summaries, and validation traces.

## Monorepo Layout
```text
hitech-os/
  apps/
  packages/
  tools/
    create-worker.ts
  docs/
  configs/
    factory/
      feature-flags.json
      runtime.json
    tsconfig.factory.json
  factory/
    contracts/
      AgentInterface.ts
      BundleSchema.ts
      ExecutionReport.ts
      FactoryContracts.ts
    shared/
      DeterministicJson.ts
      Hashing.ts
      Immutability.ts
      Pathing.ts
    A_core/
      AgentRegistry.ts
      ContextGuard.ts
      CoreOrchestrator.ts
      DeterministicExecutor.ts
    B_tooling/
      ToolingPolicy.ts
    C_features/
      FeatureFlagRegistry.ts
    D_validation/
      SchemaValidator.ts
      SnapshotValidator.ts
      DeterminismAudit.ts
    Z_aggregator/
      ResultAggregator.ts
      FinalReportBuilder.ts
  scripts/
    run_factory_smoke.ps1
  tests/
    smoke/
      factory.e2e.test.ts
  package.json
  pnpm-workspace.yaml
  tsconfig.base.json
  .editorconfig
  .gitignore
```

## Factory Runtime Blocks
- `A_core`: orchestrator, deterministic executor, context and registry guards.
- `B_tooling`: deterministic tooling policy and smoke-plan shaping.
- `C_features`: feature-flag registry with OFF-by-default enforcement.
- `D_validation`: schema validation, snapshot consistency checks, determinism audit.
- `Z_aggregator`: deterministic result merge and `FINAL_REPORT.txt` builder.

## Deterministic Defaults
- Stable path sorting and canonical JSON serialization.
- Cross-worker mutable state is prevented through clone-and-freeze context handling.
- Temporal and non-deterministic API patterns are audited and blocked.
- Cross-module imports between worker blocks are audited and blocked.
- Feature flags are explicit and default to `false`.

## Commands
```bash
pnpm install
pnpm run factory:build
pnpm run factory:smoke
```

## Snapshot Mini
Generate the deterministic repository mini snapshot:
```bash
pnpm run snapshot:hos
```

Validate snapshot JSON against schema:
```bash
pnpm run snapshot:hos:validate
```

Windows smoke helper:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_factory_smoke.ps1
```

## Worker Generator
Generate a new worker scaffold under `factory/<WORKER_ID>/`:
```bash
pnpm run factory:create-worker -- --name E_observability --description "Observability worker"
```

Dry-run mode:
```bash
pnpm run factory:create-worker -- --name E_observability --dry-run
```
