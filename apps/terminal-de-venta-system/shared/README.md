# PRISMA Shared

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PRISMA tiene Tablet POS standalone, PC Backoffice y contratos compartidos. Tablet no requiere PC para vender. PC no bloquea ventas locales de Tablet. Sync reconcilia eventos. Eventos son verdad operacional. Tablet usa DB local para operacion standalone.

Toda entrega relevante debe ser reversible y verificable. ZIP + installer `.py` sigue siendo el modelo preferido para futuras integraciones empaquetadas cuando el flujo pida entrega por paquete.


Shared es contrato compartido, no utileria generica. Incluye `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts` y `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\twin-kernel`.

No incluir helpers locales Tablet, helpers locales PC, queries especificas, UI especifica, logica touch POS, logica backoffice ni parches temporales.
