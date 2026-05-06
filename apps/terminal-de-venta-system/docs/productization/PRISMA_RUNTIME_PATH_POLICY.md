---
title: PRISMA Runtime Path Policy
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Runtime Path Policy

## 1. Proposito

Definir como PRISMA debe resolver rutas de runtime sin depender del directorio actual ni del repositorio de desarrollo.

## 2. Fuentes de verdad

Orden recomendado de resolucion:

1. parametro explicito de arranque;
2. archivo `runtime.json`;
3. variable de entorno controlada;
4. fallback de desarrollo solo si `runtimeMode = dev`.

Nunca usar `process.cwd()` como raiz de datos del cliente.

## 3. Rutas canonicas cliente

| Nombre logico | Ruta recomendada |
|---|---|
| runtimeRoot | `C:\ProgramData\PRISMA` |
| configRoot | `C:\ProgramData\PRISMA\config` |
| businessRoot | `C:\ProgramData\PRISMA\businesses\<businessId>` |
| tabletDataRoot | `...\tablet\data` |
| pcDataRoot | `...\pc\data` |
| syncRoot | `...\sync` |
| supportRoot | `...\support` |
| updatesRoot | `C:\ProgramData\PRISMA\updates` |
| rollbackRoot | `C:\ProgramData\PRISMA\rollback` |

## 4. Rutas de desarrollo

En desarrollo se permite usar rutas dentro del repo, pero deben marcarse como `devOnly`.

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\data\tablet-pos.db
```

Esa ruta puede existir para pruebas. No debe ser destino de cliente.

## 5. Contrato de paths

Cada path resuelto debe incluir:

```text
key
resolvedPath
source
mode
isWritable
isCustomerData
isDevOnly
```

## 6. Verificaciones minimas

Antes de arrancar runtime cliente:

- runtimeRoot existe o puede crearse;
- configRoot existe;
- businessId existe;
- DB path no apunta al repo;
- logs path es escribible;
- backups path es escribible;
- license file existe o el modo permite bootstrap;
- si managed, syncRoot existe.

## 7. Fallos bloqueantes

Bloquear arranque administrado si:

- runtimeMode no es valido;
- customer DB apunta a repo;
- businessId esta vacio;
- license file apunta a ruta dentro de git;
- config contiene paths relativos ambiguos.

## 8. Mensaje de error humano

Los errores deben decir ruta, causa y accion.

Mal:

```text
ENOENT
```

Bien:

```text
No se encontro la carpeta runtime de PRISMA en C:\ProgramData\PRISMA. Ejecuta el instalador o selecciona una raiz runtime valida.
```
