# PRISMA PC Backoffice

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PRISMA tiene Tablet POS standalone, PC Backoffice y contratos compartidos. Tablet no requiere PC para vender. PC no bloquea ventas locales de Tablet. Sync reconcilia eventos. Eventos son verdad operacional. Tablet usa DB local para operacion standalone.

Toda entrega relevante debe ser reversible y verificable. ZIP + installer `.py` sigue siendo el modelo preferido para futuras integraciones empaquetadas cuando el flujo pida entrega por paquete.


PC es backoffice/gobierno: catalogo, stock, conteos, compras, recepcion, reabasto, auditoria, sync, dashboard y settings.

PC puede definir politicas, publicar catalogos, ingestar eventos, reconciliar conflictos y consolidar informacion. PC no debe ser requisito para venta local basica Tablet.
