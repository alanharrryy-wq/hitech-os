# E2E_012_PLAN_BASED_CLIENT_ONBOARDING

## Purpose

Certify, by source and contract inspection only, that Prisma Customer Setup supports one-shot client onboarding by plan. The flow must create license, assignment, setup bundle, prepared device claim slots, and audit without requiring the operator to generate claims manually per device.

## Scope

Canonical files:

```text
shared/licensing/customer-setup-contract.ts
infra/cloudflare/licflow3-worker/src/worker.js
infra/cloudflare/licflow3-worker/migrations/0003_plan_based_provisioning.sql
tools/verify-customer-setup-multidevice.mjs
docs/ops/PRISMA_SUPREME_OPERATIONS_MAP.md
docs/productization/PRISMA_PLAN_BASED_CLIENT_ONBOARDING_MATRICES.md
```

No browser, no screenshots, no deploy, no D1 live operation, and no new runtime launch are part of this E2E.

## GIVEN

- The operator chooses customer + plan once.
- The plan comes from `PLAN_BASED_PROVISIONING_CATALOG`.
- Historical Customer Setup migration `0002_customer_setup.sql` remains unchanged.
- Additive migration `0003_plan_based_provisioning.sql` defines plan, assignment, bundle, and individual claim-slot tables.

## WHEN

`POST /api/admin/customer-setups/create` receives a customer and plan.

## THEN

- The worker resolves the plan.
- The worker creates or updates the license plan.
- The worker creates license and license assignment.
- The worker creates the setup bundle.
- The worker creates device claim slots from plan limits.
- The bundle carries setup code, setup link, setup QR payload, expiration, and audit id.
- The Worker emits sanitized `customer_setup.create` and `customer_setup.plan_based_provision` audit events.
- Tablet, PC, and Mobile claim against prepared slots.
- Claims cannot exceed per-surface plan limits.
- `manualDeviceClaimRequired = false`.

## Result

Expected read-only result:

```text
VERIFY_PLAN_BASED_PROVISIONING_READONLY
```

Result status:

```text
PASS when the verifier succeeds.
```

## Fail Conditions

FAIL if the operator must create claims manually by device, if plan -> slots is absent, if no setup bundle exists, if either `customer_setup.create` or `customer_setup.plan_based_provision` audit evidence is absent, if surface limits are not derived from the plan, or if a device claim can be made without license and plan linkage.
