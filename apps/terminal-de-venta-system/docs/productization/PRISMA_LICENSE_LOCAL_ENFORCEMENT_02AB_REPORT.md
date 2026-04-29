# PRISMA License Local Enforcement 02AB

## Objetivo

Implementa runtime local de licencias y enforcement suave para Tablet y PC.

## Incluye

- Loader local read-only para `license.json`.
- Validación de shape/schema sin firma criptográfica todavía.
- Catálogo de planes y features.
- Resolver central `resolveFeature`.
- APIs locales `/api/license/status`, `/api/license/features`, `/api/license/features/[key]` para Tablet y PC.
- Pantalla `/settings/license` para Tablet y PC.
- Gates suaves para funciones avanzadas.
- Política de continuidad: la venta básica de Tablet no queda secuestrada por licencia faltante o caída.

## No incluye

- Firma criptográfica de licencia.
- Refresh remoto.
- Portal de pagos o facturación.
- Servidor SaaS de licencias.

## Regla de oro

La licencia gobierna planes y funciones avanzadas, pero no debe romper el POS básico standalone.
