# PRISMA_AI_READY_SUPPORT_CONTEXT_09_MASTER_SPEC

**Paquete:** `PRISMA_AI_READY_SUPPORT_CONTEXT_09`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Definir contexto read-only para IA futura.


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


# Alcance

AI Ready Support Context 09 prepara datos estructurados para que una IA futura pueda explicar estado, resumir diagnóstico y sugerir acciones. No ejecuta acciones, no modifica ventas, no toca stock, no cambia precios, no mueve licencias y no responde como autoridad automática.


# Principio read-only

La IA lee contexto redactado y autorizado. Si sugiere algo, un humano decide. Sí, incluso si la IA se siente inspirada. Aquí no damos llaves del local al robot con autoestima.


# Contextos

diagnosticSummary, licenseSummary, runtimeSummary, syncSummary, supportThreadSummary, pluginSummary, announcementSummary, recentErrorSummary.


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
