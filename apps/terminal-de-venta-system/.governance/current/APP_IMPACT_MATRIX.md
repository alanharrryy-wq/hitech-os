# PRISMA App Impact Matrix

Task: consolidate PRISMA Mobile product-interface specifications into one canon.

| Surface | Applies | Mutation allowed | Mutation type | Reason |
| --- | --- | --- | --- | --- |
| Mobile | yes | yes | documentation/specification only | User explicitly requested one aspirational Mobile interface canon and removal of competing specifications. |
| Tablet | no | no | none | Tablet role is referenced only as a boundary. |
| PC | no | no | none | PC role is referenced only as a boundary. |
| Shared UI | no | no | none | No component or shared visual mutation. |
| Shared Core | no | no | none | No business/runtime mutation. |
| Chart Lab | no | no | none | No chart-lab mutation. |
| Control Center | no | no | none | No control-center mutation. |
| Database / Sync | no | no | none | No schema, DB, sync, outbox, ACK, checkpoint or conflict mutation. |
| Licensing | no | no | none | No license behavior mutation. |
| Quality | read-only authority | no | none | Contracts read for truthfulness/no-fake-green boundaries only. |
| Governance | yes | yes | task-exact mesh/evidence only | Required by Factory Ledger and Authority Mesh rules. |

## Protected roots

No files under Mobile `app/`, `src/`, `public/`, `scripts/`, runtime infra, API routes, package scripts, verifier code, Tablet, PC, Shared UI, Shared Core, DB/schema/migrations, Chart Lab, or Control Center are authorized for product-code mutation by this task.
