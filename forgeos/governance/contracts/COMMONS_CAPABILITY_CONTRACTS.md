# COMMONS CAPABILITY CONTRACTS

## Scope

Contract ownership and status for phase-3 Forge Commons capabilities.

## Capability mapping

| Capability | Contract ID | Status | Owner |
| --- | --- | --- | --- |
| `forge.commons.config_policy` | `forge.capability.config.resolve.v1` | planned | forge_commons_config_policy |
| `forge.commons.config_policy` | `forge.capability.config.override.apply.v1` | planned | forge_commons_config_policy |
| `forge.commons.diagnostics` | `forge.capability.diagnostics.emit.v1` | planned | forge_commons_diagnostics |
| `forge.commons.diagnostics` | `forge.capability.diagnostics.health_snapshot.v1` | planned | forge_commons_diagnostics |
| `forge.commons.process_execution` | `forge.capability.process.execute.v1` | registered | forge_commons_process_execution |
| `forge.commons.process_execution` | `forge.event.process.state_changed.v1` | registered | commons_process_execution |
| `forge.commons.history_runs` | `forge.capability.runs.append.v1` | registered | forge_commons_history_runs |
| `forge.commons.history_runs` | `forge.capability.runs.query.v1` | planned | forge_commons_history_runs |
| `forge.commons.export_artifacts` | `forge.capability.export.bundle.v1` | planned | forge_commons_export_artifacts |
| `forge.commons.export_artifacts` | `forge.capability.export.manifest.write.v1` | planned | forge_commons_export_artifacts |

## Rule

Only contract bindings marked as `registered` are allowed for runtime execution.
`planned` contracts must be registered and schema-backed before activation paths use them.
