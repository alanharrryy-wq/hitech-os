# Payload JSON Index

Malformed payloads: 0
Empty payloads: 12

| table | column | path | types | frequency | sample |
| --- | --- | --- | --- | --- | --- |
| OutboxEvent | payloadJson | $ | object | 24 |  |
| OutboxEvent | diagnosticsJson | $ | object | 12 |  |
| OutboxEvent | payloadJson | clientRequestId | string | 24 | "req_seedline_0001" |
| OutboxEvent | payloadJson | createdAt | string | 24 | "2026-07-05T09:03:00Z" |
| OutboxEvent | payloadJson | folio | string | 24 | "PR-20260705-0001" |
| OutboxEvent | diagnosticsJson | lineage | string | 12 | "explicit" |
| OutboxEvent | payloadJson | originBusinessId | string | 24 | "biz_prisma_rey_lineage_seed" |
| OutboxEvent | payloadJson | originDeviceId | string | 24 | "DEV-2026-000002" |
| OutboxEvent | payloadJson | originDeviceType | string | 24 | "tablet_pos" |
| OutboxEvent | payloadJson | originSaleId | string | 24 | "sale_seedline_0001" |
| OutboxEvent | payloadJson | originStoreId | string | 24 | "store_prisma_rey_centro" |
| OutboxEvent | payloadJson | originTerminalId | string | 24 | "term_tablet_pos_001" |
| OutboxEvent | payloadJson | saleId | string | 24 | "sale_seedline_0001" |
| OutboxEvent | payloadJson | seedline | boolean | 24 | true |
| OutboxEvent | diagnosticsJson | seedline | boolean | 12 | true |
| OutboxEvent | payloadJson | sourceEventId | string | 24 | "evt_seedline_sale_0001" |
| OutboxEvent | payloadJson | status | string | 24 | "PAID" |
| OutboxEvent | payloadJson | surface | string | 24 | "tablet" |
| OutboxEvent | payloadJson | syncBatchId | string | 24 | "sync_batch_seedline_001" |
| OutboxEvent | payloadJson | target | string | 24 | "canonical" |
| OutboxEvent | payloadJson | totalCents | number | 24 | 3300 |
| runtime_chart_payloads | payloadJson | $ | object | 6 |  |
| runtime_chart_payloads | payloadJson | batchId | string | 6 | "lifecycle_light_20260705_063131_57e5dc" |
| runtime_chart_payloads | payloadJson | chartKey | string | 6 | "[REDACTED_SECRET]" |
| runtime_chart_payloads | payloadJson | generatedBy | string | 6 | "PRISMA Data Lifecycle" |
| runtime_chart_payloads | payloadJson | mode | string | 6 | "light" |
| runtime_chart_payloads | payloadJson | series | array | 6 |  |
| runtime_chart_payloads | payloadJson | series[0] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[0].day | number | 6 | 1 |
| runtime_chart_payloads | payloadJson | series[0].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[0].value | number | 6 | 153 |
| runtime_chart_payloads | payloadJson | series[1] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[1].day | number | 6 | 2 |
| runtime_chart_payloads | payloadJson | series[1].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[1].value | number | 6 | 163 |
| runtime_chart_payloads | payloadJson | series[10] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[10].day | number | 6 | 11 |
| runtime_chart_payloads | payloadJson | series[10].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[10].value | number | 6 | 200 |
| runtime_chart_payloads | payloadJson | series[11] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[11].day | number | 6 | 12 |
| runtime_chart_payloads | payloadJson | series[11].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[11].value | number | 6 | 208 |
| runtime_chart_payloads | payloadJson | series[12] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[12].day | number | 6 | 13 |
| runtime_chart_payloads | payloadJson | series[12].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[12].value | number | 6 | 136 |
| runtime_chart_payloads | payloadJson | series[13] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[13].day | number | 6 | 14 |
| runtime_chart_payloads | payloadJson | series[13].risk | string | 6 | "warn" |
| runtime_chart_payloads | payloadJson | series[13].value | number | 6 | 225 |
| runtime_chart_payloads | payloadJson | series[14] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[14].day | number | 6 | 15 |
| runtime_chart_payloads | payloadJson | series[14].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[14].value | number | 6 | 111 |
| runtime_chart_payloads | payloadJson | series[15] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[15].day | number | 6 | 16 |
| runtime_chart_payloads | payloadJson | series[15].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[15].value | number | 6 | 157 |
| runtime_chart_payloads | payloadJson | series[16] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[16].day | number | 6 | 17 |
| runtime_chart_payloads | payloadJson | series[16].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[16].value | number | 6 | 147 |
| runtime_chart_payloads | payloadJson | series[17] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[17].day | number | 6 | 18 |
| runtime_chart_payloads | payloadJson | series[17].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[17].value | number | 6 | 250 |
| runtime_chart_payloads | payloadJson | series[18] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[18].day | number | 6 | 19 |
| runtime_chart_payloads | payloadJson | series[18].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[18].value | number | 6 | 189 |
| runtime_chart_payloads | payloadJson | series[19] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[19].day | number | 6 | 20 |
| runtime_chart_payloads | payloadJson | series[19].risk | string | 6 | "warn" |
| runtime_chart_payloads | payloadJson | series[19].value | number | 6 | 204 |
| runtime_chart_payloads | payloadJson | series[2] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[2].day | number | 6 | 3 |
| runtime_chart_payloads | payloadJson | series[2].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[2].value | number | 6 | 172 |
| runtime_chart_payloads | payloadJson | series[20] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[20].day | number | 6 | 21 |
| runtime_chart_payloads | payloadJson | series[20].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[20].value | number | 6 | 205 |
| runtime_chart_payloads | payloadJson | series[21] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[21].day | number | 6 | 22 |
| runtime_chart_payloads | payloadJson | series[21].risk | string | 6 | "warn" |
| runtime_chart_payloads | payloadJson | series[21].value | number | 6 | 210 |
| runtime_chart_payloads | payloadJson | series[22] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[22].day | number | 6 | 23 |
| runtime_chart_payloads | payloadJson | series[22].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[22].value | number | 6 | 170 |
| runtime_chart_payloads | payloadJson | series[23] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[23].day | number | 6 | 24 |
| runtime_chart_payloads | payloadJson | series[23].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[23].value | number | 6 | 120 |
| runtime_chart_payloads | payloadJson | series[24] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[24].day | number | 6 | 25 |
| runtime_chart_payloads | payloadJson | series[24].risk | string | 6 | "critical" |
| runtime_chart_payloads | payloadJson | series[24].value | number | 6 | 183 |
| runtime_chart_payloads | payloadJson | series[25] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[25].day | number | 6 | 26 |
| runtime_chart_payloads | payloadJson | series[25].risk | string | 6 | "warn" |
| runtime_chart_payloads | payloadJson | series[25].value | number | 6 | 229 |
| runtime_chart_payloads | payloadJson | series[26] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[26].day | number | 6 | 27 |
| runtime_chart_payloads | payloadJson | series[26].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[26].value | number | 6 | 141 |
| runtime_chart_payloads | payloadJson | series[27] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[27].day | number | 6 | 28 |
| runtime_chart_payloads | payloadJson | series[27].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[27].value | number | 6 | 242 |
| runtime_chart_payloads | payloadJson | series[28] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[28].day | number | 6 | 29 |
| runtime_chart_payloads | payloadJson | series[28].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[28].value | number | 6 | 127 |
| runtime_chart_payloads | payloadJson | series[29] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[29].day | number | 6 | 30 |
| runtime_chart_payloads | payloadJson | series[29].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[29].value | number | 6 | 143 |
| runtime_chart_payloads | payloadJson | series[3] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[3].day | number | 6 | 4 |
| runtime_chart_payloads | payloadJson | series[3].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[3].value | number | 6 | 163 |
| runtime_chart_payloads | payloadJson | series[4] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[4].day | number | 6 | 5 |
| runtime_chart_payloads | payloadJson | series[4].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[4].value | number | 6 | 174 |
| runtime_chart_payloads | payloadJson | series[5] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[5].day | number | 6 | 6 |
| runtime_chart_payloads | payloadJson | series[5].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[5].value | number | 6 | 190 |
| runtime_chart_payloads | payloadJson | series[6] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[6].day | number | 6 | 7 |
| runtime_chart_payloads | payloadJson | series[6].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[6].value | number | 6 | 175 |
| runtime_chart_payloads | payloadJson | series[7] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[7].day | number | 6 | 8 |
| runtime_chart_payloads | payloadJson | series[7].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[7].value | number | 6 | 170 |
| runtime_chart_payloads | payloadJson | series[8] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[8].day | number | 6 | 9 |
| runtime_chart_payloads | payloadJson | series[8].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[8].value | number | 6 | 211 |
| runtime_chart_payloads | payloadJson | series[9] | object | 6 |  |
| runtime_chart_payloads | payloadJson | series[9].day | number | 6 | 10 |
| runtime_chart_payloads | payloadJson | series[9].risk | string | 6 | "ok" |
| runtime_chart_payloads | payloadJson | series[9].value | number | 6 | 233 |
| SalePaymentTender | metadataJson | $ | object | 24 |  |
| SalePaymentTender | metadataJson | clientRequestId | string | 24 | "req_seedline_0001" |
| SalePaymentTender | metadataJson | originBusinessId | string | 24 | "biz_prisma_rey_lineage_seed" |
| SalePaymentTender | metadataJson | originDeviceId | string | 24 | "DEV-2026-000002" |
| SalePaymentTender | metadataJson | originDeviceType | string | 24 | "tablet_pos" |
| SalePaymentTender | metadataJson | originSaleId | string | 24 | "sale_seedline_0001" |
| SalePaymentTender | metadataJson | originStoreId | string | 24 | "store_prisma_rey_centro" |
| SalePaymentTender | metadataJson | originTerminalId | string | 24 | "term_tablet_pos_001" |
| SalePaymentTender | metadataJson | seedline | boolean | 24 | true |
| SalePaymentTender | metadataJson | syncBatchId | string | 24 | "sync_batch_seedline_001" |
| SyncCheckpoint | metadataJson | $ | object | 2 |  |
| SyncCheckpoint | metadataJson | sales | number | 2 | 12 |
| SyncCheckpoint | metadataJson | seedline | boolean | 2 | true |
| SyncCheckpoint | metadataJson | tablets | number | 2 | 2 |
