# PRISMA_REMOTE_OPS_BRIDGE_08_ACCEPTANCE_MATRIX

**Paquete:** `PRISMA_REMOTE_OPS_BRIDGE_08`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Aceptación del bridge.


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


# Matriz

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| REMOTE-08-AC-001 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-002 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-003 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-004 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-005 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-006 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-007 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-008 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-009 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-010 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-011 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-012 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-013 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-014 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-015 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-016 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-017 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-018 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-019 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-020 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-021 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-022 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-023 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-024 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-025 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-026 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-027 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-028 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-029 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-030 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-031 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-032 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-033 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-034 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-035 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-036 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-037 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-038 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-039 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-040 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-041 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-042 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-043 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-044 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-045 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-046 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-047 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-048 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-049 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-050 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-051 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-052 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-053 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-054 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-055 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-056 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-057 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-058 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-059 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-060 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-061 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-062 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-063 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-064 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-065 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-066 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-067 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-068 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-069 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-070 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-071 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-072 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-073 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-074 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-075 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-076 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-077 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-078 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-079 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-080 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-081 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-082 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-083 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-084 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-085 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-086 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-087 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-088 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-089 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-090 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-091 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-092 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-093 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-094 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-095 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-096 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-097 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-098 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-099 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-100 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-101 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-102 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-103 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-104 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-105 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-106 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-107 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-108 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-109 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-110 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-111 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-112 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-113 | Polling | Debe validar polling sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-114 | Command envelope | Debe validar command envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-115 | Allowlist | Debe validar allowlist sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-116 | Heartbeat | Debe validar heartbeat sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-117 | Security | Debe validar security sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-118 | Audit | Debe validar audit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-119 | Offline fallback | Debe validar offline fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-08-AC-120 | Rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
