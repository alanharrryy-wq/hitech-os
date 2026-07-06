# Field Alias Contract

| Alias | Meaning | Status | Evidence |
| --- | --- | --- | --- |
| `SaleLine.qty` | quantity when present | PARCIAL | table_columns/payload_json_index |
| `SaleLine.quantity` | quantity canonical alias | PASS | table_columns/payload_json_index |
| `SalePaymentTender.tenderType` | tender kind | PASS | SalePaymentTender contract |
| `Terminal.storeId` | derived store | PASS | relationship_edges |
| `CashSession.userId` | cashier/operator | PASS | relationship_edges |
| `OutboxEvent.aggregateId` | sale/entity id candidate | PASS | outbox linking rules |
| `OutboxEvent.payloadJson.*` | operational payload ids | PASS | payload_json_index |
