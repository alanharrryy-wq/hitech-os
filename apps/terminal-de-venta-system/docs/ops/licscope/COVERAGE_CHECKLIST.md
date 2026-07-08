# LICSCOPE Coverage Checklist

Status: PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED

| item | status | fileProduced | evidence | blocker | nextAction |
| --- | --- | --- | --- | --- | --- |
| 1. Export row-level sanitizado completo de las DBs principales, no sólo samples. | PASS | docs/ops/licscope/row_exports_sanitized | docs/ops/licscope/row_exports_sanitized |  |  |
| 2. Todas las filas sanitizadas de estas tablas: CommandClient, LicenseAssignment, LicensePlan, ManagedDevice, ProvisioningDraft, CommandAuditEvent, Business, Store, Terminal, User, CashSession, Sale, SaleLine, SalePaymentTender, OutboxEvent, SyncCheckpoint, DeviceHeartbeat, AuditEvent. | PASS | docs/ops/licscope/row_exports_sanitized; docs/ops/licscope/row_counts.json | docs/ops/licscope/row_exports_sanitized,docs/ops/licscope/row_counts.json |  |  |
| 3. row_counts.json completo por DB y tabla. | PASS | docs/ops/licscope/row_counts.json | docs/ops/licscope/row_counts.json |  |  |
| 4. table_columns.json completo por DB y tabla. | PASS | docs/ops/licscope/table_columns.json | docs/ops/licscope/table_columns.json |  |  |
| 5. relationship_edges.json con relaciones reales detectadas entre cliente, business, licencia, device, store, terminal, usuario, cash session, venta, líneas, pagos, outbox y sync. | PASS | docs/ops/licscope/relationship_edges.json; docs/ops/licscope/RELATIONSHIP_EDGE_CLOSURE_REPORT.md | docs/ops/licscope/relationship_edges.json,docs/ops/licscope/RELATIONSHIP_EDGE_CLOSURE_REPORT.md |  |  |
| 6. payload_json_index.json con llaves encontradas dentro de OutboxEvent.payloadJson y cualquier payload operativo parecido. | PASS | docs/ops/licscope/payload_json_index.json | docs/ops/licscope/payload_json_index.json |  |  |
| 7. Contrato oficial de tenant/scope. | PASS | docs/ops/licscope/TENANT_SCOPE_CONTRACT.json; docs/ops/licscope/TENANT_SCOPE_CONTRACT.md | docs/ops/licscope/TENANT_SCOPE_CONTRACT.json,docs/ops/licscope/TENANT_SCOPE_CONTRACT.md |  |  |
| 8. Definición exacta de cloudTenantId. | PASS | docs/ops/licscope/CLOUD_TENANT_ID_DEFINITION.md | docs/ops/licscope/CLOUD_TENANT_ID_DEFINITION.md |  |  |
| 9. Definición exacta de scopeKey en SyncCheckpoint. | PASS | docs/ops/licscope/SYNC_SCOPEKEY_DEFINITION.md | docs/ops/licscope/SYNC_SCOPEKEY_DEFINITION.md |  |  |
| 10. Contrato de permisos por scope. | PASS | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json |  |  |
| 11. Contrato oficial de provenance de ventas. | PASS | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json |  |  |
| 12. Regla oficial para enlazar venta con outbox. | PASS | docs/ops/licscope/SALES_OUTBOX_LINKING_RULES.md | docs/ops/licscope/SALES_OUTBOX_LINKING_RULES.md |  |  |
| 13. Regla oficial para enlazar venta Tablet con venta canonical/PC. | PASS | docs/ops/licscope/TABLET_TO_CANONICAL_LINKING_RULES.md | docs/ops/licscope/TABLET_TO_CANONICAL_LINKING_RULES.md |  |  |
| 14. Regla oficial para originDeviceId cuando no existe campo directo en Sale. | PASS | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json |  |  |
| 15. Regla oficial para derivar storeId de venta cuando sólo existe terminalId. | PASS | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json; docs/ops/licscope/FIELD_ALIAS_CONTRACT.md | docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json,docs/ops/licscope/FIELD_ALIAS_CONTRACT.md |  |  |
| 16. Contrato de alias de campos en JSON. | PASS | docs/ops/licscope/FIELD_ALIAS_CONTRACT.md | docs/ops/licscope/FIELD_ALIAS_CONTRACT.md |  |  |
| 17. Datos reales o export completo de DeviceHeartbeat. | PASS | docs/ops/licscope/row_exports_sanitized | docs/ops/licscope/row_exports_sanitized |  |  |
| 18. Datos reales o export completo de AuditEvent. | PASS | docs/ops/licscope/row_exports_sanitized | docs/ops/licscope/row_exports_sanitized |  |  |
| 19. Datos reales o export completo de CommandAuditEvent. | PASS | docs/ops/licscope/row_exports_sanitized | docs/ops/licscope/row_exports_sanitized |  |  |
| 20. Confirmación explícita de tablas operativas vacías. | PASS | docs/ops/licscope/row_exports_sanitized; docs/ops/licscope/db_inventory.md | docs/ops/licscope/row_exports_sanitized,docs/ops/licscope/db_inventory.md |  |  |
| 21. Golden path operativo esperado paso por paso. | PASS | docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json | docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json |  |  |
| 22. Para cada paso del golden path: tabla, campo, API, surface, verifier y evidencia. | PASS | docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json | docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json |  |  |
| 23. Mapa API -> servicio/repositorio -> tabla -> surface -> verifier. | PASS | docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json | docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json |  |  |
| 24. Lista de rutas API de licensing/setup/customer/device/sales/sync/billing/revoke/renewal/replacement. | PASS | docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json | docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json |  |  |
| 25. Lista de servicios/repositorios que escriben o leen cliente, licencia, device, venta, outbox, sync y canonical. | PASS | docs/ops/licscope/SERVICE_REPOSITORY_MAP.json | docs/ops/licscope/SERVICE_REPOSITORY_MAP.json |  |  |
| 26. Contrato de roles por superficie. | PASS | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json; docs/ops/licscope/ENTITY_DEFINITIONS.json | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json,docs/ops/licscope/ENTITY_DEFINITIONS.json |  |  |
| 27. Regla dura de qué surface puede originar ventas. | PASS | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json; shared/licensing/feature-resolver.ts | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json,shared/licensing/feature-resolver.ts |  |  |
| 28. Regla dura de qué surface puede administrar licencias/devices. | PASS | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json |  |  |
| 29. Regla dura de qué surface sólo puede leer o supervisar. | PASS | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json | docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json |  |  |
| 30. Reglas customer-visible. | PASS | docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md | docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md |  |  |
| 31. Reglas para palabras demo/test/mock/dummy/smoke/prueba/fixture/pilot/piloto. | PASS | docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md; docs/ops/licscope/CUSTOMER_VISIBLE_SCAN.json | releaseBlockingCount=0 |  |  |
| 32. Lista de clientes/nombres de prueba permitidos. | PASS | docs/ops/licscope/ENTITY_DEFINITIONS.json; docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md | docs/ops/licscope/ENTITY_DEFINITIONS.json,docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md |  |  |
| 33. Lista de nombres o datos que bloquean release. | PASS | docs/ops/licscope/RELEASE_BLOCKING_VISIBLE_DATA.md | docs/ops/licscope/RELEASE_BLOCKING_VISIBLE_DATA.md |  |  |
| 34. Reglas de PII. | PASS | docs/ops/licscope/PII_REDACTION_RULES.md | docs/ops/licscope/PII_REDACTION_RULES.md |  |  |
| 35. Reglas de secretos. | PASS | docs/ops/licscope/SECRET_EXPOSURE_RULES.md | docs/ops/licscope/SECRET_EXPOSURE_RULES.md |  |  |
| 36. Dos snapshots operativos comparables. | PASS | docs/ops/licscope/snapshots/current; docs/ops/licscope/snapshots/previous | docs/ops/licscope/snapshots/current,docs/ops/licscope/snapshots/previous |  |  |
| 37. Snapshot anterior y snapshot actual de row counts. | PASS | docs/ops/licscope/snapshots/current/row_counts.json; docs/ops/licscope/snapshots/previous/row_counts.json | docs/ops/licscope/snapshots/current/row_counts.json,docs/ops/licscope/snapshots/previous/row_counts.json |  |  |
| 38. Snapshot anterior y actual de devices/licencias/clientes/ventas/outbox/sync. | PASS | docs/ops/licscope/snapshots/current/devices_licenses_clients_sales_outbox_sync.json; docs/ops/licscope/snapshots/previous/devices_licenses_clients_sales_outbox_sync.json | docs/ops/licscope/snapshots/current/devices_licenses_clients_sales_outbox_sync.json,docs/ops/licscope/snapshots/previous/devices_licenses_clients_sales_outbox_sync.json |  |  |
| 39. Historial mínimo de cambios operativos relevantes. | PASS | docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.json; docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.md | docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.json,docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.md |  |  |
| 40. Verifiers exactos que certifican setup de cliente. | PASS | docs/ops/licscope/verifier_outputs/verify-customer-setup-full.json | docs/ops/licscope/verifier_outputs/verify-customer-setup-full.json |  |  |
| 41. Verifiers exactos que certifican claim de Tablet. | PASS | docs/ops/licscope/verifier_outputs/verify-tablet-claim.json | docs/ops/licscope/verifier_outputs/verify-tablet-claim.json |  |  |
| 42. Verifiers exactos que certifican claim de PC. | PASS | docs/ops/licscope/verifier_outputs/verify-pc-claim.json | docs/ops/licscope/verifier_outputs/verify-pc-claim.json |  |  |
| 43. Verifiers exactos que certifican claim de Mobile. | PASS | docs/ops/licscope/verifier_outputs/verify-mobile-claim.json | docs/ops/licscope/verifier_outputs/verify-mobile-claim.json |  |  |
| 44. Verifiers exactos que certifican venta completa. | PASS | docs/ops/licscope/verifier_outputs/verify-device-without-license-blocked.json; tools/verify-data-surface-connections.mjs | docs/ops/licscope/verifier_outputs/verify-device-without-license-blocked.json,tools/verify-data-surface-connections.mjs |  |  |
| 45. Verifiers exactos que certifican outbox/sync/canonical. | PASS | docs/ops/licscope/verifier_outputs/verify-outbox-sync-canonical.json | docs/ops/licscope/verifier_outputs/verify-outbox-sync-canonical.json |  |  |
| 46. Verifiers exactos que certifican revoke/renewal/device replacement. | PASS | docs/ops/licscope/verifier_outputs/verify-revoke-renewal-replacement.json | docs/ops/licscope/verifier_outputs/verify-revoke-renewal-replacement.json |  |  |
| 47. Evidencia runtime relacionada con licensing, devices, sales, sync, PC, Tablet y Mobile. | PASS | docs/ops/licscope/live_smoke_outputs/cloudflare-d1-oauth-certification.json; docs/ops/licscope/live_smoke_outputs/cloud-center-live-readiness.json; docs/ops/licscope/live_smoke_outputs/local-runtime-surface-readiness.json; docs/ops/licscope/RUNTIME_EVIDENCE_LINKS.json | PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED; PASS_LOCAL_RUNTIME_READONLY |  |  |
| 48. Contrato de production readiness. | PASS | docs/ops/licscope/PRODUCTION_READINESS_CONTRACT.json | docs/ops/licscope/PRODUCTION_READINESS_CONTRACT.json |  |  |
| 49. Reglas para orphan detector. | PASS | docs/ops/licscope/ORPHAN_DETECTOR_RULES.json | docs/ops/licscope/ORPHAN_DETECTOR_RULES.json |  |  |
| 50. Reglas para duplicate detector. | PASS | docs/ops/licscope/DUPLICATE_DETECTOR_RULES.json | docs/ops/licscope/DUPLICATE_DETECTOR_RULES.json |  |  |
| 51. Reglas para staleness. | PASS | docs/ops/licscope/STALENESS_RULES.json | docs/ops/licscope/STALENESS_RULES.json |  |  |
| 52. Reglas para audit completeness. | PASS | docs/ops/licscope/AUDIT_COMPLETENESS_RULES.json | docs/ops/licscope/AUDIT_COMPLETENESS_RULES.json |  |  |
| 53. Reglas de reconciliación. | PASS | docs/ops/licscope/RECONCILIATION_RULES.json | docs/ops/licscope/RECONCILIATION_RULES.json |  |  |
| 54. Mapa de customer setup journey. | PASS | docs/ops/licscope/CUSTOMER_SETUP_JOURNEY_MAP.json | docs/ops/licscope/CUSTOMER_SETUP_JOURNEY_MAP.json |  |  |
| 55. Definición de cliente real vs cliente fixture vs cliente smoke. | PASS | docs/ops/licscope/ENTITY_DEFINITIONS.json | docs/ops/licscope/ENTITY_DEFINITIONS.json |  |  |
| 56. Definición de multi-tenant leakage. | PASS | docs/ops/licscope/MULTI_TENANT_LEAKAGE_DEFINITION.md | docs/ops/licscope/MULTI_TENANT_LEAKAGE_DEFINITION.md |  |  |
| 57. Definición de business/client/store/terminal ownership. | PASS | docs/ops/licscope/BUSINESS_CLIENT_STORE_TERMINAL_OWNERSHIP.md | docs/ops/licscope/BUSINESS_CLIENT_STORE_TERMINAL_OWNERSHIP.md |  |  |
| 58. Definición de canonical projection. | PASS | docs/ops/licscope/CANONICAL_PROJECTION_DEFINITION.md | docs/ops/licscope/CANONICAL_PROJECTION_DEFINITION.md |  |  |
| 59. Definición de sync checkpoint correcto. | PASS | docs/ops/licscope/SYNC_CHECKPOINT_DEFINITION.md | docs/ops/licscope/SYNC_CHECKPOINT_DEFINITION.md |  |  |
| 60. Cualquier .env.example, config sanitizada o docs que expliquen nombres de DB, sin secretos reales. | PASS | docs/ops/licscope/SANITIZED_CONFIG_INDEX.json | docs/ops/licscope/SANITIZED_CONFIG_INDEX.json |  |  |
| Final result ZIP | PASS | F:\descargasf\licscope-pass-oauth-d1-local-runtime-20260707_162641.zip | ZIP exists: F:\descargasf\licscope-pass-oauth-d1-local-runtime-20260707_162641.zip,F:\descargasf\licscope-pass-oauth-d1-local-runtime-20260707_162641.zip.sha256.txt |  |  |
