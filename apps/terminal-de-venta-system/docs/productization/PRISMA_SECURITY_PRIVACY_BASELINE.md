---
title: PRISMA Security Privacy Baseline
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Security and Privacy Baseline

## Decisión

Customer Operations Layer debe nacer con mínimos de seguridad y privacidad. No se necesita burocracia infinita, pero sí reglas que eviten dispararse en el pie con entusiasmo empresarial.

## Principios

1. Minimizar datos.
2. Consentimiento para diagnósticos.
3. Firma/checksum para updates y plugins.
4. No comandos arbitrarios.
5. Logs saneados.
6. No pagos bancarios.
7. No secretos en repo.
8. Exportación y backup siempre disponibles.
9. Auditoría de acciones sensibles.
10. Grace offline responsable.

## Datos prohibidos por defecto

```text
passwords
tokens
private keys
bank account data
card data
full customer DB
unredacted logs with secrets
```

## Acciones sensibles

- cambiar licencia,
- activar plugin,
- aplicar update,
- generar diagnóstico profundo,
- modificar config runtime,
- tocar sync,
- desactivar features,
- rollback.

## Auditoría mínima

```text
actorId
actorType
action
entityType
entityId
businessId
deviceId
before
after
createdAt
result
```

## Remote commands

Solo allowlist. Nunca `run arbitrary command`.

## Diagnostics

Tres niveles:

```text
basic
standard
deep
```

Cada nivel debe declarar includes/excludes.

## Plugins

Todo plugin debe declarar permisos y superficies.

## Updates

Todo update debe tener:

- manifest,
- checksum/firma,
- backup,
- verify,
- rollback.

## Licencia

Licencia puede limitar features, pero no debe impedir exportar ni respaldar datos.

## Criterio de aceptación

La capa pasa baseline si un técnico puede explicar qué datos salen, qué acciones entran y cómo se revierte un cambio sin ponerse pálido.
