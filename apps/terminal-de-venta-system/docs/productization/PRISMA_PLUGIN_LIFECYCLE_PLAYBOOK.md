---
title: PRISMA Plugin Lifecycle Playbook
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA Plugin Lifecycle Playbook

## Paso: discover

Responsabilidad: definir cómo un plugin pasa por `discover` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: request

Responsabilidad: definir cómo un plugin pasa por `request` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: approve

Responsabilidad: definir cómo un plugin pasa por `approve` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: download

Responsabilidad: definir cómo un plugin pasa por `download` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: stage

Responsabilidad: definir cómo un plugin pasa por `stage` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: verify_signature

Responsabilidad: definir cómo un plugin pasa por `verify_signature` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: backup

Responsabilidad: definir cómo un plugin pasa por `backup` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: install

Responsabilidad: definir cómo un plugin pasa por `install` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: migrate

Responsabilidad: definir cómo un plugin pasa por `migrate` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: verify

Responsabilidad: definir cómo un plugin pasa por `verify` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: enable

Responsabilidad: definir cómo un plugin pasa por `enable` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: monitor

Responsabilidad: definir cómo un plugin pasa por `monitor` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: disable

Responsabilidad: definir cómo un plugin pasa por `disable` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: rollback

Responsabilidad: definir cómo un plugin pasa por `rollback` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

## Paso: archive

Responsabilidad: definir cómo un plugin pasa por `archive` sin comportarse como archivo suelto aventado al repo.

Checks mínimos:

- pluginId presente;
- versión presente;
- compatibilidad con PRISMA;
- requiredPlan declarado;
- permisos declarados;
- runtimeSurfaces declaradas;
- migraciones declaradas o explícitamente vacías;
- rollbackPlan presente;
- firma/checksum presente;
- eventos sensibles auditables.

Fallo común: tratar plugin como carpeta copiada a mano. Eso queda prohibido. Un plugin sin contrato es tamal sin hoja: se deshace en la mano y todos fingen que no vieron.

