# SALES_OUTBOX_LINKING_MATRIX

| sale | outbox | status | evidence |
| --- | --- | --- | --- |
| Sale.id | OutboxEvent.aggregateId/payloadJson | WARNING | payload_json_index.json |
