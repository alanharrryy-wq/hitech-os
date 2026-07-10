# 02. NDC ID Grammar and Naming

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Formato base

```text
<PREFIX>.<namespace>.<slug>[.<qualifier>...]
```

Ejemplos:

```text
TEN.prisma_rey
BIZ.prisma_rey.main
STO.prisma_rey.centro
DEV.tb.pos.01
ENT.sale
EVT.sale.created
ACT.sale.checkout
MET.sales.today
SURF.pc.sales_control
PNL.pc.sales.kpi_strip
WID.pc.sales.today_card
```

## Prefijos oficiales

| Prefijo | Nombre | Definición |
|---|---|---|
| `TEN` | Tenant | cliente lógico/comercial dueño del scope |
| `BIZ` | Business | negocio/empresa dentro del tenant |
| `STO` | Store/Site | sucursal, punto físico o sitio operativo |
| `TERM` | Terminal | terminal lógico o punto de caja |
| `DEV` | Device | dispositivo reclamado o fuente técnica |
| `USR` | User | usuario humano o cuenta operacional |
| `ROLE` | Role | rol operativo/comercial |
| `PLAN` | Plan | paquete contratado |
| `LIC` | License | derecho activo |
| `SLOT` | Device Slot | slot autorizado para device/surface |
| `MOD` | Module | módulo funcional o comercial |
| `CAP` | Capability | capacidad reusable/monetizable |
| `ENT` | Entity | entidad neutral de negocio |
| `EVT` | Event | evento ocurrido |
| `ACT` | Action | acción que intenta cambio |
| `STA` | State | estado neutral o técnico |
| `EVD` | Evidence | prueba o binding verificable |
| `MET` | Metric | métrica neutral |
| `ALT` | Alert | alerta operacional |
| `CAN` | Canonical Projection | vista consolidada |
| `SURF` | Surface | superficie/runtime/app |
| `ZONE` | Zone | zona UI |
| `PNL` | Panel | panel o contenedor UI |
| `WID` | Widget | widget/tarjeta/control |
| `BTN` | Button | botón accionable |
| `TBL` | Table | tabla/listado UI |
| `FRM` | Form | formulario |
| `CHT` | Chart | gráfica/chart |
| `DS` | Dataset | dataset o vista |
| `API` | API Endpoint | contrato API |
| `DBT` | DB Table | tabla implementación |
| `FLOW` | Flow | flujo operacional |
| `GATE` | Gate | validador |
| `DRF` | Drift Case | discrepancia/reconciliación |
| `CLAIM` | Claim | claim comercial sujeto a evidencia |

## Reglas

1. Un ID neutral no cambia por rename visual.
2. Un ID neutral no incluye runtime salvo que el runtime sea parte real del significado.
3. UI IDs localizan, no gobiernan.
4. Aliases se registran en curation.
5. Nuevos prefijos requieren definición, ejemplos, anti-patrones y schema.

## Alias example

```json
{"alias_id":"ALIAS.20260709.0001","observed_name":"PC-Dashboard-SalesCard","canonical_id":"MET.sales.today","mapping_type":"represents","confidence":"medium","reviewer":"human","reason":"UI name representa métrica, no manda."}
```

## Anti-patrones

| Malo | Bueno | Razón |
|---|---|---|
| `TB_POS_SALE` | `ENT.sale` | Venta no es de Tablet. |
| `PC-Dashboard-SalesCard` | `MET.sales.today` + `WID.pc.sales.today_card` | Métrica y widget separados. |
| `chart1` | `CHT.cl.sales.hourly_bar` | Necesita ubicación y significado. |
