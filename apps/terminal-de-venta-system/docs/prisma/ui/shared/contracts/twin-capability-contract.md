# PRISMA Twin Capability Contract
Este contrato convierte PC y Tablet en dos superficies de un mismo sistema operativo comercial. PC gobierna, tablet ejecuta, ambas conservan verdad auditable. Si esto no existe, cada pantalla se vuelve su propio changarro con letrero bonito.
## Entidades canónicas
| Entidad | Dueño | Productores | Consumidores | Regla |
|---|---|---|---|---|
| `catalog-master` | `pc` | `pc` | `tablet` | `PC mantiene catálogo canónico y tablet consume contexto limpio para venta/stock.` |
| `stock-signal` | `pc` | `pc, tablet` | `pc, tablet` | `Tablet puede consultar/levantar señales de stock sin apropiarse del ledger global.` |
| `inventory-count` | `pc` | `pc, tablet` | `pc, tablet` | `PC gobierna conteos y tablet prepara captura rápida sin romper saldos.` |
| `purchase-order` | `pc` | `pc` | `tablet` | `PC administra abasto; tablet solo observa compromisos relevantes para recepción.` |
| `receiving-flow` | `pc` | `pc, tablet` | `pc, tablet` | `Tablet puede apoyar recepción física mientras PC consolida costo, lote y stock.` |
| `replenishment-signal` | `pc` | `pc, tablet` | `pc, tablet` | `PC calcula reabasto y tablet reporta señales de agotado o urgencia.` |
| `sales-ticket` | `tablet` | `tablet` | `pc` | `Tablet vende y PC observa la transacción para control, auditoría y reportes.` |
| `checkout-payment` | `tablet` | `tablet` | `pc` | `Tablet ejecuta cobro y PC concentra consistencia de caja y conciliación.` |
| `shift-cash` | `tablet` | `tablet` | `pc` | `Tablet abre/cierra turno y PC audita diferencias, retiros y arqueos.` |
| `return-flow` | `tablet` | `tablet` | `pc` | `Tablet captura devolución; PC retiene auditoría y decisión de ajuste contable/stock.` |
| `sync-health` | `pc` | `pc, tablet` | `pc, tablet` | `Ambas superficies exponen estado de outbox, conflictos y último checkpoint.` |
| `audit-trail` | `pc` | `pc, tablet` | `pc, tablet` | `PC concentra auditoría y tablet produce eventos con actor, terminal, turno y origen.` |
| `dashboard-kpis` | `pc` | `pc, tablet` | `pc, tablet` | `PC muestra lectura gerencial y tablet muestra lectura operativa sin inventar métricas paralelas.` |
| `customer-context` | `pc` | `pc` | `tablet` | `Ambas apps leen cliente/cartera con escritura controlada hasta que exista módulo dedicado.` |

## Invariantes duras
1. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
2. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
3. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
4. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
5. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
6. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
7. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
8. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
9. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
10. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
11. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
12. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
13. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
14. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
15. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
16. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
17. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
18. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
19. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
20. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
21. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
22. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
23. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
24. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
25. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
26. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
27. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
28. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
29. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
30. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
31. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
32. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
33. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
34. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
35. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
36. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
37. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
38. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
39. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.
40. Ninguna capability puede existir solo en una app. Si PC sabe algo y tablet lo opera, la relación vive en `TWIN_CAPABILITY_MANIFEST`, no en la memoria del compa que hoy sí vino a trabajar.
   - Evidencia: binding PC + binding tablet + evento requerido cuando hay sync.
   - Riesgo si falla: divergencia silenciosa, datos fantasma y soporte técnico haciendo limpia con copal.

## Reglas por dominio
### Catálogo maestro (`catalog-master`)
- Dominio: `catalog`
- Parity key: `catalog.master`
- Sync: `pc_to_tablet`
- Resultado: PC mantiene catálogo canónico y tablet consume contexto limpio para venta/stock.
- Criterios:
  - Gate 1: validar que `catalog-master` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `catalog-master` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `catalog-master` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `catalog-master` resuelve binding local y evento compatible antes de exponer nueva UI.
### Señal de stock operativa (`stock-signal`)
- Dominio: `inventory`
- Parity key: `inventory.stock_signal`
- Sync: `bidirectional`
- Resultado: Tablet puede consultar/levantar señales de stock sin apropiarse del ledger global.
- Criterios:
  - Gate 1: validar que `stock-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `stock-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `stock-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `stock-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
### Conteos físicos (`inventory-count`)
- Dominio: `inventory`
- Parity key: `inventory.count`
- Sync: `bidirectional`
- Resultado: PC gobierna conteos y tablet prepara captura rápida sin romper saldos.
- Criterios:
  - Gate 1: validar que `inventory-count` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `inventory-count` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `inventory-count` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `inventory-count` resuelve binding local y evento compatible antes de exponer nueva UI.
