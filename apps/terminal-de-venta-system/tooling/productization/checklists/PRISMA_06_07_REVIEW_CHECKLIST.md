# PRISMA 06/07 Review Checklist

**Paquete:** `PRISMA_ANNOUNCEMENTS_PLUGIN_LOCAL_06_07_FULL_DOCS`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Checklist para revisar paquete 06/07.


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


# Checklist

- [ ] No hay codigo ejecutable
- [ ] No hay DB
- [ ] No hay .env
- [ ] No hay node_modules
- [ ] No hay .next
- [ ] Announcements no bloquea checkout
- [ ] Plugin loader no ejecuta comandos
- [ ] Schemas parsean
- [ ] Examples parsean
- [ ] Test cases existen
- [ ] Manifest no se auto-hashea
- [ ] Checksums externos presentes
- [ ] No contradice 00-05
- [ ] Rutas relativas seguras
- [ ] Installer plan documental presente
- [ ] No hay codigo ejecutable
- [ ] No hay DB
- [ ] No hay .env
- [ ] No hay node_modules
- [ ] No hay .next
- [ ] Announcements no bloquea checkout
- [ ] Plugin loader no ejecuta comandos
- [ ] Schemas parsean
- [ ] Examples parsean
- [ ] Test cases existen
- [ ] Manifest no se auto-hashea
- [ ] Checksums externos presentes
- [ ] No contradice 00-05
- [ ] Rutas relativas seguras
- [ ] Installer plan documental presente
- [ ] No hay codigo ejecutable
- [ ] No hay DB
- [ ] No hay .env
- [ ] No hay node_modules
- [ ] No hay .next
- [ ] Announcements no bloquea checkout
- [ ] Plugin loader no ejecuta comandos
- [ ] Schemas parsean
- [ ] Examples parsean
- [ ] Test cases existen
- [ ] Manifest no se auto-hashea
- [ ] Checksums externos presentes
- [ ] No contradice 00-05
- [ ] Rutas relativas seguras
- [ ] Installer plan documental presente
- [ ] No hay codigo ejecutable
- [ ] No hay DB
- [ ] No hay .env
- [ ] No hay node_modules
- [ ] No hay .next
- [ ] Announcements no bloquea checkout
- [ ] Plugin loader no ejecuta comandos
- [ ] Schemas parsean
- [ ] Examples parsean
- [ ] Test cases existen
- [ ] Manifest no se auto-hashea
- [ ] Checksums externos presentes
- [ ] No contradice 00-05
- [ ] Rutas relativas seguras
- [ ] Installer plan documental presente


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.
