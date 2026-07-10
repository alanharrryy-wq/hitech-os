# 03. NDC Scope Model

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Jerarquía

```text
TENANT → BUSINESS → STORE/SITE → TERMINAL → DEVICE → SESSION
                         ↘ LICENSE → SLOT → SURFACE GRANT
                         ↘ USER → ROLE → MODULE GRANT
```

## Objetos de scope

| ID | Objeto | Ejemplo | Uso |
|---|---|---|---|
| `TEN` | Tenant | `TEN.prisma_rey` | aislamiento y cliente lógico. |
| `BIZ` | Business | `BIZ.prisma_rey.main` | unidad de negocio. |
| `STO` | Store/Site | `STO.prisma_rey.centro` | sucursal/sitio. |
| `TERM` | Terminal | `TERM.pos.01` | punto operativo. |
| `DEV` | Device | `DEV.tb.pos.01` | device emisor/consumidor. |
| `USR` | User | `USR.cashier.01` | actor humano. |
| `ROLE` | Role | `ROLE.cashier` | autorización. |
| `PLAN` | Plan | `PLAN.abarrotes.pro` | paquete contratado. |
| `LIC` | License | `LIC.prisma_rey.main` | derecho activo. |
| `SLOT` | Slot | `SLOT.tb.pos.01` | device/surface grant. |

## Reglas

- Todo dato operativo tiene tenant.
- Ventas/caja/inventario tienen store o excepción explícita.
- Eventos de app/device tienen source_device y source_surface si hay evidencia runtime.
- Cliente-facing requiere license_ref/surface_grant.
- Premium requiere module_grant/pricing_class.

## Matrices derivadas

`Scope_Registry`, `Tenant_Master`, `Business_Site_Map`, `Device_License_Map`, `Role_Module_Map`, `Session_Context_Map`.
