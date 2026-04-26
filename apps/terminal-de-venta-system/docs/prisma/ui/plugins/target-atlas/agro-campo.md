# Agro, veterinaria y campo

**Version:** 3.0.0  
**Perspectiva:** familia agro-campo  
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

### Invariantes de Agro, veterinaria y campo

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar Agro, veterinaria y campo en PC] --> B[Publicar contrato]
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
| agroinsumos | Operacion de agroinsumos con reglas particulares, excepciones humanas y necesidad de trazabilidad. | inventory | agroinsumos_extension |
| alimento animal | Operacion de alimento animal con reglas particulares, excepciones humanas y necesidad de trazabilidad. | payments | alimento-animal_extension |
| semillas | Operacion de semillas con reglas particulares, excepciones humanas y necesidad de trazabilidad. | core | semillas_extension |
| fertilizantes | Operacion de fertilizantes con reglas particulares, excepciones humanas y necesidad de trazabilidad. | inventory | fertilizantes_extension |
| tienda agricola | Operacion de tienda agricola con reglas particulares, excepciones humanas y necesidad de trazabilidad. | fiscal | tienda-agricola_extension |
| servicios de campo | Operacion de servicios de campo con reglas particulares, excepciones humanas y necesidad de trazabilidad. | core | servicios-de-campo_extension |

## Modulos normalmente involucrados

| Modulo | Uso |
| inventory | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| core | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| sync | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| payments | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| orders | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| fiscal | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| reports | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |
| cash | Soporta el patron Agro, veterinaria y campo y debe conservar contrato compartido. |

## Plugins candidatos

| Plugin | Tipo | Notas |
| agroinsumos_plugin | vertical | agroinsumos_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| alimento-animal_plugin | vertical | alimento-animal_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| semillas_plugin | vertical | semillas_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| fertilizantes_plugin | vertical | fertilizantes_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| tienda-agricola_plugin | vertical | tienda-agricola_plugin debe declarar permisos, eventos, offline, sync y rollback. |
| agro-campo_core_pack | vertical | agro-campo_core_pack debe declarar permisos, eventos, offline, sync y rollback. |
| agro-campo_report_pack | vertical | agro-campo_report_pack debe declarar permisos, eventos, offline, sync y rollback. |

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
