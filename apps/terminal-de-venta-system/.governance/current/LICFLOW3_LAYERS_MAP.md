# LICFLOW3 Layers Map

- Task: Corregir POST `/api/licenses/activate`, `/api/licenses/refresh`, `/api/licenses/revoke` contra `https://app.hitechrts.com`.
- Generated: 2026-07-03
- Authority Mesh: `.governance/current/AUTHORITY_MESH_REPORT.md` status `PASS`.

## Layers

| Layer | Owner file / resource | Role | Mutation allowed now |
|---|---|---|---:|
| Public target | `https://app.hitechrts.com` | Live Cloudflare SaaS/licensing target. | no |
| Live Worker | `prisma-cloud-semilla` | Real Worker serving `app.hitechrts.com` today. | deploy requires explicit authorization |
| Live D1 | `prisma_cloud_semilla` | Real D1 database for Cloud Semilla metadata. | no DB copy/export; deploy binding only |
| Repo Worker source | `infra/cloudflare/licflow3-worker/src/worker.js` | Canonical local worker code for LICFLOW3 routes. | yes, minimal |
| Repo Worker config | `infra/cloudflare/licflow3-worker/wrangler.jsonc` | Deploy target and D1 binding metadata. | yes, must preserve real Worker/D1 |
| Contract source | `shared/licensing/licflow3-cloud-contract.ts` | Canonical LICFLOW3 endpoint contract. | only if contract changes |
| 3160 bridge | `Prisma Cloud Ctr/internal/config/cloud_saas.json` and `.../py/cloud_saas_api.py` | Operator read-only/redacted contract and diagnostics bridge. | only guarded diagnostics |
| Verifier | `tools/verify-licflow3.mts` | Local route/config/safety verifier. | yes |

## Current live observation

`/health` and `/api/public/capabilities` respond from `PRISMA Cloud Semilla` version `prcloud5-2026-06-23`. The three POST license endpoints respond structured `404`, which means the live Worker route table does not currently contain these handlers.

## Boundary

This task must not mutate DNS, Tunnel, D1 rows, secret values, Tablet POS autonomy, PC backoffice behavior, Mobile, Chart Lab, or LICFLOW2 local activation.
