# PRISMA_ANNOUNCEMENTS_LOCAL_06_MASTER_SPEC

**Paquete:** `PRISMA_ANNOUNCEMENTS_LOCAL_06`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Definir novedades, banners y popups locales controlados por rol, plan, severidad, version y superficie.


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


# Alcance funcional

Announcements 06 permite declarar mensajes locales de producto, banners, avisos operativos, novedades, alerts y popups controlados. No es sistema publicitario salvaje ni chat. Es comunicacion gobernada dentro de Centro PRISMA.


# Tipos de anuncio

| Tipo | Uso | Superficie | Regla |
|---|---|---|---|
| banner | Informativo persistente | PC y Tablet | Nunca tapa checkout |
| modal | Interrupcion controlada | PC principalmente | Solo severidad alta o accion requerida |
| toast | Aviso breve | PC y Tablet | No se usa para ventas agresivas |
| release_note | Novedad de version | PC | Agrupada por version |
| support_notice | Aviso soporte | PC y Tablet | Ligado a diagnostico o mensaje |
| maintenance_notice | Mantenimiento | PC y Tablet | Debe tener ventana temporal |



# Targeting

Todo anuncio declara `targetPlans`, `targetRoles`, `targetVersions`, `targetSurfaces`, `severity`, `showFrom`, `showUntil`, `frequencyPolicy` y `dismissPolicy`. Si no declara target, se trata como borrador no publicable.


# No checkout spam

Regla de oro: no popup comercial durante checkout. Si la Tablet está en venta, solo se permiten avisos críticos no comerciales y con diseño no invasivo.


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
