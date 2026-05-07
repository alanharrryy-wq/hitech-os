# PRISMA Tablet Logo Injection 01

## Objetivo
Inyectar el logo real de PRISMA en el shell lateral de Tablet, usando el asset `logo-prisma-primary.png` dentro de `public/prisma/`.

## Cambios
- Instala `public/prisma/logo-prisma-primary.png`.
- Agrega una sección CSS marcada como `PRISMA_TABLET_LOGO_INJECTION_01` en `components/tablet-shell/prisma-tablet-shell.module.css`.
- Oculta el logo geométrico anterior renderizado con CSS y el texto de marca anterior.
- Mantiene el cambio como visual-only: no toca rutas, venta, checkout, API, DB ni sync.

## Validación visual esperada
En `http://127.0.0.1:3120/`, el sidebar debe mostrar el logo PRISMA real, sin rectángulo negro ni tarjeta amarilla alrededor.
