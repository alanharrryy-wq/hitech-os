# PRISMA App Mobile 11 - iOS Home Icon Play Store

## Objetivo

Forzar que la instalación tipo PWA / marcador en iOS use el icono premium:

```text
products/mobile/app/public/icons/prisma_playstore_icon_512.png
```

Antes, `app/layout.tsx` declaraba `apple-touch-icon` apuntando a `prisma-pwa-192.png`, así que Safari podía tomar el logo de muro en vez del prisma oscuro premium. Es el clásico caso de la fonda sirviendo el plato bonito en la carta y luego sacando el plato de plástico porque alguien dejó el default prendido.

## Archivos tocados

- `products/mobile/app/app/layout.tsx`
- `products/mobile/app/public/manifest.webmanifest`
- `products/mobile/app/public/prisma-mobile-sw.js`
- `products/mobile/app/public/icons/prisma_playstore_icon_512.png`
- `products/mobile/app/public/icons/prisma_playstore_icon_192.png`
- `products/mobile/app/tools/verify_prisma_app_mobile_11_ios_home_icon_playstore.mjs`

## Qué cambia

1. `metadata.icons.apple` ahora apunta primero a `prisma_playstore_icon_512.png`.
2. `manifest.webmanifest` usa los iconos `prisma_playstore_icon_*` como iconos PNG principales.
3. Los shortcuts del manifest dejan de apuntar a `prisma-pwa-192.png`.
4. El service worker sube versión de caché para no quedarse embarrado con iconos viejos.
5. Se agrega verificador dedicado para asegurar que iOS Home Screen no vuelva al icono anterior por accidente.

## Validación manual en iPhone

1. Publicar o levantar la app después de aplicar el paquete.
2. Abrir Safari en iPhone.
3. Entrar a la URL pública o local accesible de PRISMA App.
4. Compartir > Agregar a pantalla de inicio.
5. Si ya existía el icono viejo, borrarlo primero de la pantalla de inicio y volver a agregarlo.

## Nota de caché iOS

iOS cachea iconos como si fueran secretos de familia. Si sigue apareciendo el anterior:

- borra el acceso viejo de pantalla de inicio;
- recarga la app en Safari;
- vuelve a agregarla;
- si Safari insiste, borra datos del sitio desde Ajustes > Safari > Avanzado > Datos de sitios web.

## Superficies

- Mobile/App: tocada.
- Tablet POS: no tocada.
- PC Backoffice: no tocada.
- Shared kernel: no tocado.
