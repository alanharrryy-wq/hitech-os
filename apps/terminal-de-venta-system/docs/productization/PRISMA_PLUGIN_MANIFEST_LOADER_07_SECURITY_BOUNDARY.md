# PRISMA_PLUGIN_MANIFEST_LOADER_07_SECURITY_BOUNDARY

**Paquete:** `PRISMA_PLUGIN_MANIFEST_LOADER_07`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Frontera de seguridad del loader.


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


# No ejecución arbitraria

El paquete 07 solo lee manifiestos y valida declaraciones. No carga módulos ejecutables, no evalúa JS remoto, no ejecuta comandos, no corre migraciones ni instala dependencias.


# Allowlist

Toda capacidad se compara contra catálogos conocidos. Lo desconocido se rechaza. Nada de “igual es opcional”.


# Datos y rutas

Cualquier storage declarado debe ir bajo runtime config 01. Nada de escribir en repo, escritorio, system32, temp misterioso o carpetas con olor a accidente.


# Casos de abuso

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| PLUG-SEC-AC-001 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-002 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-003 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-004 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-005 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-006 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-007 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-008 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-009 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-010 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-011 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-012 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-013 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-014 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-015 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-016 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-017 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-018 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-019 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-020 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-021 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-022 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-023 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-024 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-025 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-026 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-027 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-028 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-029 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-030 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-031 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-032 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-033 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-034 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-035 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-036 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-037 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-038 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-039 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-040 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-041 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-042 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-043 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-044 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-045 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-046 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-047 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-048 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-049 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-050 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-051 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-052 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-053 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-054 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-055 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-056 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-057 | raw command | Debe validar raw command sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-058 | raw SQL | Debe validar raw sql sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-059 | secret exfiltration | Debe validar secret exfiltration sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-060 | permission escalation | Debe validar permission escalation sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-061 | checkout hijack | Debe validar checkout hijack sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-062 | inbound port | Debe validar inbound port sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| PLUG-SEC-AC-063 | payment processing | Debe validar payment processing sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
