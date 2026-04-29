# PRISMA_AI_READY_SUPPORT_CONTEXT_09_SUGGESTION_POLICY

**Paquete:** `PRISMA_AI_READY_SUPPORT_CONTEXT_09`

**Estado:** documento contractual para instalación posterior.

**Propósito:** Política de sugerencias de IA.


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


# Permitido

Explicar error, resumir diagnóstico, proponer pasos manuales, clasificar severidad, sugerir revisión de permisos, recomendar generar bundle, preparar mensaje para soporte.


# Prohibido

Ejecutar comandos, editar archivos, borrar DB, cambiar precios, modificar stock, activar/desactivar plugins, aprobar updates, bloquear licencias o procesar pagos.


# Escalamiento

Si la sugerencia afecta dinero, inventario, licencia, update o plugin, requiere confirmación humana y acción por flujo gobernado.


# Cierre operativo

Este documento existe para que la implementación posterior no llegue como primo con taladro: mucho ruido, poca responsabilidad. Cualquier cambio futuro debe poder demostrar qué lee, qué escribe, qué bloquea, qué audita y cómo se revierte.

---

## Audit hardening - AI read-only suggestion policy

This document intentionally uses the audit keywords below so the AI support context remains machine-checkable:

- `read-only`: AI may inspect sanitized support context only.
- `no ejecuta`: AI must not execute commands, mutate files, change license state, edit configuration, or trigger Remote Ops.
- `human`: every suggested action requires human review and explicit operator approval.
- AI output is advisory: suggestion, diagnosis, checklist, or draft response only.
- Redaction is mandatory before context reaches AI: secrets, tokens, keys, passwords, URLs with credentials, customer private data, and payment-like sensitive fields must be masked.

If a future AI workflow needs write access, it must be designed as a separate governed package. For 00-09, AI is a read-only advisor, not a tiny intern with admin rights and bad ideas.

---

## Auditoría explícita de IA read-only

El contexto AI-ready es estrictamente de lectura y sugerencia. No ejecuta acciones, no modifica archivos, no corre comandos y no toma decisiones operativas por sí solo.

Reglas obligatorias:

- **READ-ONLY:** la IA solo lee contexto permitido y redactado.
- **NO EXECUTE:** la IA no ejecuta comandos, scripts, SQL, shells ni acciones remotas.
- **NO WRITE:** la IA no escribe archivos, no cambia configuración, no activa plugins y no modifica licencias.
- **NO SECRET EXPOSURE:** todo secreto, token, API key, connection string o dato sensible debe aparecer como `[REDACTED]`.
- **SUGGESTIONS ONLY:** la IA puede sugerir pasos, explicar hallazgos y preparar drafts, pero un humano o un flujo aprobado decide.
- **SOURCE REFS REQUIRED:** toda sugerencia debe poder apuntar a `sourceRefs` permitidos.
- **CONSTRAINTS REQUIRED:** cada contexto debe declarar restricciones como `read-only`, `no-exec`, `no-secrets` y `human-approval-required`.
- **AUDITABLE:** cada paquete de contexto debe dejar rastro de generación, redacción y superficie de origen.

Frase corta: la IA ayuda a pensar, no agarra el volante como tío confiado manejando en lluvia.
