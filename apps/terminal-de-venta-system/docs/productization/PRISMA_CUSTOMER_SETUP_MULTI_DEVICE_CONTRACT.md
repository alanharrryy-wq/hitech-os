# Prisma Customer Setup Multi-Device Contract

## Purpose

Prisma Customer Setup is the customer onboarding flow for a package with Tablet, PC, and Mobile. It is not a confirmed admin license operation and it never uses `ADMIN_TOKEN` in customer-facing apps.

## Operator Flow

When a client buys Tablet + PC + Mobile:

1. Admin creates the customer/package in Prisma Cloud Center.
2. Admin chooses customer + plan once.
3. Prisma creates license, license assignment, setup bundle, Setup Link, Setup Code, and Setup QR.
4. Prisma creates device claim slots automatically from plan limits.
5. Customer opens setup on Tablet, PC, and Mobile.
6. Each app claims its own prepared Device Slot.
7. Local license state is stored safely.
8. Refresh/status keeps devices in sync.
9. Support sees sanitized setup evidence.

## Canonical Names

- Prisma Customer Setup
- Setup Pass
- Setup Link
- Setup Code
- Setup QR
- Device Claim
- Device Slots
- Tablet POS Slot
- PC Admin Slot
- Mobile Companion Slot

## Shared Contract

Canonical source module:

```text
shared/licensing/customer-setup-contract.ts
```

The module exports:

- `CustomerSetupSurface = "tablet" | "pc" | "mobile"`
- `CustomerSetupPass`
- `CustomerSetupSlot`
- `PlanProvisioningDefinition`
- `DeviceClaimSlot`
- `PlanBasedProvisioningResult`
- `DeviceClaimRequest`
- `DeviceClaimResponse`
- `CustomerSetupErrorCode`
- `PRISMA_TRIPLE_DEVICE_STARTER`

Default package:

```json
{
  "packageCode": "PRISMA_TRIPLE_DEVICE_STARTER",
  "planCode": "TABLET_PC_MOBILE_MANAGED",
  "slots": {
    "tablet": 1,
    "pc": 1,
    "mobile": 1
  }
}
```

## Cloud License Gateway Source

Source-only endpoints:

```text
POST /api/admin/customer-setups/create
GET  /api/customer/setup/:setupCode
POST /api/customer/devices/claim
GET  /api/customer/license/status?setupCode=...&deviceId=...
```

Source migration:

```text
infra/cloudflare/licflow3-worker/migrations/0002_customer_setup.sql
infra/cloudflare/licflow3-worker/migrations/0003_plan_based_provisioning.sql
```

`0002_customer_setup.sql` is the historical Customer Setup base. Plan-based provisioning is additive in `0003_plan_based_provisioning.sql`; do not rewrite `0002` unless repository evidence proves it is still a draft.

Do not deploy or run D1 without explicit authorization.

## Plan-Based Provisioning

Plan provisioning uses `PLAN_BASED_PROVISIONING_CATALOG` in `shared/licensing/customer-setup-contract.ts` and the matching Cloud License Gateway plan catalog. The one-shot create route produces `licenseId`, `licenseAssignmentId`, `setupBundleId`, `setupCode`, `setupLink`, `setupQrPayload`, prepared `deviceClaimSlots`, and `auditEventId`.

Acceptance gates:

- `manualDeviceClaimRequired = false`
- `operatorActionCount = 1`
- plan -> slots comes from max devices per surface
- claims consume existing slots, not manual per-device claim records
- consumed claims cannot exceed surface limits
- every prepared slot carries surface, status, claim code, expiration, license, plan, and audit

## Surface Rules

- Tablet uses surface `tablet` and claims `Tablet POS Slot`.
- PC uses surface `pc` and claims `PC Admin Slot`.
- Mobile uses surface `mobile` and claims `Mobile Companion Slot`.
- No customer-facing app asks for or stores `ADMIN_TOKEN`.
- Device replacement is not silent; return a human message and require support/admin flow.

## Error Shape

Every customer setup error includes:

```json
{
  "customerMessage": "...",
  "nextStep": "...",
  "secretsExposed": false
}
```

Required customer-safe errors include `SETUP_CODE_REQUIRED`, `SETUP_NOT_FOUND`, `SETUP_EXPIRED`, `SETUP_REVOKED`, `DEVICE_SLOT_FULL`, `DEVICE_ALREADY_CLAIMED`, `DEVICE_REPLACEMENT_REQUIRED`, `SURFACE_NOT_ALLOWED`, and `CUSTOMER_SETUP_UPSTREAM_FAILED`.

## Source-Ready Boundary

Current source can represent and validate the flow locally. Live customer use requires authorized Cloud License Gateway deploy and D1 migration. Do not report hosted PASS until those are authorized and verified.
