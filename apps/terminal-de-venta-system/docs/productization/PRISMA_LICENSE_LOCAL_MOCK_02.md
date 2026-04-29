---
title: PRISMA License Local Mock 02
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License Local Mock 02

## 1. Decision madre

Esta entrega define el contrato inicial para licencia local, planes, feature flags, entitlements y grace offline.

No implementa servidor remoto. No valida pagos. No cambia Tablet ni PC. No bloquea ventas. No toca DB productiva. Es un mock contractual instalable que deja listos los archivos de referencia para que la siguiente etapa construya la primera lectura local real.

Dicho en barrio fino: primero ponemos la chapa, la llave y la lista de quien puede entrar; todavia no contratamos al guardia con radio ni abrimos la caseta.

## 2. Objetivo

PRISMA debe poder operar con un archivo local de licencia que indique:

- negocio;
- dispositivo;
- plan;
- estado;
- features habilitadas;
- plugins permitidos;
- periodo de validez;
- periodo de gracia offline;
- fecha de ultima revision remota;
- firma futura.

## 3. Resultado esperado de esta fase

La fase deja instalados:

- contrato de licencia local;
- maquina de estados;
- catalogo de planes;
- catalogo de feature keys;
- contrato de entitlements;
- ejemplos JSON;
- schemas JSON;
- playbooks de suspension y grace;
- checklist para implementacion futura;
- plan de instalador.

## 4. No alcance

Esta entrega no hace:

- procesamiento de pagos;
- Remote Ops real;
- llamadas HTTP;
- validacion criptografica real;
- UI de Mi Plan;
- bloqueo de rutas;
- instalacion de plugins;
- migracion de DB;
- cambios en Tablet POS;
- cambios en PC Backoffice.

## 5. Regla de producto

```text
Licencia habilita capacidades.
Licencia no secuestra datos.
Grace offline protege continuidad.
Suspension limita funciones futuras.
Exportar y respaldar siempre debe ser posible.
```

## 6. Estados canonicos

| Estado | Uso | Venta local basica | Exportar datos | Plugins premium |
|---|---|---:|---:|---:|
| dev | desarrollo local | si | si | si |
| trial | prueba | si | si | segun trial |
| active | licencia vigente | si | si | segun plan |
| offline_grace | no pudo validar remoto | si temporal | si | conserva estado previo temporal |
| past_due_external | pendiente administrativo externo | si temporal | si | limitar premium |
| suspended | suspendida | grace o bloqueo gradual | si | no |
| revoked | revocada | no nuevas operaciones comerciales tras grace | si | no |
| expired | vencida | grace si aplica | si | no |

## 7. Planes iniciales

| Plan | Descripcion |
|---|---|
| TABLET_SOLO | POS standalone con venta, ticket, stock local, reporte basico y exportacion |
| TABLET_PRO | Tablet con devoluciones, turnos, ajustes locales controlados, outbox visible y export avanzado |
| PC_BACKOFFICE | Panel administrativo, catalogo, inventario, compras, recepcion, auditoria, dashboard y sync ingest |
| TABLET_PC_MANAGED | Tablet + PC con gobierno, snapshots, sync, conflictos y auditoria avanzada |

## 8. Contrato con no pagos bancarios

La licencia puede registrar que un cliente tiene un plan activo, pero PRISMA no debe procesar el cobro dentro de la app. Las altas, cobros, facturacion, transferencias, tarjetas o acuerdos comerciales quedan fuera del runtime local.

El producto puede mostrar:

```text
Solicitar activacion
Contactar soporte
Pedir informacion
```

No debe mostrar:

```text
Pagar ahora con tarjeta
Hacer transferencia desde PRISMA
Validar SPEI
Guardar tarjeta
```

## 9. Siguiente paso tecnico

Despues de esta entrega, la implementacion futura debe crear un lector local no invasivo que cargue un archivo `license.local.example.json` o `license.json` desde runtime config, determine feature availability y exponga helpers read-only para UI y servicios.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si la licencia local toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
