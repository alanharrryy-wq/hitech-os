# PRISMA App Mobile 30 - Install Landing Black

## Objetivo

Convertir `/prisma-app/install?from=whatsapp` en una landing visual premium para usuarios que abren el link desde WhatsApp.

## Qué cambia

- Pantalla tipo teléfono con marco visual oscuro premium.
- Badge superior `LLEGASTE DESDE WHATSAPP`.
- Logo PRISMA central con presencia hero.
- Tarjetas grandes para Android e iPhone.
- Flecha circular por plataforma.
- Nota contextual de WhatsApp.
- Acción secundaria `Abrir PRISMA` para usuarios que ya la tienen instalada.
- Acción `Copiar enlace` como salida segura cuando iOS/WhatsApp no permitan instalación directa.
- Assets PWA faltantes para Android, iOS y manifest.

## Archivos principales

- `app/prisma-app/install/page.tsx`
- `src/components/prisma-app/PrismaMobilePwaInstallPage.tsx`
- `src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- `src/components/prisma-app/prisma-mobile-pwa.module.css`
- `public/icons/prisma_whatsapp_install_icon.png`
- `public/icons/prisma_playstore_icon_192.png`
- `public/icons/prisma_playstore_icon_512.png`
- `public/icons/prisma_ios_touch_icon_180.png`
- `public/apple-touch-icon.png`
- `public/apple-touch-icon-precomposed.png`
- `public/screenshots/prisma-mobile-pwa-dashboard.png`

## Validación

Ejecutar desde `products/mobile/app`:

```powershell
node tools/verify_prisma_app_mobile_29_whatsapp_install_gate.mjs
node tools/verify_prisma_app_mobile_30_install_landing_black.mjs
```

## Nota iOS

iOS no permite instalar una PWA con un disparo automático desde WhatsApp. La pantalla guía al usuario hacia Safari y conserva una opción para copiar el enlace.
