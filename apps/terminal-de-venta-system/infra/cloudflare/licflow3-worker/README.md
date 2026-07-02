# LICFLOW3 Cloudflare Worker Scaffold

This is the minimal governed scaffold for `https://app.hitechrts.com` licensing/support endpoints.

It was added because no canonical Worker, Pages Function, or D1 backend root for `app.hitechrts.com` was found in the active workspace.

## Safety

- No deploy is performed by this scaffold.
- No DNS, route, or Tunnel config is included.
- No secret values are stored here.
- No local POS, Tablet, PC, or Mobile runtime is moved to cloud.
- LICFLOW2 remains the local/offline/hybrid activation authority.

## Expected Commands

Use package-local Wrangler only:

```powershell
pnpm -C infra/cloudflare/licflow3-worker exec wrangler --version
pnpm -C infra/cloudflare/licflow3-worker exec wrangler whoami
```

Do not deploy without explicit authorization.

## Expected Bindings And Secret Names

Bindings:

- `PRISMA_LICFLOW3_D1`

Secret/env names:

- `PRISMA_ADMIN_TOKEN`
- `PRISMA_LICFLOW3_MODE`

Only names are documented. Values must be configured outside the repo.

## Implemented Contract Surface

- `GET /health`
- `GET /api/public/capabilities`
- `GET /api/public/tenants/:tenant/status`
- `GET /api/client/contract?tenant=:tenant`
- `POST /api/licenses/activate`
- `POST /api/licenses/refresh`
- `POST /api/licenses/revoke`
- `POST /api/devices/register`
- `POST /api/client/integration-receipt`
- `GET /api/support/diagnostics?tenant=:tenant`
- `GET /api/admin/selftest`
- `GET /api/admin/commercial-summary`
- `GET /api/admin/tenants/:tenant/snapshot`
- `POST /api/admin/tenants/:tenant/notes`

Mutating endpoints require `PRISMA_ADMIN_TOKEN` and a D1 binding. Without D1, they return an explicit binding-required status instead of fake success.
