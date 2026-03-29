# INITIAL CONTRACT SET

This file defines the first contract IDs and versions that must exist before product migration.

## Naming convention

`forge.<family>.<scope>.<name>.v<major>`

Examples:

- `forge.lifecycle.product.activate.v1`
- `forge.command.host.slot_bind.v1`

## Contract seed (wave 1)

| ID | Family | Owner | Purpose |
| --- | --- | --- | --- |
| `forge.lifecycle.package.register.v1` | lifecycle | Forge Kernel | Register package with validated manifest and permissions. |
| `forge.lifecycle.product.activate.v1` | lifecycle | Forge Kernel | Activate product runtime in a host slot. |
| `forge.lifecycle.product.suspend.v1` | lifecycle | Forge Kernel | Suspend product without destructive teardown. |
| `forge.lifecycle.package.dispose.v1` | lifecycle | Forge Kernel | Ordered dispose with evidence. |
| `forge.state.slice.publish.v1` | state | Slice owner | Publish contract-safe state for authorized readers. |
| `forge.state.slice.snapshot.v1` | state | Slice owner | Snapshot state with schema version. |
| `forge.command.host.slot_bind.v1` | command | Forge Kernel Host Shell | Bind contribution to a shell slot. |
| `forge.command.host.slot_unbind.v1` | command | Forge Kernel Host Shell | Unbind contribution from a shell slot. |
| `forge.event.package.faulted.v1` | event | Runtime owner | Emit runtime fault with correlation and severity. |
| `forge.event.process.state_changed.v1` | event | Commons Process Execution | Emit process lifecycle transition. |
| `forge.contribution.surface.register.v1` | contribution | Product owner + Kernel validation | Register host contribution surface. |
| `forge.contribution.action.invoke.v1` | contribution | Product owner + Kernel mediation | Invoke contributed action through validated wiring. |
| `forge.capability.process.execute.v1` | capability_service | Commons Process Execution | Request process execution with timeout and kill policy. |
| `forge.capability.runs.append.v1` | capability_service | Commons History & Runs | Append run record with retention metadata. |
| `forge.persistence.store.migrate.v1` | persistence | Store owner | Run schema migration with explicit source and target versions. |
| `forge.packaging.package.validate.v1` | packaging | Forge Kernel Packaging | Validate manifest, integrity, and compatibility before activation. |
| `forge.compatibility.package.check.v1` | compatibility | Package owner + Kernel gate | Validate kernel/commons/product version ranges. |

## Validation minimum for each contract

- Owner
- Version
- Request schema
- Response schema (or event envelope schema)
- Error envelope
- Timeout/SLA (where applicable)
- Observability fields (contract id, correlation id, actor, outcome)

## Phase rule

No real product runtime may be activated until this wave exists in a contract registry and passes schema validation.
