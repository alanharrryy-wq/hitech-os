# PRISMA Shared Kernel

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PRISMA tiene Tablet POS standalone, PC Backoffice y contratos compartidos. Tablet no requiere PC para vender. PC no bloquea ventas locales de Tablet. Sync reconcilia eventos. Eventos son verdad operacional. Tablet usa DB local para operacion standalone.

Toda entrega relevante debe ser reversible y verificable. ZIP + installer `.py` sigue siendo el modelo preferido para futuras integraciones empaquetadas cuando el flujo pida entrega por paquete.


Directorio reservado para contrato compartido empaquetable. No crear helpers genericos aqui.

Puede contener tipos compartidos reales, event names, sync contracts, screen contracts, plugin contracts, glosario compartido y reglas de compatibilidad.

Regla twin: si cambia identidad compartida, naming compartido, eventos compartidos o sync contract, es twin change. Si solo mejora operacion local Tablet o PC, es local.
