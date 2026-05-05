---
title: PRISMA License Enforcement Policy
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA License Enforcement Policy

## Estado: dev

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en dev |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: trial

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en trial |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: active

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en active |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: offline_grace

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en offline_grace |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: past_due_external

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en past_due_external |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: suspended

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en suspended |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: revoked

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en revoked |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

## Estado: expired

Comportamiento requerido:

- mostrar estado entendible al dueño/admin;
- mantener exportación y backups disponibles;
- mantener soporte disponible;
- no borrar datos;
- limitar features según entitlement;
- registrar transición en auditoría;
- respetar grace offline si aplica;
- no procesar pagos bancarios ni intentar cobrar dentro de la app.

Tabla de impacto:

| Función | Comportamiento en expired |
|---|---|
| venta local básica | según política y grace, nunca borrar historial |
| exportación | permitir |
| backup | permitir |
| soporte | permitir |
| plugins premium | bloquear si entitlement no activo |
| updates | permitir solo críticos si política lo autoriza |
| diagnóstico | permitir con consentimiento |

