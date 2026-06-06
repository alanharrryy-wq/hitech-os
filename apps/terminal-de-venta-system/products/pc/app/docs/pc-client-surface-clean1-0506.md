# PC clean1 0506 1315

Objetivo: separar PC cliente final de laboratorios oscuros, y quitar overlays rojos de desarrollo en pantallas de inventario que fallaban por Prisma DB local.

## Cliente final PC
- `/dashboard` vuelve a usar `DecisionScreen` claro y operativo.
- `AppShell` queda forzado a modo claro.
- Se retira el selector oscuro del topbar del cliente.
- Navegación principal y secundaria ya no muestra rutas `internal` ni `lab`.

## Laboratorio aislado
- Nuevo hub: `/laboratorio-pc`.
- Referencia visual movida por instalador a `/laboratorio-pc/referencia-visual`.
- Liquid Glass y Capsules pasan bajo `/laboratorio-pc/referencia-visual/...`.
- Chart Lab pasa a `/laboratorio-pc/chart-lab?preview=charts`.
- Dashboard Governor piloto pasa a `/laboratorio-pc/dashboard-governor`.

## Errores rojos inferiores
- `/catalogo-activo`, `/existencias-criticas`, `/salud-barcodes` ya no dejan que Prisma rompa el render.
- Si la DB local no abre, muestran estado vacío honesto con alerta interna, no overlay rojo de Next.
- No se oculta el overlay con CSS. Se evita la excepción.
