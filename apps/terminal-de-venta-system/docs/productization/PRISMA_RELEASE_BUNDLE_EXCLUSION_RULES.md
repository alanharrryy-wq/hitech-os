---
title: PRISMA Release Bundle Exclusion Rules
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---


# PRISMA Release Bundle Exclusion Rules

Reglas para que un release de PRISMA no salga con mugrero de taller. Un bundle cliente debe parecer producto, no mochila de estudiante con tarea de tres semestres.

## 1. `.git`

**Motivo:** nunca incluir historia git.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: .git no debe empaquetarse para cliente.
```

## 2. `node_modules`

**Motivo:** nunca incluir dependencias instaladas completas.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: node_modules no debe empaquetarse para cliente.
```

## 3. `.next/cache`

**Motivo:** cache dev.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: .next/cache no debe empaquetarse para cliente.
```

## 4. `*.db`

**Motivo:** DB cliente o dev.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: *.db no debe empaquetarse para cliente.
```

## 5. `*.log`

**Motivo:** logs runtime o dev.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: *.log no debe empaquetarse para cliente.
```

## 6. `.env`

**Motivo:** secretos.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: .env no debe empaquetarse para cliente.
```

## 7. `tmp`

**Motivo:** temporales.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: tmp no debe empaquetarse para cliente.
```

## 8. `temp`

**Motivo:** temporales.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: temp no debe empaquetarse para cliente.
```

## 9. `.prisma_integration_backups`

**Motivo:** backups de integracion interna.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: .prisma_integration_backups no debe empaquetarse para cliente.
```

## 10. `coverage`

**Motivo:** cobertura dev.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: coverage no debe empaquetarse para cliente.
```

## 11. `dist/dev`

**Motivo:** salida dev.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: dist/dev no debe empaquetarse para cliente.
```

## 12. `screenshots`

**Motivo:** evidencia visual no runtime.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: screenshots no debe empaquetarse para cliente.
```

## 13. `*.tsbuildinfo`

**Motivo:** cache TypeScript.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: *.tsbuildinfo no debe empaquetarse para cliente.
```

## 14. `*.map`

**Motivo:** source maps si no hay politica.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: *.map no debe empaquetarse para cliente.
```

## 15. `docs.zip`

**Motivo:** paquetes viejos o duplicados.

**Accion del gate:** bloquear si aparece en paquete cliente, salvo excepcion documentada.

**Mensaje recomendado:**

```text
BUNDLE_EXCLUDED_PATTERN: docs.zip no debe empaquetarse para cliente.
```

## Gate minimo

Un empaquetador futuro debe listar todos los archivos incluidos, todos los excluidos y el motivo de exclusion. Si no puede explicarlo, no debe empaquetarlo.
