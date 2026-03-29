# PHASE2 CONTRACT REGISTRATION REPORT

## Runtime snapshot

- Kernel bootstrap contract count: `17`
- Source command:
  - `$env:PYTHONPATH='src'; python -` with `KernelBootstrap.start().contracts.known_contracts()`

## Registered contracts

| Contract ID | Family | Owner | Version |
| --- | --- | --- | --- |
| `forge.capability.process.execute.v1` | capability_service | commons_process_execution | v1 |
| `forge.capability.runs.append.v1` | capability_service | commons_history_runs | v1 |
| `forge.command.host.slot_bind.v1` | command | forge_kernel_host_shell | v1 |
| `forge.command.host.slot_unbind.v1` | command | forge_kernel_host_shell | v1 |
| `forge.compatibility.package.check.v1` | compatibility | package_owner_and_kernel | v1 |
| `forge.contribution.action.invoke.v1` | contribution | product_owner_and_kernel | v1 |
| `forge.contribution.surface.register.v1` | contribution | product_owner_and_kernel | v1 |
| `forge.event.package.faulted.v1` | event | runtime_owner | v1 |
| `forge.event.process.state_changed.v1` | event | commons_process_execution | v1 |
| `forge.lifecycle.package.dispose.v1` | lifecycle | forge_kernel | v1 |
| `forge.lifecycle.package.register.v1` | lifecycle | forge_kernel | v1 |
| `forge.lifecycle.product.activate.v1` | lifecycle | forge_kernel | v1 |
| `forge.lifecycle.product.suspend.v1` | lifecycle | forge_kernel | v1 |
| `forge.packaging.package.validate.v1` | packaging | forge_kernel_packaging | v1 |
| `forge.persistence.store.migrate.v1` | persistence | store_owner | v1 |
| `forge.state.slice.publish.v1` | state | state_slice_owner | v1 |
| `forge.state.slice.snapshot.v1` | state | state_slice_owner | v1 |

## Schema coverage

- Contract schema index:
  - `F:/repos/hitech-os/forgeos/governance/schemas/contract_schema_index.json`
- Coverage test:
  - `platform/forge_kernel/tests/test_contract_schema_coverage.py`
- Result:
  - Wave-1 contracts are mapped 1:1 to schema files.
