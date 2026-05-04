# PRISMA Tablet Flow Guided Sidebar 04I

## Objetivo

Convertir el menu lateral de Tablet en una navegacion guiada por contexto operativo, no en un tablero de avion con todos los botones visibles todo el tiempo.

## Regla funcional

- En `Inicio` el menu lateral muestra solamente `Inicio`.
- Al entrar a venta, el menu muestra el flujo minimo para operar: `Inicio`, `Vender`, `Turno`, `Ventas de hoy` y rutas de soporte solo cuando aplican.
- `Catalogo` y `Existencias` no aparecen como ruido permanente; aparecen cuando el usuario esta en esas rutas o cuando el flujo de control lo amerita.
- `Pendientes` aparece si existen pendientes/fallidos/conflictos o si la ruta activa es sync.
- `Estado del sistema` aparece si hay advertencias, problemas de conexion/catalogo o si la ruta activa es release gate.

## Justificacion de producto

Tablet es POS touch-first. La navegacion debe empujar venta y turno, no convertir la caja en mini backoffice. PC gobierna el control avanzado; Tablet vende, opera caja y deja eventos.

## Estados soportados

| Estado | Como se detecta | Menu esperado |
|---|---|---|
| `inicio` | `currentPath === /` | Solo `Inicio` |
| `venta` | `/pos` o `/checkout` | Inicio, Vender, Turno, Ventas de hoy, soporte contextual |
| `operacion` | ventas, turno, pendientes, devoluciones | Inicio, Vender y ruta activa |
| `control` | catalogo, stock, inventory, estado | Inicio, Vender y ruta activa/control |

## Alcance

Toca solo Tablet:

- `components/tablet-shell/tablet-nav.ts`
- `components/tablet-shell/prisma-tablet-shell.tsx`
- `components/tablet-shell/prisma-tablet-shell.module.css`
- `components/pos/pos-screen.tsx`
- `components/pos/pos-ticket-panel.tsx`
- `tools/verify_tablet_flow_guided_sidebar_04i.mjs`

## No toca

- `packages/shared-kernel/*`
- `shared/*`
- PC
- Prisma schema
- APIs de venta

## Nota de UX

La idea no es esconder por esconder. Es esconder para guiar. En caja, menos ruido equivale a menos errores, menos vueltas y menos cajero picando botones como si estuviera jugando buscaminas con dinero real.
