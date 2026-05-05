# Shared Error Contract

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Define errores POS canonicos y comportamiento visible.


## Canonical POS errors

- `EMPTY_CART`
- `INVALID_QUANTITY`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_INACTIVE`
- `INSUFFICIENT_STOCK`
- `TERMINAL_NOT_FOUND`
- `NETWORK_UNAVAILABLE`
- `SYNC_PENDING`

## Rules

- `EMPTY_CART`: bloquear cierre de venta y mostrar que el ticket esta vacio.
- `INVALID_QUANTITY`: bloquear linea invalida y pedir cantidad valida.
- `PRODUCT_NOT_FOUND`: informar que no se encontro producto/SKU/codigo.
- `PRODUCT_INACTIVE`: bloquear venta del producto inactivo.
- `INSUFFICIENT_STOCK`: explicar stock insuficiente sin lenguaje tecnico.
- `TERMINAL_NOT_FOUND`: pedir revisar configuracion local de terminal.
- `NETWORK_UNAVAILABLE`: informar que venta local puede continuar si el flujo lo permite.
- `SYNC_PENDING`: mostrar pendiente de sincronizacion sin bloquear venta local permitida.
