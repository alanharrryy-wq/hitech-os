# PRISMA App Mobile 28 - Data Real Readiness

## Objetivo

La iteración 28 endurece la app móvil para que distinga con claridad entre datos reales, datos vacíos, fuentes caídas y lectura parcial. La app móvil no debe rellenar huecos con información inventada ni hacer que una pantalla sin tickets parezca rota.

## Alcance

Esta entrega toca únicamente PRISMA App Mobile:

- contrato de `summary.dataReadiness`;
- construcción del payload desde el data-plane Tablet/PC;
- copy operativo para estados vacíos;
- hero móvil con lectura de madurez de datos;
- panel visual de madurez y calidad del dato dentro de la navegación premium;
- verificador propio `verify:data-readiness`;
- documentación y escenarios QA.

No toca Tablet POS, PC Backoffice ni `shared-kernel`.

## Decisión de producto

La app móvil debe contestar una pregunta muy humana, lamentablemente inevitable:

> ¿Estoy viendo operación real, operación vacía o una fuente caída?

Antes de esta ronda, varios estados podían verse parecidos: cero tickets, falta de PC, ausencia de inventario o falta de sync. La iteración 28 los separa para que el dueño no tenga que interpretar entrañas de backend como brujo de mercado.

## Nuevo contrato: `summary.dataReadiness`

El nuevo bloque vive dentro de `summary` para que esté disponible desde el primer render ejecutivo.

Campos principales:

| Campo | Propósito |
|---|---|
| `level` | Estado global: `ready`, `partial`, `empty`, `offline`, `blocked`. |
| `label` | Etiqueta corta visible para hero y panel. |
| `headline` | Mensaje principal para el dueño. |
| `detail` | Explicación accionable del estado. |
| `sourceSummary` | Resumen de disponibilidad Tablet/PC. |
| `salesState` | `with_sales`, `empty` o `unavailable`. |
| `inventoryState` | `with_items`, `empty` o `unavailable`. |
| `pcState` | `connected` o `unavailable`. |
| `syncState` | `clean`, `pending`, `failed` o `unknown`. |
| `facts` | Hechos breves derivados del estado real. |
| `actions` | Acciones recomendadas con dueño y prioridad. |

## Niveles de madurez

| Nivel | Significado | Mensaje operativo |
|---|---|---|
| `ready` | Fuentes conectadas y sin señales críticas. | Se puede decidir con confianza. |
| `partial` | Una fuente o señal requiere revisión. | Sirve para decidir, pero con contexto. |
| `empty` | Todo conectado. Ahora toca vender. | No es error; todavía no hay ventas registradas hoy. |
| `offline` | No hay fuentes activas. | Se informa honestamente sin inventar valores. |
| `blocked` | Falta la fuente clave Tablet. | Recuperar Tablet POS antes de confiar en ventas/stock. |

## Cambios visibles

El navegador premium ahora muestra un panel de madurez en:

- `Resumen`, para explicar qué tan confiable es la lectura general;
- `Sync`, para conectar madurez, fuentes y salud técnica.

El panel muestra:

1. estado global;
2. fuentes disponibles;
3. estado de ventas;
4. estado de inventario;
5. estado de sync;
6. hechos observados;
7. siguiente acción recomendada.

## Estados vacíos productivos

La app ya no debe tratar el cero como si fuera basura visual. Cero puede significar:

- no hay ventas cerradas hoy;
- Tablet no respondió;
- el inventario no publicó SKUs;
- PC no está disponible para consolidado;
- sync no confirmó eventos.

Cada caso tiene copy distinto y acción distinta. Porque claro, la humanidad necesitó inventar cinco formas distintas de “no hay datos”, pero por lo menos ya no se ven iguales.

## Reglas de aceptación

Una instalación se considera correcta si:

- `pnpm run typecheck` pasa;
- `pnpm run verify:data-readiness` pasa;
- el hero usa `summary.dataReadiness.headline`;
- el navegador muestra `PrismaMobileReadinessPanel`;
- no quedan selectores CSS Modules impuros;
- no quedan residuos visibles tipo `mock`, `fixture`, `fakeChart` o textos de prueba en archivos de runtime tocados;
- `summary.quickActions` se alimenta desde acciones de readiness.

## Riesgos controlados

- Los snapshots antiguos de caché no rompen el parseo porque `dataReadiness` tiene default seguro en el schema.
- Si Tablet cae, la app informa `blocked` u `offline`, no inventa ventas.
- Si PC cae, la app se mantiene útil como lectura móvil centrada en Tablet.
- Si no hay tickets, el estado es `empty`, no error.

## Comandos

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run verify:data-readiness
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run typecheck
```
