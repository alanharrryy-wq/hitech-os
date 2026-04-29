---
title: PRISMA No Payment Processing Boundary
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA No Payment Processing Boundary

## 1. Decisión

PRISMA no procesará pagos bancarios, tarjetas, transferencias, SPEI, wallets ni pasarelas de pago dentro del producto en esta etapa.

Esta frontera existe para evitar riesgos regulatorios, operativos y de seguridad.

## 2. PRISMA no hace

```text
card processing
bank transfer initiation
SPEI validation
wallet integration
payment gateway settlement
chargebacks
PCI scope
KYC
custody of funds
bank reconciliation automation
```

## 3. PRISMA sí puede hacer

Registro operativo local:

```text
cash
manual_external_payment
store_credit
accounts_receivable
```

Pero estos son registros declarativos del operador. PRISMA no valida ni mueve dinero.

## 4. Plugins

Ningún plugin inicial puede procesar pagos bancarios.

Un plugin puede agregar reportes o formas manuales de clasificación, pero no integraciones financieras activas.

## 5. Popups comerciales

PRISMA puede mostrar:

```text
Solicitar activación
Pedir información
Contactar proveedor
```

No puede mostrar:

```text
Pagar ahora
Ingresar tarjeta
Transferir desde aquí
Conectar cuenta bancaria
```

## 6. Licencia y cobro

El cobro de licencias, upgrades o plugins ocurre fuera de PRISMA.

Dentro de PRISMA solo se refleja:

```text
entitlement active
entitlement requested
entitlement suspended
```

## 7. UX

Cuando una función no esté incluida:

```text
Esta función no está incluida en tu plan actual. Puedes solicitar activación a tu proveedor PRISMA.
```

## 8. Auditoría

Solicitudes de activación deben quedar en messaging/support, no en pagos internos.

## 9. Criterio de aceptación

La frontera está bien si ningún flujo de PRISMA requiere manejar credenciales bancarias, iniciar pagos o verificar transferencias.
