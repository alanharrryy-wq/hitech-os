# PRISMA PC Proveedores v09 - Acciones reales

## Objetivo
Convertir el tablero visual de Proveedores en una superficie operable sin salir de `/proveedores`.

## Alcance
- Simular compra con presupuesto seguro.
- Crear pedido sugerido desde Compra Inteligente.
- Confirmar recepción desde pedido abierto.
- Registrar pago de cuenta por pagar.
- Consultar rastro de auditoría.

## Restricciones
- No toca Tablet.
- No toca shared-kernel.
- No introduce persistencia real; eso queda para v10.
- Los endpoints técnicos siguen ocultos para usuario final.

## Validación visual
En `/proveedores` debe aparecer **Operar Compra Inteligente sin salir de Proveedores** con el flujo: Simular → Pedido → Recepción → Pago → Auditoría.
