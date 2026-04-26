# Salud administrativa no clinica

**Version:** 3.0.0  
**Perspectiva:** familia salud-admin  
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

### Invariantes de Salud administrativa no clinica

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar Salud administrativa no clinica en PC] --> B[Publicar contrato]
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
| optica | Operacion de optica con reglas particulares, excepciones humanas y necesidad de trazabilidad. | hardware | optica_extension |
| dental administrativo | Operacion de dental administrativo con reglas particulares, excepciones humanas y necesidad de trazabilidad. | reports | dental-administrativo_extension |
| laboratorio administrativo | Operacion de laboratorio administrativo con reglas particulares, excepciones humanas y necesidad de trazabilidad. | orders | laboratorio-administrativo_extension |
| veterinaria | Operacion de veterinaria con reglas particulares, excepciones humanas y necesidad de trazabilidad. | orders | veterinaria_extension |
| paquetes esteticos | Operacion de paquetes esteticos con reglas particulares, excepciones humanas y necesidad de trazabilidad. | reports | paquetes-esteticos_extension |

## Modulos normalmente involucrados

| Modulo | Uso |
| payments | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| reports | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| fiscal | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| orders | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| customers | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| procurement | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| inventory | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |
| hardware | Soporta el patron Salud administrativa no clinica y debe conservar contrato compartido. |

## Plugins candidatos

| Plugin | Tipo | Notas |
| optica_plugin | vertical | optica_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| dental-administrativo_plugin | vertical | dental-administrativo_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| laboratorio-administrativo_plugin | vertical | laboratorio-administrativo_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| veterinaria_plugin | vertical | veterinaria_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| paquetes-esteticos_plugin | vertical | paquetes-esteticos_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| salud-admin_core_pack | vertical | salud-admin_core_pack debe declarar permisos, eventos, offline, sync y rollback. |
| salud-admin_report_pack | vertical | salud-admin_report_pack debe declarar permisos, eventos, offline, sync y rollback. |

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
