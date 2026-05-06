# Shared Screen Contract

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

Define screens compartidas por contrato sin forzar paridad visual entre PC y Tablet.


## Principio

Screen contract describe identidad, intencion, eventos, permisos y estados. No obliga a que PC y Tablet tengan la misma UI ni la misma densidad.

## Campos minimos

- `screenId`
- `surface`: `tablet` | `pc` | `shared`
- `module`
- `route`
- `states`
- `eventsEmitted`
- `permissionsRequired`
- `offlineBehavior`
- `syncBehavior`

Tablet screens priorizan tacto, venta y continuidad offline. PC screens priorizan control, tablas, auditoria, dashboard y excepciones.
