# PRISMA Sync Closure Patch 20260518

Status: PARTIAL until local runtime gates pass.

This patch closes the first Tablet to PC sync gap without changing the Tablet sale path. Tablet remains local-first. PC governance is optional. Mobile remains supervision-only.

## Feature flags

All runtime dispatch features are off by default:

- `PRISMA_TABLET_PC_SYNC_ENABLED=false`
- `PRISMA_TABLET_SYNC_AUTODISPATCH=false`
- `PRISMA_TABLET_PC_ORIGIN` empty by default
- `PRISMA_TABLET_SYNC_ACK_STRICT=true`

## No fake green rule

Mobile must not count `sent` or `synced` as ACK. Only `acked` is acknowledged. Anything else is partial, stale, pending, failed or conflict until proven by remote metadata.

## Runtime status

NEEDS_RUNTIME_TEST:

- PC unavailable sale remains local and successful.
- PC returns and Tablet dispatches pending events.
- PC ingest dedupes replay and duplicate dispatch.
- Tablet stores `remoteLedgerId`, `remoteLifecycleStatus`, diagnostics and ACK timestamps.
- Mobile shows honest pending/failed/conflict/acked state.

## Non-goals in this patch

- Full projector implementation for all recognized topics.
- Public-network auth/rate-limit policy.
- Destructive DB migration apply.
- Shader, WebGL, chart-lab or prisma-charts work.
