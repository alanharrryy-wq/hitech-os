# CONTRACT INDEX

## Purpose

Track contract definitions that are registered or pending in the phase-2 runtime.

## Wave-1 baseline

Source seed:

- `INITIAL_CONTRACT_SET.md`

## Runtime registration status

| Contract ID | Family | Owner | Status |
| --- | --- | --- | --- |
| `forge.lifecycle.package.register.v1` | lifecycle | forge_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.lifecycle.product.activate.v1` | lifecycle | forge_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.lifecycle.product.suspend.v1` | lifecycle | forge_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.lifecycle.package.dispose.v1` | lifecycle | forge_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.state.slice.publish.v1` | state | state_slice_owner | REGISTERED_AT_BOOTSTRAP |
| `forge.state.slice.snapshot.v1` | state | state_slice_owner | REGISTERED_AT_BOOTSTRAP |
| `forge.command.host.slot_bind.v1` | command | forge_kernel_host_shell | REGISTERED_AT_BOOTSTRAP |
| `forge.command.host.slot_unbind.v1` | command | forge_kernel_host_shell | REGISTERED_AT_BOOTSTRAP |
| `forge.event.package.faulted.v1` | event | runtime_owner | REGISTERED_AT_BOOTSTRAP |
| `forge.event.process.state_changed.v1` | event | commons_process_execution | REGISTERED_AT_BOOTSTRAP |
| `forge.contribution.surface.register.v1` | contribution | product_owner_and_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.contribution.action.invoke.v1` | contribution | product_owner_and_kernel | REGISTERED_AT_BOOTSTRAP |
| `forge.capability.process.execute.v1` | capability_service | commons_process_execution | REGISTERED_AT_BOOTSTRAP |
| `forge.capability.runs.append.v1` | capability_service | commons_history_runs | REGISTERED_AT_BOOTSTRAP |
| `forge.persistence.store.migrate.v1` | persistence | store_owner | REGISTERED_AT_BOOTSTRAP |
| `forge.packaging.package.validate.v1` | packaging | forge_kernel_packaging | REGISTERED_AT_BOOTSTRAP |
| `forge.compatibility.package.check.v1` | compatibility | package_owner_and_kernel | REGISTERED_AT_BOOTSTRAP |

Schema mapping source:

- `F:/repos/hitech-os/forgeos/governance/schemas/contract_schema_index.json`

## Rule

No cross-layer interaction is allowed without a contract entry in this index and runtime validation path.
