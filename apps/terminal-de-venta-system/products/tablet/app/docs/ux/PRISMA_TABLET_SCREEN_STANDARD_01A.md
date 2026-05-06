# PRISMA Tablet Screen Standard 01A

## Proposito

Este estandar define la forma canonica de construir pantallas operativas Tablet en PRISMA.

Aplica a:

- `/stock`
- `/sales`
- `/sync`
- `/shift`
- `/returns`

La meta es que cada pantalla deje de ser placeholder y se convierta en una pieza premium, conectada y verificable sin inventar un layout nuevo cada vez. Nada de chile, mole y pozole visual.

## Decision canonica

Cada pantalla operativa Tablet debe seguir este flujo:

```text
page.tsx
  -> servicio de dominio existente
  -> view model operativo
  -> PrismaOperationalScreen
  -> PrismaTabletShellUnified
  -> CSS/tokens PRISMA compartidos
```

La pantalla NO debe hacer esto:

```text
page.tsx
  -> queries improvisadas
  -> estilos inline
  -> HTML suelto
  -> copy provisional
  -> otra DB
```

## Capas del estandar

### 1. Shell

Toda pantalla operativa debe vivir dentro de `PrismaTabletShellUnified`.

Responsabilidad:

- navegacion consistente;
- header consistente;
- status visible;
- acciones de pantalla;
- integracion con el sistema visual premium.

### 2. Motor de modelo operativo

Archivo canonico:

```text
products/tablet/app/src/lib/ui/prisma-operational-screen-engine.ts
```

Responsabilidad:

- normalizar tonos;
- crear metricas consistentes;
- bloquear copy placeholder;
- formatear MXN, numeros y porcentajes;
- preparar modelos listos para pintar.

### 3. Contrato de pantalla

Archivo canonico:

```text
products/tablet/app/src/lib/ui/prisma-operational-screen-contract.ts
```

Responsabilidad:

- tipos de status;
- metricas;
- acciones;
- hero;
- secciones;
- tablas;
- listas;
- estados vacios.

### 4. Componente visual unificado

Archivo canonico:

```text
products/tablet/app/components/operational-screen/prisma-operational-screen.tsx
```

Responsabilidad:

- pintar masthead premium;
- pintar metric rail;
- pintar tabla/lista/alertas;
- pintar estados vacios;
- mantener jerarquia visual unica.

## Gramatica visual obligatoria

Cada pantalla debe tener, en este orden:

1. Shell PRISMA.
2. Header del shell.
3. Status pill.
4. Acciones principales.
5. Masthead operativo.
6. Rail de KPIs.
7. Seccion primaria.
8. Secciones secundarias.
9. Estados vacios/error visibles.

## Reglas de diseno

### Permitido

- `PrismaOperationalScreen` como base.
- CSS Modules del estandar.
- tokens PRISMA.
- servicios existentes de dominio.
- view models limpios.

### Prohibido

- `style={{ padding: "24px" }}` como layout final.
- copy tipo "segun el plan activo".
- pantallas que no usen shell.
- crear DB nueva para resolver una vista.
- duplicar componentes visuales por pantalla.
- inventar badges/tablas/cards locales.

## Reglas funcionales

Cada pantalla debe declarar:

- servicio propietario;
- fuente de datos;
- estados visibles;
- acciones permitidas;
- eventos o auditoria si toca dinero, caja, stock o sync;
- criterio de rollback.

## Fuentes de datos esperadas

| Ruta | Servicio | DB nueva | Comentario |
|---|---|---:|---|
| `/stock` | `stock.ts` | No | Productos, movimientos y stock bajo. |
| `/sales` | `sales.ts` | No | Ventas, tickets y resumen. |
| `/sync` | `sync.ts` | No | OutboxEvent y eventos recientes. |
| `/shift` | `shift.ts` | No | CashSession/Shift existente. |
| `/returns` | `returns.ts` | No | SaleReturn/repositorios existentes. |

Si falta un campo real, se evoluciona el schema existente con migracion controlada. No se crea otra base paralela.

## Definition of Done por pantalla

Una pantalla queda aceptada solo si:

- no contiene placeholder copy;
- usa `PrismaOperationalScreen` o justifica excepcion;
- usa `PrismaTabletShellUnified`;
- consume su servicio de dominio;
- no mete estilos inline de layout;
- muestra KPIs o resumen operativo;
- muestra al menos una seccion primaria;
- tiene empty/error/offline cuando aplique;
- pasa verify especifico;
- se entrega como ZIP + instalador con rollback.

## Orden recomendado de inyecciones

1. `PRISMA_TABLET_STOCK_SCREEN_01A_REAL_VIEW`
2. `PRISMA_TABLET_SALES_SCREEN_01A_REAL_VIEW`
3. `PRISMA_TABLET_SYNC_SCREEN_01A_REAL_VIEW`
4. `PRISMA_TABLET_SHIFT_SCREEN_01A_REAL_VIEW`
5. `PRISMA_TABLET_RETURNS_SCREEN_01A_REAL_VIEW`

## Ruta de preview

Se incluye una ruta interna para validar el estandar:

```text
/screen-standard-preview
```

Esta ruta no toca negocio, no crea DB y no reemplaza pantallas operativas. Solo permite ver el patron premium antes de inyectar cada pantalla real.
