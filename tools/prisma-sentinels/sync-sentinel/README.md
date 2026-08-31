# PRISMA Sync Sentinel

Fail-closed, evidence-first verification tooling for the **existing** PRISMA Tablet ↔ PC synchronization architecture plus the governed **Mobile read-side runtime on canonical port 3140**.

The Sentinel orchestrates and proves existing product owners. It does **not** reimplement product business logic and it does not mutate Tablet, PC or Mobile source merely to satisfy tests. All runtime databases are Sentinel-owned temporary SQLite files and all spawned services are Sentinel-owned loopback processes.

## Canonical runtime topology

- Tablet product runtime: `3120`.
- PC product runtime: `3130`.
- Mobile product runtime: `3140`.
- Tablet/PC test transports may bind ephemeral loopback ports inside the disposable capsule.
- GitHub certification binds the real Mobile Next runtime to `3140` and fails closed if that canonical port is unexpectedly unavailable.

## Scope

- `scan`: authority/source presence plus native Tablet/PC sync and Mobile secure-projection verifiers.
- `diagnose`: HEAD/worktree/live-DB inventory without mutation.
- `doctor`: disposable dependency/Prisma/runtime preparation check.
- `e2e`: isolated Tablet/PC journeys plus Mobile runtime journeys and negatives.
- `certify`: full isolated Tablet/PC/Mobile certification, fixture readiness, native probes, safety guards, cleanup and sanitized evidence ZIP.
- `self-test`: fail-closed safety, Watch classification and evidence unit tests.

## Tablet / PC journeys

### Journey A

Real Tablet `dispatchTabletOutboxOnce` → Sentinel loopback transport → real PC `persistSyncIngestPayload` / projectors → real Tablet ACK reconciliation.

### Journey B

Real PC `exportPcCatalogDelta` → real Tablet `pullCatalogDeltaFromPc` / `applyCatalogDeltaEnvelope` / checkpoint, including the local-stock preservation invariant.

## Mobile journeys

### M1: canonical read projection

Real Tablet/PC source owners behind Sentinel loopback transports → Mobile data plane → signed-session secure projection gateway → real Mobile Next runtime → `GET /api/mobile/v1/read-models/sync-source-health` → final scoped projection.

The projection must prove `sourceRuntime: "3140"`, source owner `TABLET|PC`, signed-session authorization, tenant/business/branch/terminal/device/license/actor scope and the correct owner-derived outbox state.

### M2: owner change observed later

A synthetic event is written only to the Sentinel-owned Tablet database. A new HTTP read through Mobile `3140` must observe that changed owner state. Python does not calculate or substitute the product projection.

### M3: governed read-only boundary

`NOT_APPLICABLE` while `mobile.secure_projection_gateway_phase1` remains read-only and the canonical Mobile verifier reports `commandPathsEnabled=false`. A future mutating Mobile journey requires a separate governed mutation owner and fresh authority. Sentinel will not fabricate one.

## Mobile negative matrix

The runtime runner verifies signed-session rejection, expiry, permission denial, required license-contract shape, cross-business isolation, Tablet/PC source loss, retry, all-upstream fail-closed behavior, recovery, stale projection and malformed upstream payload handling. Boundaries that the current architecture does not own are recorded as `NOT_APPLICABLE` or `EXTERNAL_REQUIRED`, never as synthetic PASS.

## PRISMA Sync Sentinel Watch

`.github/workflows/prisma-sync-sentinel-watch.yml` classifies changed paths as `NONE`, `SCAN` or `CERTIFY` using `SYNC_SENTINEL_WATCH_CONTRACT.json`.

- `NONE`: clean skip without installing runtime dependency islands.
- `SCAN`: self-test + scan.
- `CERTIFY`: self-test + scan + diagnose + full isolated Tablet/PC/Mobile certify.
- Pull-request concurrency cancels obsolete runs of the same PR.
- Main certification is grouped by exact SHA, so a distinct canonical SHA never loses its evidence to cancellation.
- A weekly schedule forces full certification as a safety net.
- PASS stays quiet except for retained evidence. FAIL/BLOCKED/UNKNOWN stays red and writes causal localization to the Actions job summary.

## Safety invariants

- Temporary DB paths stay under the Sentinel-owned temp root.
- Customer/live DB mutation is forbidden and guarded.
- Only exact processes spawned by Sentinel may be terminated.
- No global process cleanup and no port-killing behavior.
- No product source modification merely to satisfy a test.
- No manifest or lockfile mutation to manufacture green.
- HEAD/source drift fails closed.
- `UNKNOWN` never passes.
- Evidence is sanitized before ZIP creation.
- `productionCertified=false` remains mandatory.

## Commands

```bash
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py self-test
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py scan --repo .
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py diagnose --repo .
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py certify --repo . --expected-head <sha> --evidence-dir tools/_local/reports/sync-sentinel
```

`certify` may generate Prisma clients only inside its disposable capsule and points all runtime database URLs to temporary files. It is not a hot-injection gate for live dev processes.
