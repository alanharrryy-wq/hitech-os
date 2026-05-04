# PRISMA 00D - Politica de sync y auditoria por vertical

La sincronizacion no es un boton magico. Es un contrato operativo para que lo local y lo central no se agarren a sillazos.

## Estados humanos permitidos

- Pendiente por enviar
- Enviado
- Fallo el envio
- Se intentara de nuevo
- Requiere revision
- Conflicto detectado

## Estados tecnicos internos

Estos pueden existir en codigo, pero no deben aparecer al cajero: pending, sent, failed, acked, conflict, retry, payload, resolver.

## Tienda de conveniencia
- ID: `convenience`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Restaurante o cafeteria
- ID: `restaurant`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Farmacia
- ID: `pharmacy`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Estetica, barberia o salon
- ID: `beauty`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Ferreteria
- ID: `hardware`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Ropa o boutique
- ID: `apparel`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Taller o reparaciones
- ID: `repair`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Venta en campo o ruta
- ID: `field_route`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Abarrotes con bascula
- ID: `grocery_scale`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.

## Food truck o punto movil
- ID: `food_truck`
- Venta local: permitida si el perfil vertical lo declara.
- Auditoria minima: actor, accion, entidad, antes, despues, terminal, negocio, fecha.
- Conflictos: precio local viejo, stock negativo, permiso insuficiente, entidad descontinuada o duplicado.
- Regla: si el conflicto afecta dinero o inventario, PC resuelve o marca revision.
