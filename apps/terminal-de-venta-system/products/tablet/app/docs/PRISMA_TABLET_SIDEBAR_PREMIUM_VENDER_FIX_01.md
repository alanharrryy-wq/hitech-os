# PRISMA Tablet Sidebar Premium Vender Fix 01

## Objetivo
Hacer que el CTA lateral **Vender** se vea premium/glass, eliminar el texto auxiliar bajo la etiqueta y agregar motion más elegante:
- estado normal: flotación ambiental muy sutil
- hover: lift suave con más brillo
- seleccionado: resplandor y micro-pulso premium

## Archivos tocados
- `apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css`

## No toca
- lógica de navegación
- POS / cobro / checkout
- APIs / DB / sync
- catálogo / packshots

## Resultado esperado
- El botón **Vender** deja de mostrar el texto auxiliar largo.
- Se ve como CTA glass premium azul.
- Tiene motion sutil cuando no está seleccionado.
- Tiene motion distinto cuando está seleccionado.
