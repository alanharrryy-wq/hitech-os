# PRISMA_AI_READY_SUPPORT_CONTEXT_09_ACCEPTANCE_MATRIX

**Paquete:** `PRISMA_AI_READY_SUPPORT_CONTEXT_09`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Aceptación del contexto IA.


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
| AI-09-AC-001 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-002 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-003 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-004 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-005 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-006 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-007 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-008 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-009 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-010 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-011 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-012 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-013 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-014 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-015 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-016 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-017 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-018 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-019 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-020 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-021 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-022 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-023 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-024 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-025 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-026 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-027 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-028 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-029 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-030 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-031 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-032 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-033 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-034 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-035 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-036 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-037 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-038 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-039 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-040 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-041 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-042 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-043 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-044 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-045 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-046 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-047 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-048 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-049 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-050 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-051 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-052 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-053 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-054 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-055 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-056 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-057 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-058 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-059 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-060 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-061 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-062 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-063 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-064 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-065 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-066 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-067 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-068 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-069 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-070 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-071 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-072 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-073 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-074 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-075 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-076 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-077 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-078 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-079 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-080 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-081 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-082 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-083 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-084 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-085 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-086 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-087 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-088 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-089 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-090 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-091 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-092 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-093 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-094 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-095 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-096 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-097 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-098 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-099 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-100 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-101 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-102 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-103 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-104 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-105 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-106 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-107 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-108 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-109 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-110 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-111 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-112 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-113 | Read-only | Debe validar read-only sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-114 | Redaction | Debe validar redaction sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-115 | Source refs | Debe validar source refs sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-116 | Forbidden actions | Debe validar forbidden actions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-117 | Support summary | Debe validar support summary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-118 | Consent | Debe validar consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-119 | No hallucinated evidence | Debe validar no hallucinated evidence sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-09-AC-120 | Human approval | Debe validar human approval sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
