# PRISMA Tablet Ice Glass Cleanup 01

## Objetivo
Eliminar el tinte cálido / amarillo residual del shell Light de Tablet y dejar el layout en un glass frío, limpio y premium.

## Cambios
- Purga variables heredadas tipo gold/warm en el shell Light.
- Sidebar, brand, header, runtime strip y runtime chips con vidrio frío azul/blanco.
- Fondo base del shell neutralizado para evitar crema / mostaza / champagne.
- Selector de apariencia con acabado más frío para no contaminar visualmente el header.

## Archivos tocados
- `components/tablet-shell/prisma-tablet-shell.module.css`
- `components/ui/prisma-skin-selector.module.css`

## No toca
- lógica POS
- rutas
- API / DB / sync
- drawer de edición
- catálogo / datos

## Validación visual esperada
- `http://127.0.0.1:3120/` en skin claro debe verse sin velo amarillo en el header ni en el shell.
- Sidebar y header deben verse blanco-hielo / azul frío.
- El logo no debe quedar dentro de una mancha beige.
