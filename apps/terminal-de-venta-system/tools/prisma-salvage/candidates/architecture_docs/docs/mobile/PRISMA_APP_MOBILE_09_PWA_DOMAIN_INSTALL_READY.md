# PRISMA_APP_MOBILE_09_PWA_DOMAIN_INSTALL_READY

## Objetivo

Permitir que PRISMA App Mobile avance sin pagar Play Store, usando instalación PWA desde un dominio HTTPS propio.

## Alcance

Esta inyección agrega runtime PWA, service worker, shell offline, configuración de dominio, guía de instalación dentro de la app, verificador de readiness y smoke de URLs públicas.

## No toca

- `products/tablet`
- `products/pc`
- `packages/shared-kernel`
- `shared/contracts`

## Criterio de salida

- `/prisma-app` sigue funcionando.
- `/prisma-app/install` existe.
- `manifest.webmanifest` tiene iconos PNG y screenshot.
- `prisma-mobile-sw.js` existe y precachea offline shell.
- `verify:pwa-installable` pasa.
- El dominio puede configurarse sin editar archivos a mano.

## Decisión comercial

Play Store se posterga. La distribución inicial se hace por URL instalable desde navegador.
