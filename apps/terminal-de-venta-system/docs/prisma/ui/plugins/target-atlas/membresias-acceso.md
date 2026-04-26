# Membresias, acceso y recurrencia

**Version:** 3.0.0  
**Perspectiva:** familia membresias-acceso  
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

### Invariantes de Membresias, acceso y recurrencia

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar Membresias, acceso y recurrencia en PC] --> B[Publicar contrato]
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
| gym | Operacion de gym con reglas particulares, excepciones humanas y necesidad de trazabilidad. | hardware | gym_extension |
| estudio fitness | Operacion de estudio fitness con reglas particulares, excepciones humanas y necesidad de trazabilidad. | inventory | estudio-fitness_extension |
| club | Operacion de club con reglas particulares, excepciones humanas y necesidad de trazabilidad. | customers | club_extension |
| coworking | Operacion de coworking con reglas particulares, excepciones humanas y necesidad de trazabilidad. | cash | coworking_extension |
| academia deportiva | Operacion de academia deportiva con reglas particulares, excepciones humanas y necesidad de trazabilidad. | hardware | academia-deportiva_extension |
| yoga | Operacion de yoga con reglas particulares, excepciones humanas y necesidad de trazabilidad. | cash | yoga_extension |
| suscripcion local | Operacion de suscripcion local con reglas particulares, excepciones humanas y necesidad de trazabilidad. | payments | suscripcion-local_extension |

## Modulos normalmente involucrados

| Modulo | Uso |
| procurement | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| customers | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| cash | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| hardware | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| inventory | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| sales | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| sync | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |
| payments | Soporta el patron Membresias, acceso y recurrencia y debe conservar contrato compartido. |

## Plugins candidatos

| Plugin | Tipo | Notas |
| gym_plugin | vertical | gym_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| estudio-fitness_plugin | vertical | estudio-fitness_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| club_plugin | vertical | club_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| coworking_plugin | vertical | coworking_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| academia-deportiva_plugin | vertical | academia-deportiva_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| membresias-acceso_core_pack | vertical | membresias-acceso_core_pack debe declarar permisos, eventos, offline, sync y rollback. |
| membresias-acceso_report_pack | vertical | membresias-acceso_report_pack debe declarar permisos, eventos, offline, sync y rollback. |

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
