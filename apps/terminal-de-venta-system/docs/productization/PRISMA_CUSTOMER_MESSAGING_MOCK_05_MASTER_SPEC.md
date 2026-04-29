# PRISMA Customer Messaging Mock 05 — Master Spec


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Objetivo

Definir mensajería local mock sin servidor real. Sirve para validar flujo de mensajes, categorías, threads, estados y relación con soporte/diagnóstico sin abrir comunicación remota.

## Categorías

| Categoría | Uso | Superficie |
| --- | --- | --- |
| support | ayuda operativa | PC/Tablet |
| license | dudas de plan | PC |
| diagnostics | solicitud de diagnóstico | PC |
| plugins | dudas de plugins | PC |
| updates | dudas de actualización | PC |
| general | mensaje general | PC/Tablet |

## Estados de thread

| Estado | Significado |
| --- | --- |
| draft | creado localmente, no confirmado |
| local_only | existe solo local |
| queued_mock | simula cola futura |
| read | leído local |
| closed_local | cerrado local |
| blocked_no_server | no puede enviarse porque no hay servidor |

## Estados de mensaje

| Estado | Significado |
| --- | --- |
| draft | borrador |
| created_local | creado local |
| queued_mock | cola mock |
| failed_mock | falló simulación |
| read_local | leído local |

## Adjuntos permitidos

Solo referencias controladas:

- diagnosticBundleId
- screenshotId futuro controlado
- packageId
- routeId
- logExcerptId redactado
- licenseStateRef

Nada de archivos libres. Un adjunto libre en mensajería mock es una fuga esperando encontrar puerta.

## Límites

- Sin servidor.
- Sin polling.
- Sin websockets.
- Sin SMTP.
- Sin WhatsApp automático.
- Sin API externa.
- Sin promesa de SLA.
- Sin bloqueo de venta.
