# PRISMA Tablet Sidebar Groups Order Fix 01

## Objetivo

Ordenar la navegación lateral de Tablet para que el flujo operativo sea más natural:

1. Inicio
2. Turno y caja
3. Vender
4. Catálogo
5. Existencias
6. Ventas de hoy
7. Soporte operativo

Además, los grupos `Operación`, `Consulta rápida` y `Soporte` ahora son colapsables mediante `<details>/<summary>` nativo.

## Alcance

Archivos tocados:

- `components/tablet-shell/tablet-nav.ts`
- `components/tablet-shell/prisma-tablet-shell.tsx`
- `components/tablet-shell/prisma-tablet-shell.module.css`
- `tools/verify_prisma_tablet_sidebar_groups_order_fix_01.mjs`

## No toca

- POS engine
- checkout
- venta
- API
- DB
- sync/outbox
- PC
- shared-kernel
- packshots

## Criterios visuales

- Grupos abiertos: letras con brillo/control visual claro.
- Grupos cerrados: encabezado más grande y azul.
- El orden favorece operación real: primero iniciar y turno, luego venta, luego consulta.
- Sin estado React nuevo: usa `<details>` nativo para evitar meter bundle inútil al shell.

## Validación esperada

Abrir `http://127.0.0.1:3120/` y revisar:

- La barra lateral muestra `Inicio`, `Turno y caja`, `Vender` dentro de Operación.
- `Catálogo`, `Existencias`, `Ventas de hoy` aparecen bajo Consulta rápida.
- Los headers de grupo se pueden colapsar/desplegar.
- Al cerrar un grupo, el header queda grande y azul.
- Al abrir un grupo, el texto del header brilla.
