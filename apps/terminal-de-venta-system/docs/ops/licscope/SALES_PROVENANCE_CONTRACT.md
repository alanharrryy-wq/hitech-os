# Sales Provenance Contract

Status: PASS

- Tablet POS can originate sales only after license/device/scope gate passes.
- Sale.businessId is required for business provenance.
- Sale.terminalId derives store through Terminal.storeId when direct storeId is absent.
- CashSession.userId or cashier field identifies the operator when available.
- SaleLine.saleId ties lines to sale.
- SalePaymentTender.saleId ties tenders to sale.
- OutboxEvent.aggregateId, idempotencyKey, clientRequestId and payloadJson sale identifiers are the official sale-to-outbox link candidates.
- Canonical projection in PC is linked by shared sale id, idempotency key, client request id, source event id or payload JSON identifiers.
- Missing provenance is release-blocking for production PASS and must be reconciled by RECONCILIATION_RULES.

Origin device rule: If Sale lacks originDeviceId, derive candidate origin from the claimed Tablet device context, Terminal, OutboxEvent payloadJson, aggregateId/idempotencyKey/clientRequestId or sync source event. If none exists, mark the sale BLOCKED for provenance.

Store derivation rule: When Sale has terminalId and not storeId, derive storeId through Terminal.storeId. If Terminal.storeId is absent, mark BLOCKED for store provenance.
