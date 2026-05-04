# PRISMA_APP_MOBILE_07_API_CLIENT_UI_BINDING

## Resumen

Esta integración vuelve operativa la pantalla móvil `/prisma-app` usando los contratos de API instalados en `PRISMA_APP_MOBILE_06_API_CONTRACTS`.

La entrega agrega una capa completa de consumo y presentación:

- endpoint agregado `/api/mobile/snapshot`;
- contratos snapshot `zod`;
- cliente API con fallback progresivo;
- caché local para operación móvil degradada;
- tablero client-side conectado;
- componentes para KPIs, caja, ventas, inventario, alertas, reportes y sucursales;
- CSS responsive de vista móvil premium;
- verificador propio `verify:ui-binding`.

## Orden de datos

La UI consulta en este orden:

1. snapshot agregado;
2. endpoints individuales en paralelo;
3. caché local;
4. fixture demo contractual.

## Límites explícitos

No toca `products/pc/*`, `products/tablet/*`, `packages/shared-kernel/*` ni `shared/contracts/*`.

No resuelve todavía autenticación, autorización por rol, conexión a datos reales PC/backoffice, bridge real de sync ni publicación Android/AAB.

## Siguiente integración sugerida

`PRISMA_APP_MOBILE_08_AUTH_SESSION_AND_CONNECTED_SOURCE_ADAPTER`

## QA fixtures

Incluye `docs/prisma-app/fixtures/prisma-app-mobile-07-client-ui-binding-scenarios.json` con 60 escenarios de validación para snapshot, endpoints paralelos, caché local y fallback demo. Se valida con `verify:ui-fixtures`.
