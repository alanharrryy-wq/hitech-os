# PRISMA_AI_READY_SUPPORT_CONTEXT_09_REDACTION_POLICY

**Paquete:** `PRISMA_AI_READY_SUPPORT_CONTEXT_09`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Política de redacción para IA.


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


# Prohibido enviar

Tokens, API keys, passwords, connection strings, rutas con nombres personales sensibles, datos bancarios, datos de tarjetas, dumps DB completos, mensajes privados no autorizados.


# Transformaciones

Hash parcial de IDs, truncado de logs, conteos agregados, timestamps normalizados, ocultamiento de valores sensibles y allowlist de campos.


# Matriz

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| AI-REDACT-AC-001 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-002 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-003 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-004 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-005 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-006 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-007 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-008 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-009 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-010 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-011 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-012 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-013 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-014 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-015 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-016 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-017 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-018 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-019 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-020 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-021 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-022 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-023 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-024 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-025 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-026 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-027 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-028 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-029 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-030 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-031 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-032 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-033 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-034 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-035 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-036 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-037 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-038 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-039 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-040 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-041 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-042 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-043 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-044 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-045 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-046 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-047 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-048 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-049 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-050 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-051 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-052 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-053 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-054 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-055 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-056 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-057 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-058 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-059 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-060 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-061 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-062 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-063 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-064 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-065 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-066 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-067 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-068 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-069 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-070 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-071 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-072 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-073 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-074 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-075 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-076 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-077 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-078 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-079 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-080 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-081 | token | Debe validar token sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-082 | password | Debe validar password sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-083 | connection string | Debe validar connection string sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-084 | payment data | Debe validar payment data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-085 | personal data | Debe validar personal data sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-086 | DB dump | Debe validar db dump sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-087 | log truncation | Debe validar log truncation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| AI-REDACT-AC-088 | support consent | Debe validar support consent sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
