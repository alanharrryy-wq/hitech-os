# PRISMA 03-04-05 — Screen Copy Catalog


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: documentación y contratos.  
> Prohibido: runtime, DB, `.env`, comunicación remota, pagos, ejecución de plugins y updates reales.


## Propósito

Catálogo de textos seguros para estados del Centro PRISMA, soporte y mensajería mock. La UI futura debe usar textos que no prometan backend real ni asusten al usuario con errores falsos.

## Catálogo

| Módulo | Estado | Significado | Copy recomendado | Límite |
| --- | --- | --- | --- | --- |
| Centro | empty | Estado vacío normal | Centro: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | mock_local | Modo mock local | Centro: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | read_only | Solo lectura | Centro: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | requires_permission | Requiere permiso | Centro: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | requires_consent | Requiere consentimiento | Centro: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | blocked_by_plan | Bloqueado por plan | Centro: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | offline | Sin conexión | Centro: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Centro | error_safe | Error seguro | Centro: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | empty | Estado vacío normal | Mi Plan: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | mock_local | Modo mock local | Mi Plan: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | read_only | Solo lectura | Mi Plan: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | requires_permission | Requiere permiso | Mi Plan: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | requires_consent | Requiere consentimiento | Mi Plan: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | blocked_by_plan | Bloqueado por plan | Mi Plan: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | offline | Sin conexión | Mi Plan: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mi Plan | error_safe | Error seguro | Mi Plan: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | empty | Estado vacío normal | Plugins: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | mock_local | Modo mock local | Plugins: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | read_only | Solo lectura | Plugins: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | requires_permission | Requiere permiso | Plugins: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | requires_consent | Requiere consentimiento | Plugins: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | blocked_by_plan | Bloqueado por plan | Plugins: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | offline | Sin conexión | Plugins: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Plugins | error_safe | Error seguro | Plugins: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | empty | Estado vacío normal | Soporte: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | mock_local | Modo mock local | Soporte: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | read_only | Solo lectura | Soporte: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | requires_permission | Requiere permiso | Soporte: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | requires_consent | Requiere consentimiento | Soporte: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | blocked_by_plan | Bloqueado por plan | Soporte: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | offline | Sin conexión | Soporte: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte | error_safe | Error seguro | Soporte: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | empty | Estado vacío normal | Mensajes: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | mock_local | Modo mock local | Mensajes: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | read_only | Solo lectura | Mensajes: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | requires_permission | Requiere permiso | Mensajes: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | requires_consent | Requiere consentimiento | Mensajes: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | blocked_by_plan | Bloqueado por plan | Mensajes: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | offline | Sin conexión | Mensajes: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes | error_safe | Error seguro | Mensajes: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | empty | Estado vacío normal | Novedades: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | mock_local | Modo mock local | Novedades: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | read_only | Solo lectura | Novedades: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | requires_permission | Requiere permiso | Novedades: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | requires_consent | Requiere consentimiento | Novedades: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | blocked_by_plan | Bloqueado por plan | Novedades: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | offline | Sin conexión | Novedades: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades | error_safe | Error seguro | Novedades: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | empty | Estado vacío normal | Diagnóstico: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | mock_local | Modo mock local | Diagnóstico: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | read_only | Solo lectura | Diagnóstico: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | requires_permission | Requiere permiso | Diagnóstico: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | requires_consent | Requiere consentimiento | Diagnóstico: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | blocked_by_plan | Bloqueado por plan | Diagnóstico: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | offline | Sin conexión | Diagnóstico: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Diagnóstico | error_safe | Error seguro | Diagnóstico: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | empty | Estado vacío normal | Actualizaciones: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | mock_local | Modo mock local | Actualizaciones: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | read_only | Solo lectura | Actualizaciones: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | requires_permission | Requiere permiso | Actualizaciones: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | requires_consent | Requiere consentimiento | Actualizaciones: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | blocked_by_plan | Bloqueado por plan | Actualizaciones: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | offline | Sin conexión | Actualizaciones: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Actualizaciones | error_safe | Error seguro | Actualizaciones: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | empty | Estado vacío normal | Estado Tablet: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | mock_local | Modo mock local | Estado Tablet: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | read_only | Solo lectura | Estado Tablet: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | requires_permission | Requiere permiso | Estado Tablet: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | requires_consent | Requiere consentimiento | Estado Tablet: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | blocked_by_plan | Bloqueado por plan | Estado Tablet: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | offline | Sin conexión | Estado Tablet: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Estado Tablet | error_safe | Error seguro | Estado Tablet: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | empty | Estado vacío normal | Soporte Tablet: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | mock_local | Modo mock local | Soporte Tablet: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | read_only | Solo lectura | Soporte Tablet: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | requires_permission | Requiere permiso | Soporte Tablet: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | requires_consent | Requiere consentimiento | Soporte Tablet: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | blocked_by_plan | Bloqueado por plan | Soporte Tablet: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | offline | Sin conexión | Soporte Tablet: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Soporte Tablet | error_safe | Error seguro | Soporte Tablet: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | empty | Estado vacío normal | Mensajes Tablet: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | mock_local | Modo mock local | Mensajes Tablet: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | read_only | Solo lectura | Mensajes Tablet: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | requires_permission | Requiere permiso | Mensajes Tablet: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | requires_consent | Requiere consentimiento | Mensajes Tablet: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | blocked_by_plan | Bloqueado por plan | Mensajes Tablet: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | offline | Sin conexión | Mensajes Tablet: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Mensajes Tablet | error_safe | Error seguro | Mensajes Tablet: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | empty | Estado vacío normal | Novedades Tablet: esta sección está en estado empty. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | mock_local | Modo mock local | Novedades Tablet: esta sección está en estado mock_local. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | read_only | Solo lectura | Novedades Tablet: esta sección está en estado read_only. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | requires_permission | Requiere permiso | Novedades Tablet: esta sección está en estado requires_permission. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | requires_consent | Requiere consentimiento | Novedades Tablet: esta sección está en estado requires_consent. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | blocked_by_plan | Bloqueado por plan | Novedades Tablet: esta sección está en estado blocked_by_plan. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | offline | Sin conexión | Novedades Tablet: esta sección está en estado offline. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |
| Novedades Tablet | error_safe | Error seguro | Novedades Tablet: esta sección está en estado error_safe. La operación principal se mantiene segura. | No se ejecutan acciones reales desde esta vista. |

## Reglas de copy

- No decir “enviado” en paquete 05.
- No decir “actualizado” antes de paquete 08.
- No decir “plugin instalado” antes de paquete 07.
- No decir “diagnóstico generado” antes de implementación real 04.
- No decir “pago”, “tarjeta”, “SPEI” ni “procesamiento bancario”.
- No usar “error” cuando sea estado vacío normal.
- No usar “bloqueado” para plan limitado si puede sonar a secuestro de datos.
