# PRISMA Sync Sentinel

Fail-closed, evidence-first verification tooling for the **existing** PRISMA Tablet ↔ PC synchronization architecture.

This tool is an orchestrator and evidence producer. It **does not reimplement business synchronization logic**. Runtime certification imports and exercises the existing Tablet dispatcher, PC ingest/projectors, PC catalog exporter, and Tablet catalog pull/apply/checkpoint code against **Sentinel-owned temporary SQLite databases**.

## Scope

- `scan`: authority/source presence plus native static sync verifiers.
- `diagnose`: HEAD/worktree/live-DB inventory without mutation.
- `certify`: isolated synthetic runtime Journey A + Journey B, native verifiers, drift checks, cleanup, evidence ZIP.
- `self-test`: fail-closed safety and evidence unit tests.

## Certification semantics

A successful isolated run prints `PASS_SYNC_CERTIFICATION` only when all required checks pass. It still records:

```text
productionCertified: false
```

because synthetic isolated evidence is not hosted/customer production evidence.

### Journey A

Real Tablet `dispatchTabletOutboxOnce` → loopback Sentinel test transport → real PC `persistSyncIngestPayload` / projectors → real Tablet ACK reconciliation.

### Journey B

Real PC `exportPcCatalogDelta` → real Tablet `pullCatalogDeltaFromPc` / `applyCatalogDeltaEnvelope` / checkpoint. The test also changes PC catalog stock after bootstrap and proves Tablet local operational stock is preserved while catalog name/price advance.

## Safety invariants

- Temporary DB paths must remain under the Sentinel-owned temp root.
- No customer/live DB is passed to Prisma runtime code.
- Only the exact process spawned by Sentinel may be terminated.
- No global process cleanup.
- No product/UI source mutation.
- HEAD/source drift during certification fails closed.
- Unknown verifier output is `UNKNOWN`, never PASS.
- Evidence is sanitized before ZIP creation.
- `productionCertified=false` is hard-coded for isolated certification.

## Commands

```bash
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py self-test
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py scan --repo .
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py diagnose --repo .
python tools/prisma-sentinels/sync-sentinel/prisma_sync_sentinel.py certify --repo . --expected-head <sha> --evidence-dir tools/_local/reports/sync-sentinel
```

`certify` may run Prisma generation only inside a clean isolated CI/test context and points all runtime database URLs to temporary files. It must not be used as a hot-injection gate against live dev processes.
