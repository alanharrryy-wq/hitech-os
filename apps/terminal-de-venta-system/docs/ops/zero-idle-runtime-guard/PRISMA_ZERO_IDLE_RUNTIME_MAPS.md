# PRISMA Zero-Idle Runtime Guard Maps

Classification: `BUILD`  
Capability: `CAP.RUNTIME.ZERO_IDLE_GUARD`

## Ownership map

| Concern | Canonical owner | Scope |
|---|---|---|
| Certified Node runtime | `F:\PRISMA_CTX\RUNTIMES\node-v24.18.0-win-<arch>\node.exe` | Tablet 3120 and finite shadow certification only |
| Tablet process tree | `prisma-control-center/Fast Ignit/internal/zero_idle_guard.py` | Tablet 3120 only |
| Launch integration | `prisma-control-center/Fast Ignit/internal/fast_ignit.py` | Existing Fast Ignit controller |
| Browser error beacon | `products/tablet/app/instrumentation-client.ts` | Passive, once per browser session |
| Local evidence route | `products/tablet/app/app/api/runtime-evidence/chunk-load/route.ts` | Minimal local evidence |
| Contract and gates | `quality/contracts/PRISMA_ZERO_IDLE_RUNTIME_GUARD_CONTRACT.json` | Governance / Quality |

## Route map

| Route | Role | Phase |
|---|---|---|
| `/api/health` | Health 3/3 | Finite startup certification |
| `/`, `/pos` | Critical shell and selling flow | Finite warm-up |
| `/sales/today`, `/settings/export` | Protected Tablet Debt baseline | Finite warm-up |
| `/settings/license`, `/offline` | Protected ChunkCure baseline | Finite warm-up |
| `/api/runtime-evidence/chunk-load` | Minimal local ChunkLoad evidence | Passive event only |

## Process map

`Fast Ignit` creates the Tablet root suspended, assigns it to a Job Object, then
resumes the primary thread. Children inherit the Job. The root process handle
is registered with `RegisterWaitForSingleObject`; memory notifications arrive
through the Job completion port. Closing the last Job handle terminates the
owned tree. No process is selected by executable name.

The Node owner is resolved explicitly from the verified PRISMA portable runtime
before the Tablet command is built. The existing global Node installation is
not uninstalled and the global/user PATH is not modified. Tablet is launched
directly with the certified `node.exe` and Next CLI; the zero-important gate is
executed first with the same binary.

## Cache map

The fingerprint covers certified Node major/minor, Next version, Webpack,
`pnpm-lock.yaml`, Tablet `package.json`, `next.config.mjs`, `app/layout.tsx`,
and the imported generated visual runtime. Only `.next/dev` may move on
incompatibility. The destination is `F:\Trash-old\<run>\tablet-next-dev` with
`manifest.json`, `manifest.md`, hashes, original paths and rollback.

## Evidence map

| Evidence | Truth proved |
|---|---|
| Node bootstrap `manifest.json` | Official archive URL, architecture, archive hash, executable hash, exact version and no global PATH mutation |
| `runtime-certification.json` | Real Tablet shadow runtime: Webpack, route warm-up, current chunk 200/content, health 3/3, cold/steady Job memory |
| `sabotage-report.json` | EOL Node block, cache/chunk/memory policy, root wait and Job close |
| `overhead.json` | Incremental RAM/handles/threads/CPU and zero active HTTP after `CERTIFIED` |
| `chunkload-beacons.ndjson` | Minimal passive browser signal; no PII or sales data |
| `ROLLBACK.ps1` | Exact restoration from the run backup |

The installer never stops, frees, replaces or restarts the pre-existing owner
of port 3120. It certifies the real Tablet application on an ephemeral
loopback shadow port, closes only that Job, and records
`LOCAL_SHADOW_VERIFIED`. The installed Fast Ignit integration adopts port 3120
at the next user-controlled Tablet start. The shadow runtime uses a unique
`distDir`; it never shares or mutates the live `.next/dev`, and its generated
cache moves to `F:\Trash-old` after the finite run.

## Layer map

| Layer ID | Type | Owner | Runtime mutation |
|---|---|---|---|
| `LYR.RUNTIME.TABLET.3120.JOB` | Process boundary | Fast Ignit | Job membership only |
| `LYR.RUNTIME.TABLET.3120.STARTUP_CERT` | Finite probe layer | Zero-Idle certifier | Stops after `CERTIFIED` |
| `LYR.RUNTIME.TABLET.3120.CACHE_FP` | Cache compatibility | Zero-Idle guard | `.next/dev` only on mismatch |
| `LYR.RUNTIME.TABLET.3120.CHUNK_BEACON` | Passive evidence | Tablet instrumentation client | Event-triggered local POST |
| `LYR.RUNTIME.TABLET.3120.MEMORY_NOTICE` | Soft memory signal | Job completion port | No hard cold-build limit |
| `LYR.RUNTIME.TABLET.SHADOW.INSTALL_CERT` | Finite installer certification | Zero-Idle applicator | Ephemeral loopback port only; never mutates 3120 |
| `LYR.TOOLING.NODE24.PORTABLE` | Certified runtime prerequisite | PRISMA toolchain | Tablet-only executable selection; no global PATH mutation |

No visual CSS layer is added. PC, Mobile, Web, Chart Lab and Shared UI are
explicitly excluded.
