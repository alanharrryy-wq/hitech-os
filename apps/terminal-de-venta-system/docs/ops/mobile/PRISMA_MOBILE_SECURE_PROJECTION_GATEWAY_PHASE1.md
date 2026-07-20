# PRISMA Mobile Secure Projection Gateway Phase 1

**Package:** `MOBPROJ1_SECURE_PROJECTION_GATEWAY_PHASE1`
**Classification:** `VERIFY`
**Source status after focused validation:** `LOCAL_VERIFIED_PENDING_RUNTIME_SESSION_E2E`

## Scope

This phase hardens Mobile runtime 3140 without redesigning frozen Mobile surfaces.

It provides:

- a signed-session verification boundary for production;
- a loopback-only development context outside production;
- server-authorized tenant, business, branch, terminal, device, license and actor context;
- permission checks for every existing `/api/mobile/*` data route;
- five governed read-model endpoints;
- sanitized upstream diagnostics;
- memory-only operational fallback;
- removal of authority from snapshot query parameters.

## Production behavior

Production fails closed when an authenticated signed Mobile session is absent,
invalid, expired or unsupported.

Session issuance is intentionally not invented here. The existing Customer Setup
capability remains source-ready/local-verified, while hosted session issuance is
an external/runtime gate.

## Development behavior

Outside production, requests are accepted only on loopback hosts. The context is
explicitly labeled `development-loopback`, has read-only permissions and cannot
be used as production evidence.

Set `PRISMA_MOBILE_DEV_LOOPBACK_CONTEXT=disabled` to test fail-closed behavior in
development.

## Phase 1 read models

- `RM.SYSTEM.SUMMARY`
- `RM.DATA.READINESS`
- `RM.SYNC.SOURCE_HEALTH`
- `RM.BUSINESS.EXECUTIVE_SUMMARY`
- `RM.SALES.SUMMARY`

## Cache

The legacy key `prisma.mobile.snapshot.v18` is purged. Full operational snapshots
are not written to persistent browser storage. A bounded in-memory fallback may
be used for the current tab only and is always marked stale.

## Mutations

No mutation path is added. No approve/reject, sync recovery, device claim,
license operation or queued offline command becomes authorized by this phase.

## Evidence boundary

Static/focused verification and TypeScript validation prove source integration.
They do not prove:

- a hosted live identity/session issuer;
- LAN or cloud reachability;
- production license/device claim;
- runtime browser auth E2E;
- offline capability;
- zero-custody runtime certification;
- any Mobile mutation.
