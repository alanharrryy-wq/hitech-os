# PRISMA App Mobile 29 - WhatsApp install gate

## Objetivo

Separar el selector Android/iPhone del tablero normal de PRISMA App.

Antes, el selector podía aparecer dentro de la pantalla operativa normal, como vendedor ambulante metiéndose a una junta directiva. Ahora queda aislado en la pantalla de instalación abierta desde WhatsApp.

## Cambios

- El tablero normal `/prisma-app` ya no renderiza `PrismaMobilePwaInstallCard compact`.
- La pantalla `/prisma-app/install?from=whatsapp` queda como landing dedicada de instalación.
- Se integra el icono visual de PRISMA en la landing.
- Se reemplaza el copy vacío `La conexión existe...` por `Todo conectado. Ahora toca vender.`.
- Se agrega verificador `verify_prisma_app_mobile_29_whatsapp_install_gate.mjs`.

## Regla visual

Android/iPhone solo deben verse en contexto de instalación por enlace, principalmente WhatsApp. El home operativo no debe enseñar esas opciones.

## Validación

```bash
pnpm -C products/mobile/app run verify:whatsapp-install-gate
pnpm -C products/mobile/app run typecheck
```

## Paquete

`PRISMA_APP_MOBILE_WHATSAPP_INSTALL_GATE_29_20260503_v01`
