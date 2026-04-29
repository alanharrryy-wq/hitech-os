# PRISMA_ANNOUNCEMENTS_LOCAL_06_ACCEPTANCE_MATRIX

**Paquete:** `PRISMA_ANNOUNCEMENTS_LOCAL_06`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Criterios de aceptación de anuncios locales.


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
| ANN-06-AC-001 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-002 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-003 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-004 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-005 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-006 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-007 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-008 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-009 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-010 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-011 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-012 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-013 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-014 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-015 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-016 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-017 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-018 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-019 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-020 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-021 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-022 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-023 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-024 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-025 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-026 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-027 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-028 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-029 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-030 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-031 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-032 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-033 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-034 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-035 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-036 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-037 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-038 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-039 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-040 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-041 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-042 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-043 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-044 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-045 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-046 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-047 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-048 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-049 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-050 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-051 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-052 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-053 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-054 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-055 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-056 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-057 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-058 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-059 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-060 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-061 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-062 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-063 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-064 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-065 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-066 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-067 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-068 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-069 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-070 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-071 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-072 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-073 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-074 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-075 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-076 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-077 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-078 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-079 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-080 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-081 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-082 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-083 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-084 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-085 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-086 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-087 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-088 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-089 | Targeting | Debe validar targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-090 | Popup policy | Debe validar popup policy sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-091 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-092 | No checkout spam | Debe validar no checkout spam sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-093 | Severity | Debe validar severity sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-094 | Version targeting | Debe validar version targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-095 | Plan targeting | Debe validar plan targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-06-AC-096 | Role targeting | Debe validar role targeting sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
