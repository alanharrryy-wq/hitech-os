# Sales Outbox Linking Rules

Official link candidates, in order: `OutboxEvent.aggregateId`, `idempotencyKey`, `clientRequestId`, parsed `payloadJson.saleId`, parsed `payloadJson.clientRequestId`, parsed source event ids. If no candidate exists, mark BLOCKED for production provenance.
