# PRISMA_REMOTE_OPS_BRIDGE_08_MASTER_SPEC

**Paquete:** `PRISMA_REMOTE_OPS_BRIDGE_08`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Definir bridge remoto por polling seguro sin puertos entrantes.


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

Remote Ops Bridge 08 prepara la arquitectura para que dispositivos PRISMA consulten tareas remotas permitidas, reporten heartbeat y suban resultados controlados. No abre puertos entrantes ni expone API local pública.


# Flujo

Device -> polling saliente -> recibe envelope firmado -> valida allowlist -> decide si aplica -> ejecuta solo acción futura permitida -> reporta resultado -> audita.


# Comandos permitidos

| Comando | Uso | Regla |
|---|---|---|
| CHECK_HEALTH | Leer estado local | read-only |
| GENERATE_DIAGNOSTIC_BUNDLE | Generar soporte local | requiere consentimiento/policy |
| REFRESH_LICENSE | Refrescar licencia | no toca datos cliente |
| CHECK_FOR_UPDATES | Consultar updates | read-only |
| STAGE_UPDATE | Preparar update | sin apply directo |
| APPLY_APPROVED_UPDATE | Aplicar update aprobado | requiere firma y rollback |
| DISABLE_PLUGIN | Deshabilitar plugin | no borra datos |
| ENABLE_PLUGIN | Habilitar plugin | requiere entitlement |
| RETRY_SYNC | Reintentar sync | auditable |



# Comandos prohibidos

`RUN_ARBITRARY_COMMAND`, `EXECUTE_POWERSHELL`, `DELETE_DATABASE`, `EDIT_FILE_RAW`, `OPEN_INBOUND_PORT`, `UPLOAD_SECRETS`, `PROCESS_PAYMENT`. Si aparece uno de estos, rechazo duro y evento de seguridad.


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
