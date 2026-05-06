---
title: PRISMA Runtime Config Schema Contract
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Runtime Config Schema Contract

## 1. Objetivo

Definir el contrato minimo de configuracion runtime.

El archivo principal debe ser:

```text
C:\ProgramData\PRISMA\config\runtime.json
```

## 2. Campos minimos

```json
{
  "schemaVersion": "1.0.0",
  "runtimeMode": "standalone",
  "runtimeRoot": "C:\\ProgramData\\PRISMA",
  "businessId": "demo-prisma-store",
  "deviceId": "tablet-001",
  "packageType": "TABLET_SOLO",
  "paths": {},
  "license": {},
  "sync": {},
  "features": {},
  "support": {},
  "updates": {}
}
```

## 3. runtimeMode

Valores permitidos:

```text
dev
standalone
pro
pc_backoffice
managed
degraded_managed
```

## 4. packageType

Valores permitidos:

```text
TABLET_SOLO
TABLET_PRO
PC_BACKOFFICE
TABLET_PC_MANAGED
DEV
```

## 5. paths

Debe resolver rutas absolutas. Las rutas relativas solo se aceptan en fixtures de prueba.

## 6. license

La licencia se referencia por path, no se incrusta completa si contiene firma o datos sensibles.

## 7. sync

Sync puede estar apagado en Tablet Solo. En Managed, debe declarar endpoint local o estrategia de intercambio.

## 8. support

Debe declarar si diagnosticos remotos estan habilitados y si requieren consentimiento.

## 9. updates

Debe declarar canal, politica de staging y bloqueo durante venta/turno.

## 10. Errores esperados

| Codigo | Significado |
|---|---|
| RUNTIME_CONFIG_MISSING | no existe runtime.json |
| RUNTIME_ROOT_INVALID | raiz runtime invalida |
| BUSINESS_ID_MISSING | falta businessId |
| DEVICE_ID_MISSING | falta deviceId |
| PATH_POINTS_TO_REPO | ruta cliente apunta al repo |
| RELATIVE_PATH_NOT_ALLOWED | ruta relativa en modo cliente |
| LICENSE_FILE_MISSING | falta licencia local |
| SYNC_CONFIG_INVALID | sync incompleto para modo administrado |
