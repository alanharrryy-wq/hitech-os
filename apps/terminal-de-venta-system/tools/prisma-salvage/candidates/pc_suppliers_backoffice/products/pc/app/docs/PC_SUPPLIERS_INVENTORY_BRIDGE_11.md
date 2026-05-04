# PRISMA PC Proveedores - Inventario conectado 11

## Objetivo

Conectar Proveedores y Compra Inteligente con señales reales de Inventario cuando existan en la base consolidada de PC.

## Qué instala

- `inventory-bridge.ts`: lee productos, existencias, cobertura y señales de reabasto desde Prisma cuando están disponibles.
- Fallback explícito: si la base consolidada no responde o no tiene coincidencias, la UI declara que está usando datos cargados en Proveedores.
- `/api/proveedores/inventario`: expone el puente para QA y futura integración.
- `/proveedores`: muestra la sección **Inventario conectado** con fuente, cobertura, críticos y productos sugeridos.

## Límites

- No crea tablas nuevas.
- No toca Tablet.
- No toca `shared-kernel`.
- No persiste pedidos en DB formal todavía.

## Validación visual

En `/proveedores` debe existir la sección **Inventario conectado** con tarjetas de producto separadas por SKU, disponible, cobertura y sugerido.
