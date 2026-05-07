# PC_IMPACT_01_NAV_REAL

## Objetivo

Convertir acciones simuladas de la landing PC en navegacion real hacia rutas existentes del backoffice.

## Alcance

- PC solamente.
- No toca Tablet.
- No toca Mobile.
- No toca shared-kernel.
- No toca Prisma schema ni base de datos.

## Cambios

- Agrega mapa de rutas por modulo.
- Agrega mapa de rutas por accion rapida.
- Reemplaza el mensaje de accion simulada por navegacion real usando `window.location.href`.
- Agrega CTA visible para abrir el modulo activo.
- Agrega CSS marcado para el CTA y estado de navegacion listo.

## Validacion

El instalador verifica rutas, snippets aplicados, CSS marker, release doc, y ejecuta `pnpm exec tsc --noEmit` si `pnpm` esta disponible.
