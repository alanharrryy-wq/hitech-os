# Code Atlas professional overview

> Compatibility filename retained for existing links and operator references.

The canonical current Code Atlas overview is now [`README.md`](README.md).

That document reflects the merged architecture after Universal Intelligence and Customer Wow V1:

```text
Universal Neutral Core
        ↓
Optional profiles / adapters
        ↓
Change Intelligence / Customer Wow
        ↓
Authority Pack → Human/Agent → Verify
        ↓
PASS / BLOCKED / UNKNOWN + evidence
```

The older description of Code Atlas primarily as a Python / Prisma / SQLite visual-forensic workspace is historical. Those PySide6, DB Glass, Visual Atlas, coverage and Todo El Show capabilities remain useful compatibility/engineering surfaces, but they no longer define the reusable architecture.

For current usage, neutrality rules, evidence boundaries and certification status, use:

- [`README.md`](README.md)
- [`NEUTRALITY_POLICY.md`](NEUTRALITY_POLICY.md)
- [`CODE_ATLAS_NEUTRALITY_CONTRACT.json`](CODE_ATLAS_NEUTRALITY_CONTRACT.json)
- [`docs/CODE_ATLAS_CUSTOMER_WOW_V1.md`](docs/CODE_ATLAS_CUSTOMER_WOW_V1.md)
- [`docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json`](docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json)
- [`docs/README.md`](docs/README.md)

For the PRISMA/hitech-os product adapter specifically, use the canonical operator runbook:

- [`../../apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md`](../../apps/terminal-de-venta-system/docs/ops/PRISMA_AUTHORITY_MESH_AUTOMESH_V2_RUNBOOK.md)

That PRISMA runbook documents relevant-drift revalidation when `main` moves, fast-path versus full-refresh behavior, artifact chaining/security, Git-blob/CRLF portability, visual Layer Map fail-closed rules and GitHub-only operation. Those rules are product-specific governance and must not be generalized into the neutral Code Atlas core by accident.

Current governed Code Atlas boundary remains `LOCAL_VERIFIED`, with broader but bounded external-repository evidence recorded. Independent evaluator replication remains externally blocked and human usefulness remains unmeasured. `certifiable=false` and `productionCertified=false` remain unchanged by this compatibility pointer or by AutoMesh v2 documentation.
