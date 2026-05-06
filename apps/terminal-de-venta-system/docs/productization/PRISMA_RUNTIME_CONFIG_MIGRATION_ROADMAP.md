---
title: PRISMA Runtime Config Migration Roadmap
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Runtime Config Migration Roadmap

## 1. Objetivo

Mover PRISMA de repo-bound a runtime-bound sin reescritura gigante.

## 2. Fase 01: contrato

Esta entrega define contratos, schemas y ejemplos.

## 3. Fase 02: resolver de rutas no invasivo

Crear una capa que lea config y resuelva rutas, pero sin cambiar todavia los flujos principales.

## 4. Fase 03: modo dev explicito

Marcar rutas de repo como `devOnly`.

## 5. Fase 04: Tablet runtime root

Permitir que Tablet use DB fuera del repo en modo customer.

## 6. Fase 05: PC runtime root

Permitir que PC use DB/config fuera del repo en modo customer.

## 7. Fase 06: Local Agent config

Introducir estado local para licencia, updates, messaging y soporte.

## 8. Fase 07: installer customer skeleton

Instalador real crea ProgramData layout, config inicial, shortcuts y verify.

## 9. Fase 08: migration gates

Backups y migraciones antes de update.

## 10. No hacer todavia

- no mover DB real sin backup;
- no conectar Remote Ops;
- no meter pago bancario;
- no crear IA ejecutora;
- no tocar ventas sin pruebas.
