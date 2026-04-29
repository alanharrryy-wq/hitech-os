# PRISMA LICENSE SIGNED REFRESH 02CD

## Objetivo

Completar la segunda mitad del licenciamiento PRISMA:

- 02C: licencias firmadas Ed25519 para evitar manipulación manual del plan.
- 02D: refresh remoto opcional, cache local atómica, estado de actualización y UI de refresh.

## No objetivos

- No implementa pagos.
- No implementa portal SaaS de clientes.
- No obliga a internet para venta básica Tablet.
- No elimina la política de continuidad del POS.

## Reglas operativas

- El archivo local puede ser firmado o unsigned dev.
- En producción, una licencia sin firma se considera inválida salvo override explícito.
- Refresh remoto solo corre si `PRISMA_LICENSE_REFRESH_ENABLED=1` y `PRISMA_LICENSE_SERVER_URL` está definido.
- Si refresh falla, se conserva la última licencia local válida.
- La venta básica sigue protegida por la política de continuidad definida en 02AB.

## Variables

```text
PRISMA_LICENSE_PATH
PRISMA_LICENSE_ALLOW_UNSIGNED
PRISMA_LICENSE_REQUIRE_SIGNED_DEV
PRISMA_LICENSE_REFRESH_ENABLED
PRISMA_LICENSE_SERVER_URL
PRISMA_LICENSE_DEVICE_ID
PRISMA_LICENSE_REFRESH_TIMEOUT_MS
```
