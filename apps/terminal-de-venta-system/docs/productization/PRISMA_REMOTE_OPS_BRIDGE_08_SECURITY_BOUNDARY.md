# PRISMA_REMOTE_OPS_BRIDGE_08_SECURITY_BOUNDARY

**Paquete:** `PRISMA_REMOTE_OPS_BRIDGE_08`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Frontera de seguridad Remote Ops.


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


# No inbound

No hay puertos entrantes. No hay túnel remoto. No hay ejecución shell. No hay edición raw de archivos.


# Datos

El bridge lee estados permitidos y ejecuta acciones permitidas. Nunca secuestra datos del cliente ni bloquea venta local por capricho remoto.


# Abuse cases

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| REMOTE-ABUSE-AC-001 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-002 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-003 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-004 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-005 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-006 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-007 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-008 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-009 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-010 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-011 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-012 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-013 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-014 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-015 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-016 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-017 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-018 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-019 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-020 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-021 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-022 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-023 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-024 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-025 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-026 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-027 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-028 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-029 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-030 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-031 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-032 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-033 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-034 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-035 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-036 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-037 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-038 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-039 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-040 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-041 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-042 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-043 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-044 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-045 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-046 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-047 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-048 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-049 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-050 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-051 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-052 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-053 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-054 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-055 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-056 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-057 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-058 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-059 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-060 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-061 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-062 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-063 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-064 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-065 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-066 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-067 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-068 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-069 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-070 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-071 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-072 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-073 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-074 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-075 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-076 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-077 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-078 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-079 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-080 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-081 | shell injection | Debe validar shell injection sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-082 | command replay | Debe validar command replay sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-083 | expired envelope | Debe validar expired envelope sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-084 | wrong device | Debe validar wrong device sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-085 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-086 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-087 | raw file edit | Debe validar raw file edit sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| REMOTE-ABUSE-AC-088 | database delete | Debe validar database delete sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
