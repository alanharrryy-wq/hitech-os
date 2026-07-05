# PRISMA License Admin Portal Contract 05

## 1. Propósito

Definir el panel mínimo para operar clientes y licencias sin editar JSON a mano como si estuviéramos vendiendo software en una servilleta.

## 2. Módulos mínimos

```text
Clientes
Negocios
Planes
Licencias
Dispositivos
Renovaciones
Suspensiones / Revocaciones
Auditoría
Soporte / Diagnóstico
```

## 3. Pantallas mínimas

### Clientes

- crear cliente;
- editar datos básicos;
- ver estado de facturación;
- ver negocios asociados.

### Negocios

- crear negocio/sucursal;
- asignar plan;
- ver terminales activas;
- ver límites.

### Licencias

- emitir licencia;
- renovar;
- suspender;
- revocar;
- upgrade/downgrade;
- descargar licencia firmada;
- ver último refresh.

### Dispositivos

- ver `deviceId`;
- ver `terminalId`;
- ver último contacto;
- suspender device;
- reset controlado.

### Auditoría

- filtros por cliente, actor, evento, fecha;
- detalle de before/after;
- export de evidencia.

## 4. Acciones críticas y confirmación

Estas acciones requieren confirmación explícita:

```text
license.revoke
license.suspend

## Prisma Cloud Center Customer Setup Addendum

The admin portal surface for this flow is the existing Prisma Cloud Center, not a new Control Center.

Operator creates or represents a Prisma Customer Setup package with:

- Setup Link
- Setup Code
- Setup QR
- Tablet POS Slot
- PC Admin Slot
- Mobile Companion Slot

License Admin Bridge remains separate. Customer onboarding must not be modeled as activate/refresh/revoke.
device.reset
plan.downgrade
terminal.limit.reduce
```

## 5. MVP interno aceptable

No necesita ser SaaS bonito en la primera vuelta. Debe ser seguro, auditable, claro, con formularios mínimos, sin edición manual de archivos productivos y con logs de acciones.

## 6. Criterio de salida

El portal MVP sirve si soporte puede:

1. crear cliente;
2. asignar plan;
3. activar device;
4. emitir licencia;
5. suspender/revocar;
6. ver diagnóstico;
7. descargar licencia firmada.
