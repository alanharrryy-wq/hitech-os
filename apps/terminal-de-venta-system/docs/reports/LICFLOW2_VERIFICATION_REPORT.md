# LICFLOW2 Verification Report

Generated: 2026-07-02

Evidence root for the clean run:

```text
F:\descargasf\licflow2-result-20260702-014703
```

## Final Verifier Exit Codes

| Command | Exit code |
| --- | ---: |
| `node --check tools/provision-prisma-runtime.mjs` | 0 |
| `python -m py_compile Prisma Cloud Ctr/internal/py/license_ops_api.py` | 0 |
| `pnpm run verify:licflow2:inventory` | 0 |
| `pnpm run verify:licflow2:offline` | 0 |
| `pnpm run verify:licflow2:online` | 0 |
| `pnpm run verify:licflow2:hybrid` | 0 |
| `pnpm run verify:licflow2:support` | 0 |
| `pnpm run verify:licflow2:no-duplicates` | 0 |
| `pnpm run verify:licflow2:no-secrets` | 0 |
| `pnpm run verify:licflow2:no-db-commit` | 0 |
| `pnpm run verify:licflow2:no-demo-leaks` | 0 |
| `pnpm run verify:licdesk:signing` | 0 |
| `pnpm run verify:licdesk:governor` | 0 |
| `pnpm run verify:licdesk:support` | 0 |
| `pnpm run verify:adlant4:sync-e2e` | 0 |
| `pnpm -C products/mobile/app typecheck` | 0 |

## Mode Evidence

- Offline generated a safe activation package ZIP and provisioned a Tablet runtime in evidence. Governor reported `active`, `TABLET_PC_MANAGED`, `assigned`, activation mode `OFFLINE_PACKAGE`.
- Online generated a local service-contract activation request/response with `hostedCloud: false` and provisioned a PC runtime in evidence. Governor reported `active`, `TABLET_PC_MANAGED`, `assigned`, activation mode `ONLINE_ACTIVATION`.
- Hybrid generated package evidence plus `hybrid-refresh-fallback.json`, then provisioned a Tablet runtime in evidence. Governor reported `active`, `TABLET_PC_MANAGED`, `assigned`, activation mode `HYBRID`.
- Support provisioned a Mobile runtime in evidence and verified Shell Lab activation summary plus Mobile activation account contract metadata.

## Safety Evidence

- `verify:licflow2:no-duplicates`: PASS. Only ADLANT4 owns Ed25519 key generation.
- `verify:licflow2:no-secrets`: PASS. No private-key blocks or secret-like filenames in LICFLOW2 evidence/implementation scan.
- `verify:licflow2:no-db-commit`: PASS. No tracked or dirty DB files in `apps/terminal-de-venta-system`.
- `verify:licflow2:no-demo-leaks`: PASS. No forbidden demo identifiers in LICFLOW2 implementation/evidence scan.

## Hosted Cloud Statement

LICFLOW2 `ONLINE_ACTIVATION` is a local loopback/operator-service contract (`POST /licenses/activate`). The implementation does not claim hosted cloud activation.
