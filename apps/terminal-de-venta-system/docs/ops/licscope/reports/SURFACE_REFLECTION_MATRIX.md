# Surface Reflection Matrix

| Dato dummy | DB/modelo | Tablet | PC/Admin | Mobile | Estado | Evidencia |
| --- | --- | --- | --- | --- | --- | --- |
| Venta hoy / actividad reciente | Sale/SaleLine/SalePaymentTender | loader/contrato POS | loader/API sales-control | snapshot/API | PASS | verify:data-surfaces |
| Stock critico | StockSnapshot/Product | loader inventario | canonical/API | snapshot/API | PASS | verify:data-surfaces |
| Alerta operativa | Data readiness/outbox/sync | contrato operativo | admin/readiness | mobile snapshot | PASS | verify:data-surfaces |
