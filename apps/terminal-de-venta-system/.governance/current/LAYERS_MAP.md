# PRISMA Mobile Interface Authority Layer Map

Status: `PASS`

This Layer Map governs **interface authority**, not CSS/runtime z-index. No visual implementation mutation is authorized in this task.

| Layer | Authority | Role | Can override product-interface canon? |
| --- | --- | --- | --- |
| L0 | `PRISMA_MOBILE_INTERFACE_CANON.md` | Aspirational Mobile product-interface truth | yes, this is the canon |
| L1 | `PRISMA_MOBILE_INTERFACE_CANON_MIGRATION_20260825.md` | Migration, supersession, compatibility and rollback record | no |
| L2 | Mobile Atlas (`docs/atlas/**`) | Current implementation inventory, routes, components, interaction/runtime evidence | no |
| L3 | `PRISMA_MOBILE_FUTURE_EDIT_MAP.md` | Engineering ownership and edit hotspots | no |
| L4 | Mobile source/runtime | Current implementation truth and implementation drift evidence | no |
| L5 | API/data-plane/security/sync/PWA/release docs | Technical contracts and bounded readiness evidence | no |
| L6 | Mobile verifier scripts / QA corpora | Technical regression gates | no |
| L7 | Factory Ledger / Quality / Authority Mesh / Field Manual | Governance, anti-rework, truthfulness and safe-change constraints | constrains change process, but does not invent product IA |
| L8 | Git history / salvage / archived evidence | Historical recovery and provenance | no |

## Binding rules

- Product hierarchy and screen intent come only from L0.
- Current source differences at L4 are implementation drift, not an automatic update to L0.
- Atlas and Future Edit Map may describe old/current labels because they map implementation. They cannot become competing aspirational specifications.
- Technical verifier compatibility may keep a legacy doc path, but the file must be a non-authoritative pointer to L0.
- No lower layer may revive deleted navigation models by citation alone.

## Mutation scope

Allowed: L0/L1 documentation, legacy specification bodies, commercial wording alignment, and task-exact governance evidence.

Excluded: Mobile application/runtime, Tablet, PC, Shared UI, Shared Core, Chart Lab, Control Center, DB/schema/migrations, sync, licensing/auth, PWA behavior and verifier code.
