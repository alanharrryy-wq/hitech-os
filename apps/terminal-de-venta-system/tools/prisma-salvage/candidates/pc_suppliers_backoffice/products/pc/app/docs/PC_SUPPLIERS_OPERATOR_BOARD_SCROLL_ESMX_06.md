# PRISMA PC - Proveedores operator board + scroll real v06

## Objetivo

Esta integración corrige la legibilidad del módulo Proveedores y hace que el panel izquierdo sea navegable cuando el navegador está con zoom alto.

## Cambios visibles

- Proveedores se presenta como centro operativo, no como lista técnica.
- Compra Inteligente mantiene cards, pero los datos internos se ordenan en tablas legibles.
- Calendario, pedidos, recepción, pagos, señales y auditoría quedan separados por bloques claros.
- No se muestran rutas API, nombres de eventos técnicos ni claves como `order_cutoff` al usuario.
- El estado `blocked` se traduce como revisión operativa o presupuesto por revisar, nunca como una palabra seca en la interfaz.
- El menú lateral vuelve a scrollear completo como contenedor real, no como subpanel escondido.

## Validación

Ejecutar:

```powershell
node F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\tools\verify_pc_suppliers_operator_board_scroll_esmx_06.mjs F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app
```

Revisar visualmente:

```text
http://127.0.0.1:3130/proveedores
```

Con zoom en 125% o 150%, el panel izquierdo debe permitir bajar hasta utilidades y footer sin mochar navegación.
