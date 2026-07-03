# LICFLOW3 Cloudflare Runbook

Última actualización de paquete: 2026-07-03

Este README/runbook deja el cierre LICFLOW3 en un solo lugar para no volver a buscar cómo se levanta, audita y verifica. Evidencia primero, ocurrencias después. 🛡️

## Estado final confirmado

```text
LICFLOW3 local repo/scaffold: PASS
LICFLOW3 Cloudflare live evidence read-only: PASS
Cloudflare functional POST smoke: BLOCKED_LIVE_WORKER_404
Current local repair state: LOCAL_READY_CLOUDFLARE_DEPLOY_AUTH_REQUIRED
```

## Actualizacion 2026-07-03: POST 404 root cause

Dummy POST smoke without admin token confirmed the live target still returns structured `404` for:

```text
POST /api/licenses/activate
POST /api/licenses/refresh
POST /api/licenses/revoke
```

At the same time, `/health` and `/api/public/capabilities` respond from `PRISMA Cloud Semilla` version `prcloud5-2026-06-23`.

Root cause classification:

```text
d) Pages/app handler distinto
f) mismatch entre scaffold prisma-licflow3-cloud-licensing y Worker real prisma-cloud-semilla
```

The repo-local worker source has the POST handlers, but the live worker version deployed on 2026-06-23 does not. The local worker config is now aligned to:

```text
Worker: prisma-cloud-semilla
D1: prisma_cloud_semilla
```

No deploy was executed. A live fix for `app.hitechrts.com` requires explicit Cloudflare deploy authorization.

## Repo y app

```text
Repo:
F:\repos\hitech-os

App principal:
F:\repos\hitech-os\apps\terminal-de-venta-system
```

Ruta oficial de este runbook dentro del repo:

```text
apps/terminal-de-venta-system/docs/ops/LICFLOW3_CLOUDFLARE_RUNBOOK.md
```

Plantilla de payload smoke dentro del repo:

```text
apps/terminal-de-venta-system/docs/ops/LICFLOW3_SMOKE_PAYLOAD_TEMPLATE.json
```

Antes de cualquier plan, comando, patch, diagnóstico o ZIP del repo, revisar:

```text
apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md
```

Frase operativa obligatoria:

```text
Voy a revisar esa madre: `docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`. Contexto y aprendizaje actualizados.
```

## Estado Git esperado antes de pruebas Cloudflare

```powershell
$ErrorActionPreference='Stop'; Set-Location 'F:\repos\hitech-os'; git status --short --branch
```

Resultado ideal:

```text
## main...origin/main
```

Sin líneas debajo.

## Evidencia LICFLOW3 ya confirmada

ZIPs clave de cierre:

```text
licclose2 0207 132042 result.zip
liccf2 0307 105556 result.zip
```

Cierre local:

```text
LICFLOW3_LOCAL_CLOSE_PASS_CLOUDFLARE_LIVE_EVIDENCE_PENDING
```

Cierre Cloudflare read-only:

```text
LICFLOW3_CLOUDFLARE_LIVE_EVIDENCE_PASS_READONLY
```

## Target Cloudflare

```text
Dominio:
hitechrts.com

Target SaaS/licensing:
https://app.hitechrts.com
```

## Recursos vivos confirmados

```text
Worker real:
prisma-cloud-semilla

D1 real:
prisma_cloud_semilla

App:
https://app.hitechrts.com

Health:
https://app.hitechrts.com/health
```

## Evidencia Cloudflare confirmada

```text
Wrangler: OK
Wrangler version vista: 4.93.0
Wrangler whoami: OK

D1 prisma_cloud_semilla:
found: true

Worker prisma-cloud-semilla:
deployments: OK
status: OK
versions: OK
secret names list: OK

app.hitechrts.com:
HTTP 200
Cloudflare headers present

/health:
HTTP 200

/api/licenses/*:
OPTIONS 200
GET/HEAD 404
route_signal true
```

Interpretación:

```text
/api/licenses/* existe como ruta viva por OPTIONS=200.
GET/HEAD 404 no certifican fallo funcional porque esos endpoints probablemente requieren POST con payload.
No hacer POST sin payload dummy autorizado.
```

## Wrangler: regla madre

No asumir Wrangler global.

Usar siempre patrón:

```powershell
pnpm -C <root-con-wrangler> exec wrangler --version
pnpm -C <root-con-wrangler> exec wrangler whoami
```

El root que funcionó fue detectado como package root con Wrangler disponible, por ejemplo:

```text
apps/terminal-de-venta-system/products/chart-lab/app
```

Para operaciones de Worker LICFLOW3 usar `--cwd` apuntando al worker root cuando aplique:

```powershell
pnpm -C <root-con-wrangler> exec wrangler --cwd "F:\repos\hitech-os\apps\terminal-de-venta-system\infra\cloudflare\licflow3-worker" <comando>
```

## Worker repo source vs Worker real

Legacy/local-only LICFLOW3 config used to mention:

