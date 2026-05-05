# PC Twin Parity Plan

## Rol de la app PC

La PC debe ser el centro de mando de PRISMA: gobierno, catálogo, inventario global, compras, recepción, auditoría, sync, reportes y resolución de conflictos.

No debe competir con la Tablet por velocidad de caja. Sería como poner al gerente a cobrar chicles en hora pico: puede, pero no para eso se le paga.

## Lo que PC ya trae fuerte

- Catálogo y validación.
- Existencias globales.
- Conteos y auditoría.
- Compras, recepción y reabasto.
- Sync operativo.
- Muchas rutas detalladas para control.
- Servicios y repositorios Prisma de backoffice.

## Lo que PC necesita para emparejarse mejor

1. **Espejo explícito de ventas Tablet**
   - Vista/resumen de tickets.
   - Ventas netas.
   - Devoluciones.
   - Corte por turno.
   - Eventos pendientes o fallidos.

2. **Caja como dominio formal**
   - Diferencias.
   - Arqueos.
   - Movimientos.
   - Cierres de turno.

3. **Panel de conflictos sync**
   - Origen Tablet.
   - Evento.
   - Entidad afectada.
   - Estado.
   - Acción recomendada.

4. **Matriz de impacto hacia Tablet**
   - Cambios de catálogo.
   - Cambios de precio.
   - Cambios de permisos.
   - Cambios de stock.

## Contrato PC recomendado

| Campo | Recomendación |
|---|---|
| `surface` | `pc` |
| `role` | `control` |
| `mustExpose` | auditoría, reportes, conflictos, configuración |
| `mustNotOwn` | captura rápida de piso como fuente exclusiva |
| `parityRule` | todo cambio operativo debe tener efecto claro en Tablet |

## Próximo incremento recomendado

Agregar una capa documental/técnica de `sales-control` y `cash-control` en PC que reciba el reflejo de ventas, devoluciones y turnos creados desde Tablet.
