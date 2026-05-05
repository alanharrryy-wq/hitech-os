# PRISMA Tablet POS Standalone

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PRISMA tiene Tablet POS standalone, PC Backoffice y contratos compartidos. Tablet no requiere PC para vender. PC no bloquea ventas locales de Tablet. Sync reconcilia eventos. Eventos son verdad operacional. Tablet usa DB local para operacion standalone.

Toda entrega relevante debe ser reversible y verificable. ZIP + installer `.py` sigue siendo el modelo preferido para futuras integraciones empaquetadas cuando el flujo pida entrega por paquete.


Tablet es POS standalone vendible por si solo. Debe vender localmente con `products/tablet/app/data/tablet-pos.db`, catalogo local, tickets, decremento de stock, eventos, outbox, exportaciones y continuidad offline.

Variables: `TABLET_DATABASE_URL`, `TABLET_RUNTIME_MODE`.

Rutas esperadas: `/pos`, `/catalog`, `/sales/today`, `/inventory/low-stock`, `/events/outbox`, `/settings/export`.

Comandos operativos:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd tablet-db-init`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd tablet-dev`

Este README alinea el producto para codigo futuro; no promete que el motor POS final ya este completo.
