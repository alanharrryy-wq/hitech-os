# Distribucion, rutas y preventa

**Version:** 3.0.0  
**Perspectiva:** familia distribucion-rutas  
**Estado:** documento modular vivo  
**Regla madre:** crecer sin romper el core, sin secuestrar pantallas y sin meter logica de giro a martillazos.

## Proposito

Este documento define como PRISMA debe comportarse, extenderse y verificarse en la capa de interfaz y operacion. No es un adorno para sentirse profesional. Es una pieza de gobierno para que el sistema no termine convertido en una combi con aleron de Formula 1: vistosa, ruidosa y peligrosamente improvisada.

## Principios

1. **Core primero:** las verticales extienden, no reemplazan.
2. **PC gobierna:** configura, audita, reporta y resuelve.
3. **Tablet ejecuta:** opera rapido, claro, tactil y con tolerancia a fallas.
4. **Eventos siempre:** dinero, stock, cliente, caja, pedido, membresia, fiscal o produccion generan evento.
5. **Offline con reglas:** no todo se permite sin internet; lo permitido queda marcado, encolado y auditable.
6. **Plugin bajo contrato:** ningun plugin entra como primo incomodo a mover muebles sin avisar.
7. **Documento vivo:** todo cambio debe dejar rastro y compatibilidad.


## Contrato obligatorio de pantalla

| Campo | Requisito | Razon operacional |
|---|---|---|
| ID canonico | Obligatorio | Evita duplicados, alias raros y tragedias de versionado. |
| Intencion | Obligatorio | Define para que existe antes de decorarla con botones. |
| Owner | Obligatorio | Una cosa sin dueno termina siendo del diablo y del becario. |
| Modulos base | Obligatorio | Declara dependencias reales. |
| Slots de plugin | Obligatorio | Permite extensiones sin romper el corazon. |
| Permisos | Obligatorio | Si afecta dinero, inventario, cliente o caja, requiere permiso. |
| Eventos | Obligatorio | Lo que no genera evento casi no existio. |
| Offline | Obligatorio | Define que vive sin internet y que se bloquea. |
| Sync | Obligatorio | Declara cola, conflicto y reconciliacion. |
| Auditoria | Obligatorio | Debe decir quien hizo que, cuando, donde y desde que dispositivo. |
| Rollback | Obligatorio en cambios | Para no rezarle al santo patron de los deploys. |

### Invariantes de Distribucion, rutas y preventa

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar Distribucion, rutas y preventa en PC] --> B[Publicar contrato]
    B --> C[Tablet recibe politica]
    C --> D[Ejecuta flujo permitido]
    D --> E[Genera evento]
    E --> F[Sync valida]
    F --> G[PC audita y reporta]
    F --> H{Conflicto?}
    H -- Si --> I[Resolver en PC]
    H -- No --> G
```


## Targets incluidos

| Target | Dolor operativo | Modulo dominante | Plugin sugerido |
| reparto | Operacion de reparto con reglas particulares, excepciones humanas y necesidad de trazabilidad. | fiscal | reparto_extension |
| garrafones | Operacion de garrafones con reglas particulares, excepciones humanas y necesidad de trazabilidad. | core | garrafones_extension |
| preventa | Operacion de preventa con reglas particulares, excepciones humanas y necesidad de trazabilidad. | cash | preventa_extension |
| mayorista local | Operacion de mayorista local con reglas particulares, excepciones humanas y necesidad de trazabilidad. | fiscal | mayorista-local_extension |
| cobranza de campo | Operacion de cobranza de campo con reglas particulares, excepciones humanas y necesidad de trazabilidad. | catalog | cobranza-de-campo_extension |
| proveedor regional | Operacion de proveedor regional con reglas particulares, excepciones humanas y necesidad de trazabilidad. | payments | proveedor-regional_extension |

## Modulos normalmente involucrados

| Modulo | Uso |
| sync | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| cash | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| payments | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| customers | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| fiscal | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| core | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| catalog | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |
| inventory | Soporta el patron Distribucion, rutas y preventa y debe conservar contrato compartido. |

## Plugins candidatos

| Plugin | Tipo | Notas |
| reparto_plugin | vertical | reparto_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| garrafones_plugin | vertical | garrafones_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| preventa_plugin | vertical | preventa_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| mayorista-local_plugin | vertical | mayorista-local_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| cobranza-de-campo_plugin | vertical | cobranza-de-campo_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| distribucion-rutas_core_pack | vertical | distribucion-rutas_core_pack debe declarar permisos, eventos, offline, sync y rollback. |
| distribucion-rutas_report_pack | vertical | distribucion-rutas_report_pack debe declarar permisos, eventos, offline, sync y rollback. |

## Flujo comercial base

1. Identificar cliente o consumidor.
2. Seleccionar producto, servicio, pedido, membresia, ruta o activo.
3. Validar reglas de precio, stock, agenda, cartera o disponibilidad.
4. Ejecutar cobro, apartado, orden, entrega o avance.
5. Generar evento.
6. Encolar sync si hace falta.
7. Auditar en PC.

## Riesgos tipicos

- Querer crear pantalla nueva en lugar de plugin.
- Mezclar reglas fiscales con reglas operativas.
- Permitir offline sin cache valida.
- Duplicar cliente, producto o pedido por vertical.

## Demo vendible

La demo debe mostrar un caso cotidiano, un problema real y una solucion visible. Nada de explicar arquitectura como si el cliente hubiera pedido clase de ingeniería. Se muestra dolor, control y resultado.
