# PRISMA_PLUGIN_MANIFEST_LOADER_07_ACCEPTANCE_MATRIX

**Paquete:** `PRISMA_PLUGIN_MANIFEST_LOADER_07`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Criterios de aceptación del loader.


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
| PLUG-07-AC-001 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-002 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-003 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-004 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-005 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-006 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-007 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-008 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-009 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-010 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-011 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-012 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-013 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-014 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-015 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-016 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-017 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-018 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-019 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-020 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-021 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-022 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-023 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-024 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-025 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-026 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-027 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-028 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-029 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-030 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-031 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-032 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-033 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-034 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-035 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-036 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-037 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-038 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-039 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-040 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-041 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-042 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-043 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-044 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-045 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-046 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-047 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-048 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-049 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-050 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-051 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-052 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-053 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-054 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-055 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-056 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-057 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-058 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-059 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-060 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-061 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-062 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-063 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-064 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-065 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-066 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-067 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-068 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-069 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-070 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-071 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-072 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-073 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-074 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-075 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-076 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-077 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-078 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-079 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-080 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-081 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-082 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-083 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-084 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-085 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-086 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-087 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-088 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-089 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-090 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-091 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-092 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-093 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-094 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-095 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-096 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-097 | Manifest schema | Debe validar manifest schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-098 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-099 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-100 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-101 | Security boundary | Debe validar security boundary sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-102 | Rollback plan | Debe validar rollback plan sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-103 | Events | Debe validar events sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-07-AC-104 | Surface mapping | Debe validar surface mapping sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