```text
prisma-licflow3-cloud-licensing
prisma-licflow3-licensing
```

Do not use those names for the real repair unless a future migration explicitly creates a new stack. The evidence viva real confirmed:

```text
Worker remoto real:
prisma-cloud-semilla

D1 remoto real:
prisma_cloud_semilla
```

The governed worker source is:

```text
infra/cloudflare/licflow3-worker
```

Its `wrangler.jsonc` must preserve the real Worker and D1 names above. No duplicar LICFLOW2 ni crear otro stack cloud/licensing.

## Comandos read-only útiles

### Git limpio

```powershell
$ErrorActionPreference='Stop'; Set-Location 'F:\repos\hitech-os'; git status --short --branch
```

### Wrangler version/whoami

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
pnpm -C 'F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app' exec wrangler --version
pnpm -C 'F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app' exec wrangler whoami
```

### D1 list

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
pnpm -C 'F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app' exec wrangler d1 list --json
```

### D1 info

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
pnpm -C 'F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app' exec wrangler d1 info prisma_cloud_semilla --json
```

### Worker deployments/status/versions/secrets names-only

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
$Root='F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app'
$Cwd='F:\repos\hitech-os\apps\terminal-de-venta-system\infra\cloudflare\licflow3-worker'
pnpm -C $Root exec wrangler --cwd $Cwd deployments list --name prisma-cloud-semilla --json
pnpm -C $Root exec wrangler --cwd $Cwd deployments status --name prisma-cloud-semilla --json
pnpm -C $Root exec wrangler --cwd $Cwd versions list --name prisma-cloud-semilla --json
pnpm -C $Root exec wrangler --cwd $Cwd secret list --name prisma-cloud-semilla --format json
```

### Local route contract verifiers

These checks do not call production. They import the local Worker and assert dummy POST reaches the handler and returns a structured non-404 contract rejection.

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os\apps\terminal-de-venta-system'
pnpm run verify:licflow3:route-activate
pnpm run verify:licflow3:route-refresh
pnpm run verify:licflow3:route-revoke
pnpm run verify:licflow3:no-secrets
pnpm run verify:licflow3:no-db-copy
pnpm run verify:licflow3:no-deploy-autorun
```

### Deploy plan, not authorization

Only run after explicit user authorization:

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
$WorkerRoot='F:\repos\hitech-os\apps\terminal-de-venta-system\infra\cloudflare\licflow3-worker'
pnpm -C $WorkerRoot exec wrangler deploy --name prisma-cloud-semilla
```

Rollback, if the authorized deploy fails smoke:

```powershell
$ErrorActionPreference='Stop'
Set-Location 'F:\repos\hitech-os'
$Root='F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app'
$WorkerRoot='F:\repos\hitech-os\apps\terminal-de-venta-system\infra\cloudflare\licflow3-worker'
pnpm -C $Root exec wrangler --cwd $WorkerRoot versions list --name prisma-cloud-semilla --json
pnpm -C $Root exec wrangler --cwd $WorkerRoot versions deploy <previous-version-id> --name prisma-cloud-semilla
```

Nunca leer valores de secrets. Sólo names-only.

## Prohibiciones

No hacer:

```text
no deploy Cloudflare sin autorización explícita
no tocar DNS
no tocar Tunnel
no DB dumps
no secrets
no private keys
no tokens en logs
no Prisma generate hot
no matar procesos
no liberar puertos
no levantar servidores
no force push
no git add .
no fake green
```

## Smoke funcional autorizado

El smoke funcional real todavía queda pendiente porque requiere payload dummy explícito.

Archivo local esperado para ejecutar POST smoke:

```text
F:\descargasf\licflow3_smoke_payload.json
```

Plantilla versionada en repo:

```text
apps/terminal-de-venta-system/docs/ops/LICFLOW3_SMOKE_PAYLOAD_TEMPLATE.json
```

Reglas del smoke:

```text
- Sólo con datos dummy.
- No usar licencia real.
- No copiar secrets.
- No imprimir body sensible en logs.
- No declarar PASS funcional si sólo hay 404/401/422 sin contrato.
- Capturar status, headers seguros, hashes/resumen, no valores privados.
```

## Criterio de PASS futuro para smoke POST

Para declarar PASS funcional, hace falta al menos:

```text
POST /api/licenses/activate responde según contrato esperado
POST /api/licenses/refresh responde según contrato esperado
POST /api/licenses/revoke responde según contrato esperado
no 404
no 5xx
no secrets impresos
no DB dump
no deploy
repo sigue limpio
```

Si sólo se obtiene route evidence, el estado correcto será:

```text
LICFLOW3_SMOKE_ROUTE_EVIDENCE_ONLY
```

No `PASS funcional`.

## Último estado confiable

```text
LICFLOW3 repo local: cerrado
Cloudflare live evidence read-only: cerrado
Functional POST smoke: local route contract PASS; live target still requires authorized deploy
Current classification: LOCAL_READY_CLOUDFLARE_DEPLOY_AUTH_REQUIRED
```
