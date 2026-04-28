# PRISMA Terminal de Venta System

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PRISMA tiene Tablet POS standalone, PC Backoffice y contratos compartidos. Tablet no requiere PC para vender. PC no bloquea ventas locales de Tablet. Sync reconcilia eventos. Eventos son verdad operacional. Tablet usa DB local para operacion standalone.

Toda entrega relevante debe ser reversible y verificable. ZIP + installer `.py` sigue siendo el modelo preferido para futuras integraciones empaquetadas cuando el flujo pida entrega por paquete.


## Superficies

- Tablet POS standalone: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app`
- PC Backoffice: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app`
- Shared contracts: `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts`
- Canon: `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\architecture\PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md`

Preferir `F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd` para flujos de operador.

Siguiente etapa: `PRISMA_TABLET_POS_STANDALONE_FULL_ENGINE_01`, `PRISMA_TABLET_POS_TOUCH_UI_FULL_02`, `PRISMA_PC_BACKOFFICE_SYNC_DASHBOARD_03`.
