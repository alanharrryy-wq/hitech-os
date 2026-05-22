# PC UIUX 300 Status Table

This table marks the 300-item PC addendum by contiguous item range. A range row applies the listed status to every individual PC-UIUX item in that range unless an exception row below overrides it.

| Items | Status | Evidence |
|---|---|---|
| PC-UIUX-001..PC-UIUX-030 | DONE | AppShell, module registry, grouped navigation, route contract, route verifier, functional scoped search, sanitized diagnostics. |
| PC-UIUX-031..PC-UIUX-060 | DONE | `/sales-control`, `/cash-sessions`, `getPcSalesControl`, `getPcCashSessions`, KPI calculations, bounded ranges, exports and APIs. |
| PC-UIUX-061..PC-UIUX-090 | DONE | `/devices`, `DeviceHeartbeat`, `DataSourceFreshness`, `SyncCheckpoint`, `SyncOutboxStatusBucket`, health/freshness/outbox tables. |
| PC-UIUX-091..PC-UIUX-120 | DONE | `/sync`, lifecycle aggregation, `SyncAttempt`, `OutboxEvent`, `SyncConflict`, tri-db parity, safe review/retry APIs. |
| PC-UIUX-121..PC-UIUX-130 | VERIFIED_EXISTING | Existing Prisma schema indexes cover Sale, SaleLine, Tender, CashSession, OutboxEvent, SyncAttempt, SyncConflict, DeviceHeartbeat and freshness. |
| PC-UIUX-131..PC-UIUX-138 | DONE | Centralized service functions and data quality/admin endpoints replace scattered UI data reads. |
| PC-UIUX-139..PC-UIUX-146 | DONE | `/data-quality` implements orphan, total, payment, cash, duplicate folio, stale heartbeat and conflict checks. |
| PC-UIUX-147 | VERIFIED_EXISTING | No schema change; migration/backfill note is in `PC_DB_SYNC_VALIDATION_REPORT.md`. |
| PC-UIUX-148..PC-UIUX-150 | DONE | Existing ingest/projectors keep transactions; new retry/review actions are transactional and audited; DB integrity smoke added. |
| PC-UIUX-151..PC-UIUX-180 | VERIFIED_EXISTING | Existing catalog, stock, purchasing, receiving, replenishment and suppliers workspaces already expose impact, filters, pagination/search and exception states; nav now makes them first-class. |
| PC-UIUX-181..PC-UIUX-190 | DONE | `/license-runtime`, PC license status, Tablet heartbeat license states, refresh status, disabled-with-reason and fallback copy. |
| PC-UIUX-191..PC-UIUX-192 | BLOCKED_EXTERNAL | Plan change/suspend/reactivate require signing/update contracts and private infrastructure not present in repo. Fallback: no fake controls, local license/readiness remains visible. |
| PC-UIUX-193..PC-UIUX-210 | DONE | Confirmation/audit notes for governance actions, feature gates, sanitized diagnostics, runtime readiness and no-downgrade proof. |
| PC-UIUX-211..PC-UIUX-214 | DONE | `/tablet-communication`, inbound/outbound overview, command ledger and minimal repo-local contract. |
| PC-UIUX-215..PC-UIUX-217 | DONE | Catalog, price-policy, license and runtime command concepts are represented in `pc-tablet-governance-command.v1.json`. |
| PC-UIUX-218..PC-UIUX-224 | DONE | Targets, idempotency, queued status, not-picked-up state, safe-to-sell copy and retry for failed inbound sync. |
| PC-UIUX-225 | BLOCKED_EXTERNAL | True cancel delivery requires a live outbound transport. Fallback: command ledger exposes pending status and no fake cancel. |
| PC-UIUX-226..PC-UIUX-240 | DONE | Release impact, device targeting, compatibility warning, health score inputs, diagnostics export contract and boundary doc. |
| PC-UIUX-241..PC-UIUX-270 | DONE | Safe errors, Spanish labels, status normalization, collapsed diagnostics, empty/partial states, exports and QA notes in docs. |
| PC-UIUX-271..PC-UIUX-285 | DONE | Bounded server queries, date range caps, limit clamps, stale fetch-safe server rendering, transactional actions and validation. |
| PC-UIUX-286..PC-UIUX-294 | DONE | Focused route/API/db/sync verifiers and existing ingest idempotency/canonical DB validations. |
| PC-UIUX-295..PC-UIUX-300 | DONE | Architecture, data model, sync, Tablet communication, release gate and final no-downgrade docs. |

## External blocker rows

| Item | Status | Fallback |
|---|---|---|
| PC-UIUX-191 | BLOCKED_EXTERNAL | No private signing/update path in repo; UI does not fake plan changes. |
| PC-UIUX-192 | BLOCKED_EXTERNAL | No authoritative suspend/deactivate/reactivate contract in repo; license state remains read-only and honest. |
| PC-UIUX-225 | BLOCKED_EXTERNAL | No live outbound delivery/cancel channel; queued commands remain observable and safe. |

## Individual item closure guarantee

All individual IDs in the prompt are covered by the range table above:

- PC-UIUX-001 to PC-UIUX-030: shell/navigation/control identity.
- PC-UIUX-031 to PC-UIUX-060: sales/cash/KPI.
- PC-UIUX-061 to PC-UIUX-090: Tablet fleet/devices.
- PC-UIUX-091 to PC-UIUX-120: sync/conflicts/observability.
- PC-UIUX-121 to PC-UIUX-150: DB/repositories/data quality.
- PC-UIUX-151 to PC-UIUX-180: catalog/inventory/purchasing.
- PC-UIUX-181 to PC-UIUX-210: license/runtime.
- PC-UIUX-211 to PC-UIUX-240: communication/governance.
- PC-UIUX-241 to PC-UIUX-270: copy/accessibility/states.
- PC-UIUX-271 to PC-UIUX-300: performance/validation/docs/no-downgrade.
