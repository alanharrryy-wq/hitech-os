# LICFLOW3 Ownership Map

| Concern | Owner | Files / resources | Rule |
|---|---|---|---|
| Live app target | Cloudflare Worker `prisma-cloud-semilla` | `https://app.hitechrts.com` | Preserve existing Worker; do not create a parallel worker. |
| Live database | D1 `prisma_cloud_semilla` | Cloudflare D1 metadata only | Preserve existing D1; no DB copy/export or destructive query. |
| Repo deploy config | LICFLOW3 worker scaffold | `infra/cloudflare/licflow3-worker/wrangler.jsonc` | Must point to real Worker/D1 for deploy-ready repair. |
| Route handlers | LICFLOW3 worker source | `infra/cloudflare/licflow3-worker/src/worker.js` | Add/connect POST handlers here only. |
| Contract truth | Shared licensing | `shared/licensing/licflow3-cloud-contract.ts` | Keep POST contract consistent with worker routes. |
| Operator diagnostics | Existing 3160 cockpit | `Prisma Cloud Ctr/**` | No parallel cockpit; no mutating autocalls. |
| Local/offline licensing | LICFLOW2 / ADLANT4 | `shared/licensing/licflow2-activation.ts`, `shared/licensing/adlant4-local-issuer.ts` | Do not duplicate or downgrade LICFLOW2. |
| Validation | LICFLOW3 verifier | `tools/verify-licflow3.mts` | Prove route contract locally and safety gates. |

## Current root-cause classification

`d) Pages/app handler distinto` and `f) mismatch entre scaffold prisma-licflow3-cloud-licensing y Worker real prisma-cloud-semilla` are the active findings. The local scaffold exports the three POST handlers, but the live Worker version currently serving `app.hitechrts.com` is older and returns `404`.
