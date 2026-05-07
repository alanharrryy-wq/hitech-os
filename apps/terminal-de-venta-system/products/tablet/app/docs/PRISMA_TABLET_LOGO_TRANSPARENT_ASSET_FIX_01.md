# PRISMA Tablet Logo Transparent Asset Fix 01

## Objetivo
Reemplazar el asset del logo instalado previamente por la versión **original transparente**, sin re-procesar fondo, sin cambiar el tamaño visual ni tocar la composición del sidebar.

## Alcance
- Reemplaza únicamente: `app/public/prisma/logo-prisma-primary.png`
- Conserva el CSS / layout / sizing ya aplicado en la inyección anterior.
- No toca lógica POS, rutas, datos ni componentes funcionales.

## Resultado esperado
El logo del sidebar debe seguir viéndose con el mismo tamaño y colocación, pero usando el PNG transparente real del usuario.
