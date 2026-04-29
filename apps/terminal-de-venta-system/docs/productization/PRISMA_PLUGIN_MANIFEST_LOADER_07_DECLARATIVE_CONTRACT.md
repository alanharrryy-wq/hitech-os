# PRISMA_PLUGIN_MANIFEST_LOADER_07_DECLARATIVE_CONTRACT

**Paquete:** `PRISMA_PLUGIN_MANIFEST_LOADER_07`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Contratos declarativos para plugins.


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


# Qué puede declarar

| Declaración | Uso | Regla |
|---|---|---|
| capability | Capacidad funcional | Debe mapear a feature/entitlement |
| route | Ruta visible en PC/Tablet | Debe respetar shell 03 |
| permission | Permiso requerido | Debe estar en catálogo |
| event | Evento emitido | Debe tener schema |
| storage | Necesidad de storage | Solo rutas runtime 01 |
| announcement | Avisos del plugin | Debe pasar policy 06 |
| diagnostic | Campos de diagnostico | Debe respetar support 04 |



# Qué no puede declarar

`runCommand`, `powershell`, `shell`, `rawSql`, `deleteDatabase`, `editFileRaw`, `openInboundPort`, `uploadSecrets`, `paymentProcessor`.


# Contrato con 02

Si el plugin requiere plan o feature, eso se resuelve vía License Local Mock 02 y futuras licencias reales. El plugin no decide por su cuenta quién pagó. Qué cómodo sería, ¿no? También sería desastre.


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
