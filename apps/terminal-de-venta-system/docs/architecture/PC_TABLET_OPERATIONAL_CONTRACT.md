# PC Tablet Operational Contract

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Alinea limites de producto: Tablet vende, PC gobierna cuando existe, sync reconcilia.


## Producto por capas

- Tablet POS standalone: venta local, ticket, inventario local, eventos, exportaciones.
- PC Backoffice: catalogo maestro, stock avanzado, compras, recepcion, reabasto, auditoria, dashboard, conflictos.
- PC + Tablet: operacion managed con eventos y reconciliacion.

## Invariantes

- Tablet no valida existencia de PC para tareas POS basicas.
- PC no autoriza la venta local basica.
- Sync no es permiso de venta; sync es puente de reconciliacion.
- Eventos son la verdad operacional para dinero, inventario, caja y auditoria.

## Comercial

PRISMA can be sold by layers:

- Tablet POS standalone for local sales.
- PC Backoffice for advanced control.
- PC + Tablet for managed operations.
