# ForgeOS Reconstruction Workspace

This directory is the clean reconstruction workspace scaffolded from the ForgeOS foundation bundle.

Primary goals:

- Keep strict separation between `forge_kernel`, `forge_commons`, and `products`.
- Keep legacy as evidence, never as implementation template.
- Enforce contract-first execution and phase gates.

Top-level layout:

```text
forgeos/
├─ platform/
│  ├─ forge_kernel/
│  └─ forge_commons/
├─ products/
├─ governance/
│  ├─ contracts/
│  ├─ schemas/
│  ├─ matrices/
│  └─ decisions/
├─ packages/
└─ docs/
```

Execution entrypoint for this workspace:

- `RECONSTRUCTION_STATUS.md`
- `governance/decisions/PHASE0_TRUTH_CAPTURE.md`
- `governance/contracts/INITIAL_CONTRACT_SET.md`
- `docs/INDUSTRIALIZATION_PLAYBOOK.md`

Authoritative doctrine source remains under:

- `F:/repos/hitech-os/docs/forgeos-foundation/`
