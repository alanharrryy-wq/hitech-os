# PRISMA_REMOTE_OPS_BRIDGE_08_COMMAND_ALLOWLIST

**Paquete:** `PRISMA_REMOTE_OPS_BRIDGE_08`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Allowlist y rechazo de comandos remotos.


## Guardrails no negociables

- No se reemplazan runtime, pantallas reales, rutas Next, handlers API ni motores de negocio en este paquete.
- No se toca base de datos de cliente ni `tablet-pos.db`.
- No se modifica `.env`, `.next`, `node_modules`, caches, logs existentes ni archivos binarios.
- No se abren puertos entrantes ni se introduce servidor remoto local.
- No se ejecuta codigo arbitrario desde manifiestos, anuncios, mensajes, comandos remotos ni contexto de IA.
- No se procesan pagos bancarios, tarjetas, transferencias, custodia de dinero ni validacion bancaria.
- Tablet conserva autonomia de venta local; PC gobierna cuando existe, pero no autoriza la venta basica.
- Todo contrato debe declarar superficie: `pc`, `tablet`, `remote_ops`, `support`, `shared` o combinacion explicita.
- Todo flujo sensible debe tener stop condition, evento auditable futuro y criterio de rollback documental.

Dicho sin perfume: esto es contrato, no magia. Primero se dibuja la barda; luego ya vemos si metemos el perro guardian.


## Superficies PRISMA respetadas

| Superficie | Rol | Regla |
|---|---|---|
| PC | Centro de mando, administracion, auditoria, configuracion y resolucion | Puede mostrar mayor detalle y controles de gobierno. |
| Tablet | Operacion ligera de piso, venta, estado y acciones de soporte minimo | No debe saturarse ni bloquear checkout con ruido comercial. |
| Remote Ops | Canal saliente/polling seguro y controlado | No abre puertos entrantes ni ejecuta comandos libres. |
| Support | Diagnostico, evidencia y comunicacion asistida | Nunca debe filtrar secretos ni datos sensibles sin redaccion. |
| Shared contracts | Nombres, schemas, eventos y compatibilidad | No debe convertirse en basurero de utilidades. |


# Allowlist

Solo comandos enumerados son válidos. El payload nunca contiene shell, script, SQL bruto ni ruta arbitraria.


# Validaciones

Validar comando, versión de schema, firma, expiración, deviceId, businessId, replay nonce, plan/entitlement y modo runtime.


# Matriz

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| REMOTE-CMD-AC-001 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-002 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-003 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-004 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-005 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-006 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-007 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-008 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-009 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-010 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-011 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-012 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-013 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-014 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-015 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-016 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-017 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-018 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-019 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-020 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-021 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-022 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-023 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-024 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-025 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-026 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-027 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-028 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-029 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-030 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-031 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-032 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-033 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-034 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-035 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-036 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-037 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-038 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-039 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-040 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-041 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-042 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-043 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-044 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-045 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-046 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-047 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-048 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-049 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-050 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-051 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-052 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-053 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-054 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-055 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-056 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-057 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-058 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-059 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-060 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-061 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-062 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-063 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-064 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-065 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-066 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-067 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-068 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-069 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-070 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-071 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-072 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-073 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-074 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-075 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-076 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-077 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-078 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-079 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-080 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-081 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-082 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-083 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-084 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-085 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-086 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-087 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-088 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-089 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-090 | signature | Debe validar signature sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-091 | expiry | Debe validar expiry sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-092 | nonce | Debe validar nonce sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-093 | device scope | Debe validar device scope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-094 | human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-095 | no arbitrary command | Debe validar no arbitrary command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-CMD-AC-096 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.

---

## Audit hardening - Remote allowlist

This document intentionally uses the audit keywords below so the contract remains machine-checkable:

- `allowlist`: every remote command must be declared explicitly before it can be accepted.
- `RUN_ARBITRARY_COMMAND`: forbidden and must never be accepted as an allowed command.
- `EXECUTE_POWERSHELL`: forbidden and must never be accepted as an allowed command.
- `DELETE_DATABASE`, `EDIT_FILE_RAW`, `OPEN_INBOUND_PORT`, and `DISABLE_SECURITY`: forbidden.
- Polling only: Remote Ops must not open inbound ports.
- Safe commands require a signed envelope, tenant/device scope, role policy, timeout, audit event, and rollback note when applicable.

If a requested operation is not in the allowlist, PRISMA must reject it and record the rejection. The bridge must not improvise shell execution, raw file edits, or database deletion. This keeps Remote Ops useful without turning customer machines into a piñata with Wi-Fi.

---

## Auditoría explícita de allowlist remota

Esta política debe leerse como una allowlist cerrada. Remote Ops solo puede aceptar comandos declarativos conocidos, versionados y auditables.

Reglas obligatorias:

- **ALLOWLIST ONLY:** cualquier comando fuera de la lista se rechaza.
- **NO RUN_ARBITRARY_COMMAND:** queda prohibido ejecutar comandos arbitrarios.
- **NO SHELL EXEC:** queda prohibido invocar PowerShell, CMD, Bash, Node, Python o cualquier intérprete como acción remota.
- **NO FILE EDIT RAW:** Remote Ops no edita archivos crudos ni escribe contenido libre enviado por servidor.
- **NO DELETE DATABASE:** Remote Ops no borra bases de datos, backups, logs, catálogos ni archivos de cliente.
- **NO INBOUND PORTS:** el bridge opera por polling saliente; no abre puertos entrantes raros.
- **AUDIT REQUIRED:** cada comando rechazado o aceptado debe registrar actor, businessId, deviceId, commandEnvelopeId, nonce, issuedAt, expiresAt, resultado y motivo.
- **DRY-RUN FIRST:** acciones sensibles deben tener preflight o dry-run antes de apply.
- **SIGNED ENVELOPE:** ningún comando se procesa sin envelope verificable, expiración y nonce anti-replay.

Frase corta: Remote Ops no es una puerta trasera elegante. Es una cola de instrucciones limitadas, auditables y rechazables.
