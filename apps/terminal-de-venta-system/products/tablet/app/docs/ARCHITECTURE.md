# Arquitectura Tablet 6.1.1 Standalone

## Meta

Entregar una base bootable y modular para POS en tablet sin imports fantasma y sin dependencia obligatoria de PC para arrancar, validar o preparar su base local.

## Decisión clave

Tablet usa el **mismo modelo Prisma canónico** para conservar compatibilidad con PC y con sync futuro, pero ahora puede mantener un **runtime local propio** en `data/tablet-pos.db`.

Eso significa:

- Tablet puede venderse como producto POS autónomo.
- PC puede seguir existiendo como backoffice, gobierno, auditoría y operación avanzada.
- La base local de Tablet no rompe el contrato twin; lo vuelve ejecutable sin obligar PC.

## Capas

- `app/`: rutas y pantallas.
- `components/`: shell y UI mínima.
- `src/modules/`: manifest por dominio.
- `src/server/`: Prisma, repositorios y sync base.
- `src/server/prisma/client.ts`: resolución de DB Tablet por prioridad explícita.
- `shared/twin-kernel/`: contratos compartidos de referencia para ambas apps.
- `prisma/schema.prisma`: modelo canónico completo usado por Tablet.
- `scripts/tablet-db.mjs`: helper de DB local para generate, push, seed e info.
- `data/tablet-pos.db`: runtime SQLite local por defecto. No debe versionarse.

## Resolución de base de datos

Orden de prioridad:

1. `TABLET_DATABASE_URL`
2. `TABLET_DATABASE_PATH`
3. `TABLET_RUNTIME_MODE=managed` + `DATABASE_URL`
4. `data/tablet-pos.db`

La variable `DATABASE_URL` ya no se toma por defecto para Tablet, porque eso podía secuestrar el runtime con una DB canónica externa sin intención explícita.

## Contrato de producto

Tablet debe poder operar en modo standalone para negocios pequeños:

- catálogo local
- venta local futura
- turno local futuro
- eventos/outbox futuros
- reporte local futuro

PC debe ser requerido comercialmente solo cuando haya:

- multi-sucursal
- auditoría fuerte
- compras y recepción formal
- inventario caro o sensible
- permisos avanzados
- reportes ejecutivos consolidados

## Lo que esta inyección sí resuelve

- `terminal_de_venta.cmd tablet-*` ya no exige que exista PC.
- Tablet tiene schema Prisma local completo.
- Tablet tiene helper para crear DB local.
- Tablet tiene resolución de DB propia.
- Documentación deja de prometer runtime inexistente.

## Lo que esta inyección no resuelve todavía

- No implementa cierre transaccional de venta.
- No descuenta stock al vender.
- No crea tickets reales.
- No implementa outbox de cierre de venta.
- No agrega permisos Pro ni sync completo.

Esos puntos pertenecen a `PRISMA_TABLET_POS_STANDALONE_CORE_01`.
