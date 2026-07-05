# LICFLOW3 Cloudflare Worker Scaffold

This is the governed Worker source for `https://app.hitechrts.com` licensing/support endpoints.

It is aligned to the live Cloudflare resources confirmed for LICFLOW3:

- Worker: `prisma-cloud-semilla`
- D1: `prisma_cloud_semilla`

## Safety

- No deploy is performed by this scaffold.
- No DNS, route, or Tunnel config is included.
- No secret values are stored here.
- No local POS, Tablet, PC, or Mobile runtime is moved to cloud.
- LICFLOW2 remains the local/offline/hybrid activation authority.

## Expected Commands

Use package-local Wrangler only from this worker root:

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
- `POST /api/admin/customer-setups/create`
- `GET /api/customer/setup/:setupCode`
- `POST /api/customer/devices/claim`
- `GET /api/customer/license/status?setupCode=:setupCode&deviceId=:deviceId`

Mutating endpoints require `PRISMA_ADMIN_TOKEN` and a D1 binding. Without D1, they return an explicit binding-required status instead of fake success.

Customer setup resolve, claim, and status endpoints are customer-safe and use Setup Code, not the admin token. The source migration `0002_customer_setup.sql` is included for `customer_setups`, `customer_setup_slots`, and `customer_device_claims`; do not run it against live D1 without explicit authorization.

Dummy smoke without the admin token must return a structured non-404 rejection such as `401 ADMIN_TOKEN_REQUIRED`. A `404` for `/api/licenses/*` means the live Worker route table is stale or not running this source.
