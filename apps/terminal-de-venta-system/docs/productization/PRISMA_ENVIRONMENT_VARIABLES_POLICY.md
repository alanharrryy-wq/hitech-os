---
title: PRISMA Environment Variables Policy
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Environment Variables Policy

## 1. Decision

Las variables de entorno son un mecanismo de arranque, no la fuente completa de verdad.

Deben servir para encontrar la configuracion, no para esconder reglas criticas en la neblina.

## 2. Variables permitidas

| Variable | Uso |
|---|---|
| PRISMA_RUNTIME_ROOT | raiz runtime |
| PRISMA_CONFIG_ROOT | raiz config |
| PRISMA_RUNTIME_CONFIG | archivo runtime.json explicito |
| PRISMA_BUSINESS_ID | negocio activo |
| PRISMA_DEVICE_ID | dispositivo activo |
| PRISMA_RUNTIME_MODE | modo runtime |
| PRISMA_LICENSE_FILE | licencia local |
| PRISMA_TABLET_DATABASE_URL | DB Tablet |
| PRISMA_PC_DATABASE_URL | DB PC |

## 3. Variables prohibidas en commits

Nunca commitear `.env` con valores cliente.

Prohibido incluir:

- tokens;
- claves privadas;
- passwords;
- licencias firmadas cliente;
- rutas personales del cliente;
- datos bancarios;
- secretos de soporte remoto.

## 4. Precedencia

Orden recomendado:

```text
CLI explicit flag
runtime.json
environment variable
safe dev fallback
```

## 5. Auditoria

En diagnostico se puede reportar que una variable existe, pero no su valor completo si parece secreto.

Ejemplo:

```text
PRISMA_LICENSE_FILE = set
PRISMA_REMOTE_TOKEN = redacted
```
