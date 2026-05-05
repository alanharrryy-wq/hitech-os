# PRISMA PC - Proveedores + Compra Inteligente 01

## Objetivo

Agregar a PC Backoffice un módulo visible `Proveedores` con la capacidad estrella `Compra Inteligente`.

La entrega no intenta vender humo ni prometer que PRISMA compra solo. Implementa una primera capa funcional y auditable:

- manifest del módulo;
- ruta `/proveedores`;
- API `GET /api/proveedores/compra-inteligente`;
- motor determinístico de recomendación;
- simulador de compra como contrato de función;
- fixtures de proveedor/producto/pagos/recepción suficientemente amplios para probar escenarios reales;
- UI de Compra Inteligente con razones, impacto en caja, fechas, señales y trazabilidad;
- verificador específico.

## Regla de producto

PC gobierna proveedores, compras, recepciones, pagos y Compra Inteligente.
Tablet conserva señales ligeras y venta local.
App móvil supervisa alertas y aprobación futura acotada.

## Qué resuelve

1. Qué comprar.
2. Cuánto comprar.
3. Cuándo pedir.
4. Con qué proveedor.
5. Qué no comprar todavía.
6. Qué pago puede apretar caja.
7. Por qué PRISMA recomienda cada acción.
8. Cómo convertir recomendación en pedido sugerido.

## Archivos principales

- `src/lib/suppliers/types.ts`: contratos de dominio.
- `src/lib/suppliers/fixtures.ts`: dataset operativo.
- `src/lib/suppliers/smart-purchase-engine.ts`: motor de señales, recomendaciones y simulación.
- `src/lib/suppliers/server.ts`: snapshot server-side.
- `components/suppliers/smart-purchase-workbench.tsx`: UI principal.
- `app/proveedores/page.tsx`: ruta visible.
- `app/api/proveedores/compra-inteligente/route.ts`: API JSON.
- `tools/verify_pc_suppliers_smart_purchase_01.mjs`: verificación.

## Criterios de aceptación

- `/proveedores` carga sin depender de Tablet.
- El módulo aparece en navegación PC.
- Las recomendaciones muestran prioridad, proveedor, monto, cobertura, fechas, razones, riesgo y acción.
- Las compras bloqueadas o en espera no se maquillan como listas.
- Las señales críticas se separan de recomendaciones normales.
- La UI no usa términos técnicos visibles como `payload`, `runtime`, `schema` o `sync job`.
- La verificación local confirma archivos, registry, motor, simulador y microcopy clave.

## Siguiente iteración recomendada

Conectar este módulo a repositorios Prisma reales:

1. `SupplierRepository`.
2. `SupplierProductRepository`.
3. `SupplierPayableRepository`.
4. `SmartPurchaseRunRepository`.
5. persistencia de simulaciones y pedidos sugeridos.

Esta entrega deja la mesa puesta. No finge que ya llegó el banquete con mariachi.