### Órdenes de compra (`purchase-order`)
- Dominio: `procurement`
- Parity key: `procurement.purchase_order`
- Sync: `pc_to_tablet`
- Resultado: PC administra abasto; tablet solo observa compromisos relevantes para recepción.
- Criterios:
  - Gate 1: validar que `purchase-order` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `purchase-order` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `purchase-order` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `purchase-order` resuelve binding local y evento compatible antes de exponer nueva UI.
### Recepción de compras (`receiving-flow`)
- Dominio: `procurement`
- Parity key: `procurement.receiving`
- Sync: `bidirectional`
- Resultado: Tablet puede apoyar recepción física mientras PC consolida costo, lote y stock.
- Criterios:
  - Gate 1: validar que `receiving-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `receiving-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `receiving-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `receiving-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
### Reabasto inteligente (`replenishment-signal`)
- Dominio: `procurement`
- Parity key: `procurement.replenishment`
- Sync: `bidirectional`
- Resultado: PC calcula reabasto y tablet reporta señales de agotado o urgencia.
- Criterios:
  - Gate 1: validar que `replenishment-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `replenishment-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `replenishment-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `replenishment-signal` resuelve binding local y evento compatible antes de exponer nueva UI.
### Ticket de venta (`sales-ticket`)
- Dominio: `sales`
- Parity key: `sales.ticket`
- Sync: `tablet_to_pc`
- Resultado: Tablet vende y PC observa la transacción para control, auditoría y reportes.
- Criterios:
  - Gate 1: validar que `sales-ticket` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `sales-ticket` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `sales-ticket` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `sales-ticket` resuelve binding local y evento compatible antes de exponer nueva UI.
### Cobro y medios de pago (`checkout-payment`)
- Dominio: `sales`
- Parity key: `sales.checkout_payment`
- Sync: `tablet_to_pc`
- Resultado: Tablet ejecuta cobro y PC concentra consistencia de caja y conciliación.
- Criterios:
  - Gate 1: validar que `checkout-payment` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `checkout-payment` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `checkout-payment` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `checkout-payment` resuelve binding local y evento compatible antes de exponer nueva UI.
### Turno y caja (`shift-cash`)
- Dominio: `cash`
- Parity key: `cash.shift`
- Sync: `tablet_to_pc`
- Resultado: Tablet abre/cierra turno y PC audita diferencias, retiros y arqueos.
- Criterios:
  - Gate 1: validar que `shift-cash` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `shift-cash` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `shift-cash` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `shift-cash` resuelve binding local y evento compatible antes de exponer nueva UI.
### Devoluciones (`return-flow`)
- Dominio: `returns`
- Parity key: `returns.transaction`
- Sync: `tablet_to_pc`
- Resultado: Tablet captura devolución; PC retiene auditoría y decisión de ajuste contable/stock.
- Criterios:
  - Gate 1: validar que `return-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `return-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `return-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `return-flow` resuelve binding local y evento compatible antes de exponer nueva UI.
### Salud de sincronización (`sync-health`)
- Dominio: `sync`
- Parity key: `sync.health`
- Sync: `bidirectional`
- Resultado: Ambas superficies exponen estado de outbox, conflictos y último checkpoint.
- Criterios:
  - Gate 1: validar que `sync-health` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `sync-health` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `sync-health` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `sync-health` resuelve binding local y evento compatible antes de exponer nueva UI.
### Trazabilidad operativa (`audit-trail`)
- Dominio: `audit`
- Parity key: `audit.trail`
- Sync: `tablet_to_pc`
- Resultado: PC concentra auditoría y tablet produce eventos con actor, terminal, turno y origen.
- Criterios:
  - Gate 1: validar que `audit-trail` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `audit-trail` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `audit-trail` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `audit-trail` resuelve binding local y evento compatible antes de exponer nueva UI.
### KPIs gemelos (`dashboard-kpis`)
- Dominio: `reporting`
- Parity key: `reporting.kpi`
- Sync: `bidirectional`
- Resultado: PC muestra lectura gerencial y tablet muestra lectura operativa sin inventar métricas paralelas.
- Criterios:
  - Gate 1: validar que `dashboard-kpis` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `dashboard-kpis` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `dashboard-kpis` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `dashboard-kpis` resuelve binding local y evento compatible antes de exponer nueva UI.
### Contexto de cliente (`customer-context`)
- Dominio: `customer`
- Parity key: `customer.context`
- Sync: `pc_to_tablet`
- Resultado: Ambas apps leen cliente/cartera con escritura controlada hasta que exista módulo dedicado.
- Criterios:
  - Gate 1: validar que `customer-context` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 2: validar que `customer-context` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 3: validar que `customer-context` resuelve binding local y evento compatible antes de exponer nueva UI.
  - Gate 4: validar que `customer-context` resuelve binding local y evento compatible antes de exponer nueva UI.
