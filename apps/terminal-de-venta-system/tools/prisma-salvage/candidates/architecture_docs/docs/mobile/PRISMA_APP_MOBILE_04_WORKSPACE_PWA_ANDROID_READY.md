# PRISMA_APP_MOBILE_04_WORKSPACE_PWA_ANDROID_READY

## Propósito

Esta entrega prepara `products/mobile/app` para trabajo diario como producto Mobile independiente y agrega base PWA/TWA para camino futuro a Play Store.

No mueve Mobile bajo PC. No revive Pulso. No crea app final de Play Store. Deja el camino listo sin vender humo con moño.

## Cambios

- Agrega workspace raíz en `apps/terminal-de-venta-system`.
- Refuerza `products/mobile/app/package.json`.
- Agrega manifest PWA.
- Agrega iconos SVG temporales.
- Agrega template de Digital Asset Links.
- Agrega verificadores PWA y Play Store readiness.
- Crea scaffold `products/mobile/android`.
- Agrega docs de PWA, Play Store y TWA.
- Mantiene Surface IDs canónicos:
  - `prisma.pc.backoffice`
  - `prisma.tablet.pos`
  - `prisma.mobile.app`

## Comandos después de aplicar

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
pnpm install
pnpm -C products\mobile\app verify:product-root
pnpm -C products\mobile\app verify:pwa
pnpm -C products\mobile\app verify:playstore-readiness
pnpm -C products\mobile\app typecheck
pnpm -C products\pc\app typecheck
node tools\prisma\verify_prisma_tri_surface_visual_guardian_00c.mjs
```

## Estado Play Store

Queda preparado el camino, pero no queda publicada la app.

Falta:

- dominio real;
- HTTPS;
- assetlinks.json productivo;
- signing key;
- SHA-256 real;
- Android wrapper generado;
- `.aab`;
- Play Console;
- internal testing;
- privacy policy;
- data safety.

## Regla madre

Tablet vende sola. PC administra cuando existe. PRISMA App consulta, resume y alerta.
