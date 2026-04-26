# App PC - Centro de mando

**Version:** 3.0.0  
**Perspectiva:** PC  
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

### Invariantes de App PC - Centro de mando

- Ningun plugin escribe directamente sobre entidades canonicas sin pasar por contrato.
- Ninguna pantalla base se vuelve exclusiva de una vertical.
- Ningun flujo operativo queda mudo ante error, conflicto u offline.
- Toda accion sensible debe tener evento, permiso y rastro de auditoria.
- Todo cambio debe declarar reflejo PC <-> Tablet.



```mermaid
flowchart LR
    A[Configurar App PC - Centro de mando en PC] --> B[Publicar contrato]
    B --> C[Tablet recibe politica]
    C --> D[Ejecuta flujo permitido]
    D --> E[Genera evento]
    E --> F[Sync valida]
    F --> G[PC audita y reporta]
    F --> H{Conflicto?}
    H -- Si --> I[Resolver en PC]
    H -- No --> G
```


## Personalidad de PC

PC no es caja rapida. PC es centro de mando: configura, gobierna, audita, reporta y resuelve. Puede operar algunas cosas, pero su chamba fuerte es control.

## Pantallas

- [PC-01 Dashboard ejecutivo](screens/PC-01_dashboard-ejecutivo.md)
- [PC-02 Catalogo maestro](screens/PC-02_catalogo-maestro.md)
- [PC-03 Clientes y cartera](screens/PC-03_clientes-y-cartera.md)
- [PC-04 Inventario global](screens/PC-04_inventario-global.md)
- [PC-05 Pedidos y ordenes](screens/PC-05_pedidos-y-ordenes.md)
- [PC-06 Caja y finanzas operativas](screens/PC-06_caja-y-finanzas-operativas.md)
- [PC-07 Sync y eventos](screens/PC-07_sync-y-eventos.md)
- [PC-08 Usuarios roles permisos](screens/PC-08_usuarios-roles-permisos.md)
- [PC-09 Configuracion del sistema](screens/PC-09_configuracion-del-sistema.md)
- [PC-10 Plugin Studio y Target Atlas](screens/PC-10_plugin-studio-y-target-atlas.md)
