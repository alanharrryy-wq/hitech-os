# PRISMA App Mobile 09 - PWA Domain Install Ready

Esta entrega deja PRISMA App lista para avanzar sin pagar Play Store.

## Qué cambia

- La app registra `prisma-mobile-sw.js` desde el layout raíz.
- `/prisma-app` muestra tarjeta de instalación PWA.
- `/prisma-app/install` guía instalación Android/iPhone.
- `/prisma-app/offline` documenta comportamiento offline.
- `public/prisma-offline.html` sirve como shell offline estático.
- `public/prisma-mobile-pwa.config.json` concentra dominio, origen y paths.
- `public/manifest.webmanifest` incluye PNGs, screenshot y shortcut de instalación.
- Se agregan scripts para configurar dominio y probar URLs públicas.

## Comandos útiles

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run pwa:status
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run pwa:configure-domain -- --domain=tu-dominio.com
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run verify:pwa-installable
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run pwa:smoke-url -- --url=https://tu-dominio.com
```

## Ruta de instalación para cliente

1. Abrir `https://tu-dominio.com/prisma-app`.
2. En Android Chrome: botón Instalar o menú `Agregar a pantalla principal`.
3. En iPhone Safari: compartir y `Agregar a pantalla de inicio`.
4. Abrir desde el ícono PRISMA.

Play Store queda diferida. Esto no bloquea validación comercial ni uso piloto.
