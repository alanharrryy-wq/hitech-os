# Relationship Edges

| fromEntity | fromField | toEntity | toField | relationshipType | required | confidence | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AuditCount | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditCount | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| AuditEvent | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditEvent | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| AuditEvent | actorId | actor | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditEvent | entityId | entity | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Barcode | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Barcode | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Barcode | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Brand | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Brand | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Business | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Business | taxId | tax | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashAdjustment | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashAdjustment | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashAdjustment | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| CashAdjustment | cashMovementId | CashMovement | id | DERIVED | false | MEDIUM | PASS |
| CashAdjustment | actorId | actor | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashMovement | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashMovement | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashMovement | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| CashSession | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashSession | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashSession | storeId | Store | id | DERIVED | true | MEDIUM | PASS |
| CashSession | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| CashSession | cashierId | cashier | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DataSourceFreshness | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DataSourceFreshness | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DataSourceFreshness | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| DeviceHeartbeat | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DeviceHeartbeat | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DeviceHeartbeat | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| DropdownCatalog | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DropdownCatalog | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DropdownOption | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DropdownOption | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DropdownOption | catalogId | catalog | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceipt | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceipt | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| GoodsReceipt | purchaseOrderId | PurchaseOrder | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceipt | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceiptLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| GoodsReceiptLine | goodsReceiptId | GoodsReceipt | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | purchaseOrderLineId | PurchaseOrderLine | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| OutboxEvent | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| OutboxEvent | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| OutboxEvent | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| OutboxEvent | aggregateId | aggregate | id | DERIVED | false | LOW | NO_ENCONTRADO |
| OutboxEvent | correlationId | correlation | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Permission | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Permission | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceList | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PriceList | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceListItem | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PriceListItem | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceListItem | priceListId | PriceList | id | DERIVED | false | MEDIUM | PASS |
| PriceListItem | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Product | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Product | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Product | brandId | Brand | id | DERIVED | false | MEDIUM | PASS |
| Product | taxRateId | TaxRate | id | DERIVED | false | MEDIUM | PASS |
| ProductSupplier | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| ProductSupplier | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| ProductSupplier | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| ProductSupplier | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrder | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PurchaseOrder | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PurchaseOrder | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrderLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PurchaseOrderLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PurchaseOrderLine | purchaseOrderId | PurchaseOrder | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrderLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| ReplenishmentSignal | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| ReplenishmentSignal | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| ReplenishmentSignal | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Role | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Role | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Sale | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Sale | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Sale | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| Sale | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| SaleLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleLine | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| SalePaymentTender | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SalePaymentTender | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SalePaymentTender | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleReturn | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleReturn | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleReturnLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | saleReturnId | SaleReturn | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | saleLineId | SaleLine | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | stockMovementId | StockMovement | id | DERIVED | false | MEDIUM | PASS |
| StockMovement | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| StockMovement | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| StockMovement | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| StockSnapshot | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| StockSnapshot | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| StockSnapshot | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Store | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Store | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Supplier | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Supplier | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SupportIncident | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SupportIncident | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SupportIncident | openedById | openedBy | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SupportIncident | assignedToId | assignedTo | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncAttempt | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncAttempt | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SyncAttempt | eventId | event | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncAttempt | outboxEventId | OutboxEvent | id | DERIVED | false | MEDIUM | PASS |
| SyncAttempt | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| SyncAttempt | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| SyncCheckpoint | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncCheckpoint | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SyncCheckpoint | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| SyncCheckpoint | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| SyncCheckpoint | lastEventId | lastEvent | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncCheckpoint | lastAttemptId | lastAttempt | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncConflict | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncConflict | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SyncConflict | eventId | event | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncConflict | outboxEventId | OutboxEvent | id | DERIVED | false | MEDIUM | PASS |
| SyncConflict | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| SyncConflict | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| SyncConflict | aggregateId | aggregate | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncOutboxStatusBucket | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncOutboxStatusBucket | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SyncOutboxStatusBucket | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| SyncOutboxStatusBucket | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| TaxRate | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| TaxRate | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Terminal | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Terminal | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Terminal | storeId | Store | id | DERIVED | true | MEDIUM | PASS |
| User | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| User | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| AuditCount | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditCount | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| AuditEvent | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditEvent | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| AuditEvent | actorId | actor | id | DERIVED | false | LOW | NO_ENCONTRADO |
| AuditEvent | entityId | entity | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Barcode | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Barcode | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Barcode | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Brand | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Brand | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Business | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Business | taxId | tax | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashAdjustment | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashAdjustment | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashAdjustment | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| CashAdjustment | cashMovementId | CashMovement | id | DERIVED | false | MEDIUM | PASS |
| CashAdjustment | actorId | actor | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashMovement | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashMovement | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashMovement | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| CashSession | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| CashSession | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| CashSession | storeId | Store | id | DERIVED | true | MEDIUM | PASS |
| CashSession | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| CashSession | cashierId | cashier | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DropdownCatalog | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DropdownCatalog | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DropdownOption | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| DropdownOption | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| DropdownOption | catalogId | catalog | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceipt | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceipt | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| GoodsReceipt | purchaseOrderId | PurchaseOrder | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceipt | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| GoodsReceiptLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| GoodsReceiptLine | goodsReceiptId | GoodsReceipt | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | purchaseOrderLineId | PurchaseOrderLine | id | DERIVED | false | MEDIUM | PASS |
| GoodsReceiptLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| OutboxEvent | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| OutboxEvent | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| OutboxEvent | aggregateId | aggregate | id | DERIVED | false | LOW | NO_ENCONTRADO |
| OutboxEvent | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| OutboxEvent | remoteEventId | remoteEvent | id | DERIVED | false | LOW | NO_ENCONTRADO |
| OutboxEvent | remoteLedgerId | remoteLedger | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Permission | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Permission | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceList | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PriceList | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceListItem | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PriceListItem | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PriceListItem | priceListId | PriceList | id | DERIVED | false | MEDIUM | PASS |
| PriceListItem | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Product | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Product | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Product | brandId | Brand | id | DERIVED | false | MEDIUM | PASS |
| Product | taxRateId | TaxRate | id | DERIVED | false | MEDIUM | PASS |
| ProductSupplier | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| ProductSupplier | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| ProductSupplier | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| ProductSupplier | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrder | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PurchaseOrder | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PurchaseOrder | supplierId | Supplier | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrderLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| PurchaseOrderLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| PurchaseOrderLine | purchaseOrderId | PurchaseOrder | id | DERIVED | false | MEDIUM | PASS |
| PurchaseOrderLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| ReplenishmentSignal | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| ReplenishmentSignal | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| ReplenishmentSignal | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Role | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Role | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Sale | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Sale | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Sale | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| Sale | cashSessionId | CashSession | id | DERIVED | false | MEDIUM | PASS |
| Sale | clientRequestId | clientRequest | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleLine | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| SalePaymentTender | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SalePaymentTender | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SalePaymentTender | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleReturn | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleReturn | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SaleReturnLine | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | saleReturnId | SaleReturn | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | saleId | Sale | id | DERIVED | true | MEDIUM | PASS |
| SaleReturnLine | saleLineId | SaleLine | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| SaleReturnLine | stockMovementId | StockMovement | id | DERIVED | false | MEDIUM | PASS |
| StockMovement | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| StockMovement | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| StockMovement | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| StockMovement | sourceId | source | id | DERIVED | false | LOW | NO_ENCONTRADO |
| StockSnapshot | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| StockSnapshot | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| StockSnapshot | productId | Product | id | DERIVED | false | MEDIUM | PASS |
| Store | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Store | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Supplier | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Supplier | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SupportIncident | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SupportIncident | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SupportIncident | openedById | openedBy | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SupportIncident | assignedToId | assignedTo | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncCheckpoint | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncCheckpoint | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| SyncCheckpoint | deviceId | device | id | DERIVED | true | LOW | NO_ENCONTRADO |
| SyncCheckpoint | terminalId | Terminal | id | DERIVED | true | MEDIUM | PASS |
| SyncCheckpoint | lastEventId | lastEvent | id | DERIVED | false | LOW | NO_ENCONTRADO |
| SyncCheckpoint | lastAttemptId | lastAttempt | id | DERIVED | false | LOW | NO_ENCONTRADO |
| TabletLocalSecuritySecret | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| TaxRate | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| TaxRate | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Terminal | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| Terminal | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| Terminal | storeId | Store | id | DERIVED | true | MEDIUM | PASS |
| User | id |  | id | DERIVED | false | LOW | NO_ENCONTRADO |
| User | businessId | Business | id | DERIVED | true | MEDIUM | PASS |
| setup bundle | license_id | license | license_id | SERVICE_QUERY | true | HIGH | PASS |
| claim slot | license_id | license | license_id | SERVICE_QUERY | true | HIGH | PASS |
| claim slot | plan_id | license plan | plan_id | SERVICE_QUERY | true | HIGH | PASS |
| sale | id | outbox event | aggregateId | PAYLOAD_JSON | true | MEDIUM | PARCIAL |
| tablet sale | id | canonical sale | idempotencyKey/clientRequestId | DOC_CONTRACT | true | MEDIUM | PARCIAL |
