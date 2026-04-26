# Servicios con agenda

**Version:** 3.0.0  
**Perspectiva:** familia servicios-agenda  
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

### Invariantes de Servicios con agenda

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar Servicios con agenda en PC] --> B[Publicar contrato]
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
| barberia | Operacion de barberia con reglas particulares, excepciones humanas y necesidad de trazabilidad. | procurement | barberia_extension |
| salon belleza | Operacion de salon belleza con reglas particulares, excepciones humanas y necesidad de trazabilidad. | inventory | salon-belleza_extension |
| spa | Operacion de spa con reglas particulares, excepciones humanas y necesidad de trazabilidad. | core | spa_extension |
| clinica estetica | Operacion de clinica estetica con reglas particulares, excepciones humanas y necesidad de trazabilidad. | orders | clinica-estetica_extension |
| servicio tecnico | Operacion de servicio tecnico con reglas particulares, excepciones humanas y necesidad de trazabilidad. | customers | servicio-tecnico_extension |
| estudio fotografico | Operacion de estudio fotografico con reglas particulares, excepciones humanas y necesidad de trazabilidad. | payments | estudio-fotografico_extension |

## Modulos normalmente involucrados

| Modulo | Uso |
| procurement | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| customers | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| hardware | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| payments | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| orders | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| inventory | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| core | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |
| catalog | Soporta el patron Servicios con agenda y debe conservar contrato compartido. |

## Plugins candidatos

| Plugin | Tipo | Notas |
| barberia_plugin | vertical | barberia_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| salon-belleza_plugin | vertical | salon-belleza_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| spa_plugin | vertical | spa_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| clinica-estetica_plugin | vertical | clinica-estetica_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| servicio-tecnico_plugin | vertical | servicio-tecnico_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| servicios-agenda_core_pack | vertical | servicios-agenda_core_pack debe declarar permisos, eventos, offline, sync y rollback. |
| servicios-agenda_report_pack | vertical | servicios-agenda_report_pack debe declarar permisos, eventos, offline, sync y rollback. |

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
