# Supplier + ProductSupplier sync closure 01

Fecha: 2026-05-22T00:26:46

## Cerrado en esta iteración

Eventos:
- `supplier.created`
- `supplier.updated`
- `supplier.disabled`
- `product.supplier.linked`
- `product.supplier.unlinked`
- `product.supplier.updated`

## Matriz funcional

| Entity | Topic | Tablet producer | PC validator | PC projector | DB |
|---|---|---|---|---|---|
| Supplier | supplier.created | supplier-mutations.prisma.ts | sync-event-contract.ts | projectSupplier | Supplier |
| Supplier | supplier.updated | supplier-mutations.prisma.ts | sync-event-contract.ts | projectSupplier | Supplier |
| Supplier | supplier.disabled | supplier-mutations.prisma.ts | sync-event-contract.ts | projectSupplier | Supplier |
| ProductSupplier | product.supplier.linked | supplier-mutations.prisma.ts | sync-event-contract.ts | projectProductSupplier | ProductSupplier |
| ProductSupplier | product.supplier.updated | supplier-mutations.prisma.ts | sync-event-contract.ts | projectProductSupplier | ProductSupplier |
| ProductSupplier | product.supplier.unlinked | supplier-mutations.prisma.ts | sync-event-contract.ts | projectProductSupplier | ProductSupplier |

## Notas

- No se modifican schemas Prisma porque `Supplier` y `ProductSupplier` ya existen en Tablet y PC.
- El ingest ahora conserva `supplierId`, `linkId` y `productSupplierId` como candidatos de aggregateId.
- Payload inválido de proveedores/producto-proveedor cae como rejected/dead-letter, no como verde falso.
- ProductSupplier valida existencia de Product y Supplier antes de proyectar.
- Si un link se marca primario, se apagan otros primarios del mismo producto.
