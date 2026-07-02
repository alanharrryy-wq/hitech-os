# LICFLOW3 Legacy Do Not Use

Generated: 2026-07-02

These files may be useful history, but they are not LICFLOW3 authority unless a future task proves and promotes them.

## Licensing Legacy

| Path | Classification | Reason |
| --- | --- | --- |
| `tooling/licensing/server11*` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Historical server signing experiments. LICFLOW3 must reuse shared licensing and LICFLOW2/ADLANT4 authority instead. |
| `tooling/licensing/server06/mock_license_server.py` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Mock server; not hosted Cloudflare evidence. |
| `tooling/licensing/mock_license_server.py` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Mock helper; not production backend authority. |
| `tooling/licensing/dev-public-key.pem` | DOC_ONLY | Public-key fixture only; do not infer private signing setup. |
| `tooling/licensing/keys09/*` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Older key-management experiment. |
| `tooling/licensing/pro05/*` | LEGACY_DO_NOT_USE_WITHOUT_PROOF | Older productization contract; not LICFLOW3 authority. |

## Dangerous Local Launchers

| Path | Classification | Reason |
| --- | --- | --- |
| `prisma-control-center/00_KILL_ALL_LOCAL.cmd` | DANGER_DO_NOT_AUTORUN | Kills ports/processes. Classify only. |
| `prisma-control-center/09_KILL_EVERYTHING_PRISMA.cmd` | DANGER_DO_NOT_AUTORUN | Kills PRISMA ports/processes. Classify only. |
| `prisma-control-center/internal/wrappers/_kill_ports.ps1` | DANGER_DO_NOT_AUTORUN | Contains `taskkill`/`Stop-Process`. Classify only. |
| `prisma-control-center/01_LEVANTAR_TODO_LOCAL.cmd` | DANGER_DO_NOT_AUTORUN | Starts local stack. Do not run for LICFLOW3 verification. |
| `prisma-control-center/02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd` | DANGER_DO_NOT_AUTORUN | Starts local stack and Cloudflare flow. Do not run. |
| Any script that starts servers, frees ports, kills processes, or deploys Cloudflare | DANGER_DO_NOT_AUTORUN | User explicitly prohibited these actions. |

## Cloudflare Legacy Or Context-Only

| Path | Classification | Reason |
| --- | --- | --- |
| `products/chart-lab/app/scripts/deploy-cloudflare-pages.mjs` | DOC_ONLY | Correct for Chart Lab Pages only; not app.hitechrts.com licensing backend. |
| `prisma-control-center/PRISMA_CHART_LAB_CLOUDFLARE_PAGES_RUNTIME_DEPLOYMENT_README.md` | DOC_ONLY | Useful Wrangler/Pages context; not licensing authority. |
| `products/mobile/infra/cloudflare/*` | DOC_ONLY | Mobile PWA/domain bridge; not app.hitechrts.com licensing backend. |
| `products/mobile/app/deploy/*` | DOC_ONLY | Mobile deploy metadata; not hosted licensing backend. |

## External Runtime Artifacts

| Source | Classification | Reason |
| --- | --- | --- |
| `F:\descargasf\latest_CLOUD_COMMAND_CENTER_3160.zip` and timestamped 3160 ZIPs | RUNTIME_ARTIFACT | Prior evidence only; not source authority. |
| `F:\descargasf\PRISMA_cloud-command-center-3160_*.log` | RUNTIME_ARTIFACT | Prior logs only; do not replay as PASS. |
| `F:\descargasf\licflow2-result-20260702-014703.zip` | RUNTIME_ARTIFACT | LICFLOW2 evidence only; live repo remains authority. |
| Any `prcloud*\SECRET*_LOCAL_ONLY\*ADMIN*_TOKEN.txt` under `F:\descargasf` | DANGER_DO_NOT_AUTORUN | Token material. Metadata only; never copy or print values. |

## Rule

LICFLOW3 may reference these as context, but implementation authority stays in `shared/licensing`, 3160 Cloud SaaS bridge, governance contracts, and the new minimal Worker/D1 scaffold if no real backend exists.
