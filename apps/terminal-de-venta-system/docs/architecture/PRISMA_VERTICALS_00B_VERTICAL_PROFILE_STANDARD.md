# PRISMA Verticales 00B - Estandar de perfil vertical

Un perfil vertical es el contrato minimo para activar un giro de negocio sin contaminar el nucleo comun.

## Campos obligatorios

- id estable.
- displayName visible en es-MX.
- market comercial.
- status de activacion.
- capabilities activas.
- tabletNavigation.
- pcNavigation.
- tabletBlockedCapabilities.
- events.
- permissions.
- offlinePolicy.
- kpis.
- acceptanceCriteria.

## Reglas

1. Si afecta dinero, debe tener evento y permiso.
2. Si afecta inventario, debe dejar movimiento o rastro.
3. Si afecta cliente, debe dejar actor, fecha y entidad.
4. Si exige gobierno profundo, vive en PC.
5. Si es operacion rapida, puede vivir en Tablet.
6. Si no puede explicarse a un cajero en una frase, no es accion principal de Tablet.
