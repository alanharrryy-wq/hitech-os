# LICFLOW3 Cloudflare Wrangler/D1 Runbook

Status: OPERATIVO
Last updated: 2026-07-06
Scope: Cloud License Gateway / LICFLOW3 / Cloudflare Worker / D1

## Identidad canonica

- Worker: `prisma-cloud-semilla`
- D1: `prisma_cloud_semilla`
- URL viva: `https://app.hitechrts.com`
- `workers_dev=false`
- Con `workers_dev=false`, el custom domain manda. No usar `*.workers.dev` como URL viva de smoke.

## Wrangler por OAuth local

Wrangler se usa con OAuth local en esta repo. No se usa `CLOUDFLARE_API_TOKEN` para este flujo, no se guardan tokens en repo y no se imprimen secrets.

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler whoami
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler login
```

Si `whoami` falla, hacer login local antes de D1 remoto o deploy. Worker secrets son write-only: si se pierde el admin token, se rota uno nuevo; no se intenta recuperarlo.

## D1 remoto

Usar siempre `--remote` para el D1 vivo:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 list
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 migrations list prisma_cloud_semilla --remote
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 migrations apply prisma_cloud_semilla --remote
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE type IN ('table','index','trigger','view') ORDER BY type,name;"
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler d1 execute prisma_cloud_semilla --remote --json --command "PRAGMA table_info(licenses);"
```

Antes de agregar triggers o constraints sobre tablas vivas, verificar `sqlite_schema`, `PRAGMA table_info`, migraciones aplicadas y compatibilidad legacy/nuevo. No confiar solo en migraciones locales.

## Worker deploy

Deployar desde el paquete del Worker:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler deploy
```

Antes y despues del deploy, confirmar que `wrangler.jsonc` conserva `workers_dev=false` y que la URL viva sigue siendo `https://app.hitechrts.com`.

Smoke publico post-deploy:

```powershell
Invoke-WebRequest -UseBasicParsing https://app.hitechrts.com/health
Invoke-WebRequest -UseBasicParsing https://app.hitechrts.com/api/public/capabilities
```

Debe verse D1 bound, rutas LICFLOW3 live y modo `worker-d1`.

## Secrets

Rotar secrets sin imprimir valores:

```powershell
pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler secret put PRISMA_ADMIN_TOKEN
```

Reglas:

- Secrets son write-only.
- No se recuperan; se rotan.
- No se imprimen, no se guardan y no entran a ZIPs.
- Si hace falta evidencia, guardar solo fingerprint SHA-256 truncado.

## Smoke live

La URL canonica del smoke es:

```powershell
$env:PRISMA_WORKER_URL = "https://app.hitechrts.com"
```

Rutas minimas:

- `/health`
- `/api/public/capabilities`
- setup live
- claim Tablet, PC y Mobile
- portal / magic link
- status / refresh
- cleanup revoke
- read-after-write del revoke
- audit/event del revoke si aplica al contrato

`POST /api/licenses/revoke` solo es PASS si no devuelve `D1_WRITE_FAILED`, el estado persiste como `revoked` en D1 y audit/event queda verificado o se documenta con evidencia por que no aplica.

## Reglas anti-regresion

- No usar `*.workers.dev` cuando `workers_dev=false`.
- No agregar triggers D1 con columnas no verificadas en D1 remoto.
- No usar `INSERT OR REPLACE` en tablas con FKs/triggers sin justificar; preferir update/insert explicito.
- No fake green en revoke.
- Si status cambia pero audit falla, eso es FAIL.
- Si audit cambia pero status no, eso es FAIL.
- Si el endpoint responde OK pero read-after-write no confirma, eso es FAIL.

## Incidente 2026-07-06

El live smoke de cleanup revoke fallo en `POST https://app.hitechrts.com/api/licenses/revoke` con `500 D1_WRITE_FAILED`. La causa raiz fue que `0004_license_client_integrity.sql` creo triggers sobre `licenses` usando `NEW.license_id`, pero el D1 vivo usaba schema legacy `licenses.id / tenant_id`.

La correccion canonica es compensatoria:

- `0005_fix_license_revoke_legacy_schema_triggers.sql` elimina los triggers incompatibles.
- El Worker mantiene el enforcement de client-context en codigo schema-aware.
- Revoke confirmado hace lectura previa, update+audit en batch, read-after-write y verificacion de audit/event antes de devolver PASS.
