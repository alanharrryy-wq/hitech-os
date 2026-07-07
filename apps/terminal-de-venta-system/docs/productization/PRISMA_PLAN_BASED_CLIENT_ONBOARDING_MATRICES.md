# PRISMA Plan-Based Client Onboarding Matrices

## Boundary

Plan-based onboarding extends Prisma Customer Setup. It does not introduce another customer setup module, another licensing gateway, or another Cloud Center. The operator chooses customer + plan once. The system creates license, assignment, setup bundle, setup link/code/QR, prepared device claim slots, and audit.

Verifier:

```text
VERIFY_PLAN_BASED_PROVISIONING_READONLY
```

E2E/spec/result:

```text
E2E_012_PLAN_BASED_CLIENT_ONBOARDING
```

## PLAN_PROVISIONING_MATRIX

| planId | planName | maxTabletDevices | maxPcDevices | maxMobileDevices | maxTotalDevices | allowedSurfaces | features | claimMode | autoGenerateSlots | requiresManualApproval | status | evidence |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| TABLET_SOLO | Tablet Solo | 1 | 0 | 0 | 1 | tablet | pos.local_sale, catalog.local, cash.local | auto_generated_claim_slots | true | false | SOURCE_READY | `PLAN_BASED_PROVISIONING_CATALOG.TABLET_SOLO` |
| TABLET_PRO | Tablet Pro | 2 | 0 | 1 | 3 | tablet, mobile | pos.local_sale, returns, outbox.visible, mobile.supervision | auto_generated_claim_slots | true | false | SOURCE_READY | `PLAN_BASED_PROVISIONING_CATALOG.TABLET_PRO` |
| TABLET_PC_MANAGED | Tablet + PC Managed | 2 | 1 | 1 | 4 | tablet, pc, mobile | pos.local_sale, pc.backoffice, sync.audit, mobile.supervision | auto_generated_claim_slots | true | false | SOURCE_READY | `PLAN_BASED_PROVISIONING_CATALOG.TABLET_PC_MANAGED` |
| TABLET_PC_MOBILE_MANAGED | Tablet + PC + Mobile Managed | 1 | 1 | 1 | 3 | tablet, pc, mobile | pos.local_sale, pc.backoffice, mobile.companion, customer.setup | auto_generated_claim_slots | true | false | SOURCE_READY | `PLAN_BASED_PROVISIONING_CATALOG.TABLET_PC_MOBILE_MANAGED` |

## SETUP_BUNDLE_MATRIX

| setupBundleId | clientId | tenantId | businessId | licenseId | planId | setupCode | setupLink | setupQrPresent | claimSlotsGenerated | tabletSlots | pcSlots | mobileSlots | expiresAt | createdBy | createdAt | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| `setupBundleId` | `customerId` | `tenantId` | `businessId` | `licenseId` | `planId` | `setupCode` | `setupUrl` | true | `buildDeviceClaimSlotsForPlan(plan).length` | `maxTabletDevices` | `maxPcDevices` | `maxMobileDevices` | `expiresAt` | licflow3-worker | `customer_setup_bundles.created_at` | active/source_ready | `upsertSetupBundle`, `customer_setup_bundles` |

The setup bundle also carries `licenseAssignmentId`, `setupQrPayload`, `operatorActionCount = 1`, `manualDeviceClaimRequired = false`, and `auditEventId`.

## DEVICE_CLAIM_SLOT_MATRIX

| slotId | setupBundleId | clientId | licenseId | planId | surface | claimCodePresent | deviceId | claimedAt | expiresAt | status | risk | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `slot_*_tablet_*` | `setupBundleId` | `customerId` | `licenseId` | `planId` | tablet | true | null until claimed | null until claimed | required | AVAILABLE/CLAIMED | blocked when maxTabletDevices is exceeded | `customer_device_claim_slots`, `maxTabletDevices` |
| `slot_*_pc_*` | `setupBundleId` | `customerId` | `licenseId` | `planId` | pc | true | null until claimed | null until claimed | required | AVAILABLE/CLAIMED | blocked when maxPcDevices is exceeded | `customer_device_claim_slots`, `maxPcDevices` |
| `slot_*_mobile_*` | `setupBundleId` | `customerId` | `licenseId` | `planId` | mobile | true | null until claimed | null until claimed | required | AVAILABLE/CLAIMED | blocked when maxMobileDevices is exceeded | `customer_device_claim_slots`, `maxMobileDevices` |

The claim path consumes prepared slots only. It does not create ad hoc claims per device. The worker checks an available slot by setup and surface, marks it CLAIMED, and updates the aggregate slot only with `claimed < allowed`.

## CLIENT_ONBOARDING_FLOW_MATRIX

| clientId | planId | licenseCreated | assignmentCreated | setupBundleCreated | claimSlotsCreated | qrCreated | auditCreated | operatorActionCount | manualDeviceClaimRequired | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `customerId` | `planId` | true | true | true | true | true | true | 1 | false | PLAN_BASED_CUSTOMER_ONBOARDING_READY | `createCustomerSetup`, `upsertLicense`, `upsertLicenseAssignment`, `upsertSetupBundle`, `upsertDeviceClaimSlot`, `recordAudit` |

Flow detail:

| phase | input | existing function | output | acceptance |
| --- | --- | --- | --- | --- |
| Plan selection | customer + plan | `resolveCustomerSetupPlan` | canonical plan definition | Operator chooses customer + plan once. |
| Setup pass | plan + customer | `buildSetupPass` | plan-aware setup pass | Includes plan, bundle id, license id, assignment id, slots. |
| Setup bundle | setup pass | `upsertSetupBundle` | setup bundle row | setup bundle exists before customer claims. |
| Claim slots | setup pass + plan | `buildDeviceClaimSlotsForPlan` | prepared claim slots | plan -> slots matches surface limits. |
| Tablet claim | setup code + tablet device | `claimCustomerDevice` | claimed tablet slot | Tablet consumes prepared slot. |
| PC claim | setup code + pc device | `claimCustomerDevice` | claimed pc slot | PC consumes prepared slot if plan allows pc. |
| Mobile claim | setup code + mobile device | `claimCustomerDevice` | claimed mobile slot | Mobile consumes prepared slot if plan allows mobile. |
| Audit create | setup payload | `recordAudit` | `customer_setup.create` | audit exists and carries sanitized setup creation evidence. |
| Audit provisioning | provisioning payload | `recordAudit` | `customer_setup.plan_based_provision` | audit exists and carries plan/license/bundle evidence. |

## PASS Rules

PASS requires `manualDeviceClaimRequired = false`, a real setup bundle, plan -> slots, license and license assignment linkage, per-surface limits, slot expiration, and audit. FAIL if a device claim can exist without license/plan linkage or if an operator still has to create claims manually one by one.
