# PRISMA App Mobile - PWA Readiness

## Estado

Esta entrega prepara `products/mobile/app` como PWA-ready. No publica nada en tienda y no convierte la app en Android nativa por arte de magia, porque hasta Google pide papeles antes de dejar entrar al antro.

## Objetivo

PRISMA App debe poder evolucionar como una app móvil independiente:

```text
products/mobile/app
```

La app móvil no vive bajo PC y no es módulo de PC.

## Archivos PWA

```text
products/mobile/app/public/manifest.webmanifest
products/mobile/app/public/icons/prisma-app-icon.svg
products/mobile/app/public/icons/prisma-app-maskable.svg
products/mobile/app/public/icons/prisma-app-monochrome.svg
products/mobile/app/public/.well-known/assetlinks.template.json
```

## Manifest

El manifest declara:

- `name`: PRISMA App
- `short_name`: PRISMA
- `start_url`: `/prisma-app`
- `scope`: `/`
- `display`: `standalone`
- `orientation`: `portrait-primary`

## Qué falta para producción real

Antes de hablar de publicación real, falta:

1. Hosting HTTPS estable.
2. Dominio oficial.
3. Iconos finales de marca aprobados.
4. Service worker/offline strategy, si se decide usar.
5. Política de privacidad pública.
6. Pruebas reales en Android.

## Verificación

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app verify:pwa
```

## Internal testing

The Play Store release path must mention internal testing before production promotion.
