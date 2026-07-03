# LICFLOW3 Route Map

- Target base: `https://app.hitechrts.com`
- Worker source: `infra/cloudflare/licflow3-worker/src/worker.js`
- Contract source: `shared/licensing/licflow3-cloud-contract.ts`

| Route | Method | Contract key | Local handler | Expected dummy evidence | Live status before patch |
|---|---|---|---|---|---|
| `/api/licenses/activate` | `POST` | `licenseActivate` | `activateLicense(request, env, "activate")` | `401 ADMIN_TOKEN_REQUIRED` without admin token, or another structured non-404 contract rejection | `404 not_found` |
| `/api/licenses/refresh` | `POST` | `licenseRefresh` | `activateLicense(request, env, "refresh")` | `401 ADMIN_TOKEN_REQUIRED` without admin token, or another structured non-404 contract rejection | `404 not_found` |
| `/api/licenses/revoke` | `POST` | `licenseRevoke` | `activateLicense(request, env, "revoke")` | `401 ADMIN_TOKEN_REQUIRED` without admin token, or another structured non-404 contract rejection | `404 not_found` |

## Handler flow

1. Match `POST` route in `route(request, env)`.
2. Call `adminRequired(request, env)`.
3. If `PRISMA_ADMIN_TOKEN` is absent or not supplied, return structured `401`.
4. If authorized, require `PRISMA_LICFLOW3_D1`.
5. If D1 is missing, return structured binding-required status.
6. If authorized and D1-bound, write license intent/audit event. Real signed issuance remains outside this scaffold.

## Non-goals

- Do not turn dummy smoke into real activation.
- Do not print or read admin token values.
- Do not copy/export D1.
- Do not auto-deploy.
