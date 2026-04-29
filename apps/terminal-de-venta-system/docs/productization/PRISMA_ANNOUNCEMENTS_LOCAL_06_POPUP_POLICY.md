# PRISMA_ANNOUNCEMENTS_LOCAL_06_POPUP_POLICY

**Paquete:** `PRISMA_ANNOUNCEMENTS_LOCAL_06`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Definir cuándo puede interrumpirse al usuario y cuándo no.


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


# Zonas prohibidas

Checkout activo, confirmación de cobro, cierre de venta, corte de caja, resolución de conflicto, vista de error crítico y cualquier flujo donde el usuario esté cerrando dinero o inventario.


# Zonas toleradas

Centro PRISMA, inicio de sesión, dashboard PC, pantalla de novedades, ajustes, soporte, pantalla de estado y vistas informativas.


# Frecuencia

Cada popup tiene `maxShows`, `cooldownHours`, `dismissible`, `snoozeAllowed` y `requiresAcknowledgement`. Si no trae control de frecuencia, se trata como banner o se rechaza.


# Severidad

| ID | Dominio | Criterio | Evidencia | Stop condition |
|---|---|---|---|---|
| ANN-POP-AC-001 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-002 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-003 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-004 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-005 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-006 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-007 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-008 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-009 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-010 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-011 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-012 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-013 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-014 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-015 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-016 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-017 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-018 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-019 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-020 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-021 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-022 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-023 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-024 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-025 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-026 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-027 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-028 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-029 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-030 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-031 | No bloqueo checkout | Debe validar no bloqueo checkout sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-032 | Dismisibilidad | Debe validar dismisibilidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-033 | Frecuencia | Debe validar frecuencia sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-034 | Reconocimiento | Debe validar reconocimiento sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-035 | Snooze | Debe validar snooze sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |
| ANN-POP-AC-036 | Severidad | Debe validar severidad sin romper contratos anteriores | manual/schema/test-case | bloquea si contradice 00/01/02/03/04/05 |



# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
