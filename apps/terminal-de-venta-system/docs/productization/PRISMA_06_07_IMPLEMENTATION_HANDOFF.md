# PRISMA_06_07_IMPLEMENTATION_HANDOFF

**Paquete:** `PRISMA_ANNOUNCEMENTS_PLUGIN_LOCAL_06_07_FULL_DOCS`

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


# Objetivo técnico futuro

Crear pantalla local de novedades y un lector de manifests que no ejecute nada. La primera versión puede leer JSON local desde ruta de desarrollo o ProgramData, validar y mostrar estado.


# Stop conditions

Bloquear si requiere server remoto, si abre puerto, si ejecuta código, si toca DB productiva, si modifica checkout, si contradice licencia 02, si escribe fuera de runtime root.


# Checklist de implementación

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| HANDOFF-06-07-AC-001 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-002 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-003 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-004 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-005 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-006 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-007 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-008 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-009 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-010 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-011 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-012 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-013 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-014 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-015 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-016 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-017 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-018 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-019 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-020 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-021 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-022 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-023 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-024 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-025 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-026 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-027 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-028 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-029 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-030 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-031 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-032 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-033 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-034 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-035 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-036 | schema | Debe validar schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-037 | example | Debe validar example sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-038 | mock UI | Debe validar mock ui sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-039 | permission map | Debe validar permission map sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-040 | safe fallback | Debe validar safe fallback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-041 | rollback | Debe validar rollback sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| HANDOFF-06-07-AC-042 | audit future | Debe validar audit future sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
