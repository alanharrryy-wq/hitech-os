# PRISMA Sync Closure Patch 2026-05-18

## Classification

`FIX` for the Tablet POS → PC/Admin synchronization engine.

This document records the source-level closure performed under the Authority Mesh task generated on 2026-07-16. It does not declare production multi-device certification.

## Canonical flow

Tablet local operation → durable local business rows → Tablet OutboxEvent → canonical transport envelope → PC ingest → scope and integrity validation → idempotency and sequence gate → domain projector → PC canonical rows → per-event result → Tablet ACK/retry/conflict state → scoped checkpoint and observability.

## Source-level invariants

- The transport envelope is versioned.
- Tenant, business, store, terminal and device scope are explicit.
- Payload SHA-256 and batch checksum are validated.
- Identical idempotent retries are deterministic.
- Same idempotency key with a different payload becomes a conflict.
- Checkpoints advance only after accepted or duplicate outcomes.
- Rejected and conflicting events do not skip the stream.
- PC projection rows preserve Tablet origin inside the stored envelope.
- PC ledger source is classified as a canonical projection, not as a second POS origin.
- Cash sessions and cash movements emit canonical events.
- Returns preserve sale, line, stock and cash references.
- Timestamps are normalized before comparison.
- Device heartbeat and freshness are written by the canonical observability service.

## Safety

- No live business database is seeded, rewritten or migrated by the fix package.
- No process, port, browser, dev server, Prisma Generate or Git mutation is performed.
- Support Resolver remains excluded.
- Existing dirty working-tree files outside the authorized target set are preserved.
- No `!important` or visual override is introduced.

## Certification semantics

A passing source and fixture gate may emit `PASS_SYNC_ENGINE_INTEGRATION_CERTIFIED`.

Production remains `BLOCKED_REAL_MULTI_DEVICE_EVIDENCE_NOT_AVAILABLE` until real evidence proves:

- at least two independent Tablet-origin streams;
- row-level provenance into a canonical PC destination;
- scoped ACK and checkpoint continuity;
- no duplicate canonical facts;
- no cross-tenant leakage;
- and multiple PC readers when multi-PC support is claimed.
