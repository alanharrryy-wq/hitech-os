---
title: PRISMA Customer Installation Modes
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Customer Installation Modes

## 1. Modos de instalacion

| Modo | Incluye | Cliente ideal |
|---|---|---|
| TABLET_SOLO | Tablet POS + runtime local | negocio chico |
| TABLET_PRO | Tablet POS + operacion avanzada | negocio con empleados |
| PC_BACKOFFICE | PC administrativo | negocio que requiere gobierno |
| TABLET_PC_MANAGED | Tablet + PC + sync | negocio administrado |

## 2. TABLET_SOLO

Instala:

- app Tablet;
- DB local;
- config local;
- exports;
- backups;
- logs;
- soporte basico.

No requiere PC.

## 3. TABLET_PRO

Agrega:

- devoluciones;
- turnos;
- ajustes locales;
- outbox visible;
- soporte mejorado;
- plugins permitidos.

## 4. PC_BACKOFFICE

Instala:

- PC Backoffice;
- DB PC;
- catalogo;
- inventario;
- dashboard;
- auditoria;
- sync ingest si aplica.

## 5. TABLET_PC_MANAGED

Instala o coordina:

- Tablet POS;
- PC Backoffice;
- Local Agent;
- sync local;
- device registry;
- licencias y entitlements;
- soporte y diagnosticos.

## 6. Regla de continuidad

Tablet no debe dejar de vender por falta de PC, Remote Ops o internet.
