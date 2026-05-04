# PRISMA_APP_MOBILE_10B_CLOUDFLARE_LIVE_ROUTE_REPAIR

## Objetivo

Reparar el puente vivo de Cloudflare cuando PRISMA Mobile ya compila y responde localmente, pero el hostname público `prisma.hitechrts.com` devuelve `404`.

## Evidencia esperada

- `http://127.0.0.1:3140/prisma-app` responde `200`.
- `https://prisma.hitechrts.com/prisma-app` devuelve `404` antes de reparar.
- Después de reparar, los endpoints públicos deben responder `2xx/3xx`.

## Alcance

Instala herramientas de reparación y verificación bajo:

```text
products/mobile/infra/cloudflare/
```

No modifica PC, Tablet, shared-kernel ni contratos compartidos.

## Reparación

El script `repair_prisma_mobile_cloudflare_live_route.ps1 -Apply`:

1. valida el origen local;
2. asegura la ruta DNS del túnel;
3. inserta/actualiza ingress en `config.yml`;
4. reinicia `cloudflared`;
5. ejecuta smoke público con reintentos.

## Rollback

El instalador revierte sólo los archivos instalados en el repo. El script de reparación crea backup del `config.yml` antes de tocarlo.
