# PRISMA HTML · Fuentes de autoridad Cloudflare

## Autoridad interna revisada

- `Prisma Cloud Ctr.zip`: Cloud Center, Worker/D1, seguridad, runbooks y operación.
- `cloudflare.zip`: código fuente LICFLOW3 Worker, D1 y migraciones.
- `prisma-control-center.zip`: Cloudflare Tunnel, supervisor y README de despliegue Pages de Chart Lab.
- `wrappers.zip`: launchers históricos del Control Center. No se trasladan.

## Autoridad oficial consultada

- Cloudflare Pages Static HTML: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- Direct Upload: https://developers.cloudflare.com/pages/get-started/direct-upload/
- Git integration: https://developers.cloudflare.com/pages/get-started/git-integration/
- Wrangler Pages commands: https://developers.cloudflare.com/workers/wrangler/commands/pages/
- Pages rollbacks: https://developers.cloudflare.com/pages/configuration/rollbacks/

## Decisión

`prisma-html` se prepara como sitio estático para Cloudflare Pages mediante una salida pública gobernada `dist/`. El paquete de migración no despliega, no crea proyecto Cloudflare y no toca DNS, Tunnel, Worker, D1, procesos o puertos.
