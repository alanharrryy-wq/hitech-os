# Tablet POS Reports Export

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

Define exportaciones locales Tablet y futuras exportaciones consolidadas PC.


Tablet debe poder exportar, sin PC:

- ventas del dia: `GET /api/pos/export/sales-today?format=json|csv`
- eventos: `GET /api/pos/export/events?format=json|csv`
- movimientos: `GET /api/pos/export/inventory-movements?format=json|csv`

Formatos: `json` para integraciones/soporte y `csv` para revision operativa.

Export local no depende de PC y no reemplaza sync; export es salida manual/verificable.
