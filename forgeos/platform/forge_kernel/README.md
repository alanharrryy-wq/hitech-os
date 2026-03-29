# forge_kernel

Kernel runtime workspace.

Phase ownership:

- Phase 1: kernel skeleton and lifecycle authority.
- Phase 2: contract runtime base.

Hard rule:

- No product semantics in kernel.

Current phase-1 modules:

- `src/forge_kernel/lifecycle_authority.py`
- `src/forge_kernel/slot_manager.py`
- `src/forge_kernel/state_authority_registry.py`
- `src/forge_kernel/packaging_gate.py`
- `src/forge_kernel/kernel_session.py`

Current phase-2 baseline modules:

- `src/forge_kernel/contract_runtime/models.py`
- `src/forge_kernel/contract_runtime/validator.py`
- `src/forge_kernel/contract_runtime/registry.py`
- `src/forge_kernel/contract_runtime/error_envelope.py`
- `src/forge_kernel/contract_runtime/observability.py`
- `src/forge_kernel/contract_runtime/wave1_catalog.py`

Boot behavior:

- `KernelBootstrap.start()` pre-registers the full wave-1 contract set.

Current phase-4 host shell modules:

- `src/forge_kernel/host_shell/models.py`
- `src/forge_kernel/host_shell/runtime.py`

Validation command:

```powershell
$env:PYTHONPATH='src;..\\forge_commons\\src;..\\..\\products\\dummy_product\\src'; python -m unittest discover -s tests -p "test_*.py"
```
