# PRISMA 06/07 Traceability Matrix

**Paquete:** `PRISMA_ANNOUNCEMENTS_PLUGIN_LOCAL_06_07_FULL_DOCS`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Vincular requisitos con schemas, examples y test cases.


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


# Trazabilidad

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| TRACE-06-07-AC-001 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-002 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-003 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-004 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-005 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-006 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-007 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-008 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-009 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-010 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-011 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-012 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-013 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-014 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-015 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-016 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-017 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-018 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-019 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-020 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-021 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-022 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-023 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-024 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-025 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-026 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-027 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-028 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-029 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-030 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-031 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-032 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-033 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-034 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-035 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-036 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-037 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-038 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-039 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-040 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-041 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-042 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-043 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-044 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-045 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-046 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-047 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-048 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-049 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-050 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-051 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-052 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-053 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-054 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-055 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-056 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-057 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-058 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-059 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-060 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-061 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-062 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-063 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-064 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-065 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-066 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-067 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-068 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-069 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-070 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-071 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-072 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-073 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-074 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-075 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-076 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-077 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-078 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-079 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-080 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-081 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-082 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-083 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-084 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-085 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-086 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-087 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-088 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-089 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-090 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-091 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-092 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-093 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-094 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-095 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-096 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-097 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-098 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-099 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-100 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-101 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-102 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-103 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-104 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-105 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-106 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-107 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-108 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-109 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-110 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-111 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-112 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-113 | Announcement schema | Debe validar announcement schema sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-114 | Read state | Debe validar read state sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-115 | Plugin manifest | Debe validar plugin manifest sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-116 | Compatibility | Debe validar compatibility sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-117 | Permissions | Debe validar permissions sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-118 | Entitlements | Debe validar entitlements sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-119 | No execution | Debe validar no execution sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| TRACE-06-07-AC-120 | No checkout popup | Debe validar no checkout popup sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
