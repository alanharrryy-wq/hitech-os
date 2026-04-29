# PRISMA_08_09_IMPLEMENTATION_HANDOFF

**Paquete:** `PRISMA_REMOTE_OPS_AI_READY_08_09_FULL_DOCS`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Handoff para implementación futura.


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


# Secuencia futura

Primero schemas y examples. Luego heartbeat local mock. Luego command envelope validator read-only. Luego diagnostic bundle integration. Luego AI context builder read-only. Nada de servidor real hasta tener firma, nonce, expiry y logs.


# Stop conditions

Bloquear si abre puertos, usa shell, transmite secretos, ejecuta update sin firma, da a IA permiso de acción, contradice licencia, rompe venta Tablet offline.


# Checklist

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| HANDOFF-08-09-AC-001 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-002 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-003 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-004 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-005 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-006 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-007 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-008 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-009 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-010 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-011 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-012 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-013 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-014 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-015 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-016 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-017 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-018 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-019 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-020 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-021 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-022 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-023 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-024 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-025 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-026 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-027 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-028 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-029 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-030 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-031 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-032 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-033 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-034 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-035 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-036 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-037 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-038 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-039 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-040 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-041 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-042 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-043 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-044 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-045 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-046 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-047 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-048 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-049 | heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-050 | envelope | Debe validar envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-051 | allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-052 | redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-053 | read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-054 | consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-055 | audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-08-09-AC-056 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
