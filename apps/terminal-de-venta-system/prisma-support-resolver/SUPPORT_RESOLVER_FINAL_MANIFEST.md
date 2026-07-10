# PRISMA Support Resolver Final Manifest

- Generated: `2026-07-10T09:31:33.375946+00:00`
- Decision: `VERIFY_AND_FIX_EXISTING_NOT_REBUILD`
- Final runtime status: `PARTIAL_SUPPORT_RESOLVER_GAPS_REMAIN`
- UI data status: `PASS_SUPPORT_DATA_SPINE_READY_FOR_UI`
- Runtime certified: **No**. This manifest and feed are the complete UI data substrate, not a production-runtime certification.

## Executive inventory

| Metric | Value |
|---|---|
| decision | VERIFY_AND_FIX_EXISTING_NOT_REBUILD |
| doNotRebuild | True |
| canonicalArtifactCount | 57 |
| externalIntegrationCandidateCount | 20 |
| errorCodeCount | 68 |
| errorCodesImplemented | 29 |
| errorCodesDirectlyTested | 68 |
| actionCount | 13 |
| actionsImplemented | 5 |
| actionsDirectlyTested | 3 |
| uiRouteCount | 9 |
| apiRouteCount | 9 |
| gapCount | 50 |
| blockingGapCount | 1 |
| blockingSecretRiskCount | 0 |
| duplicateAuthorityBlockerCount | 1 |
| uiFeedReady | True |
| runtimeCertified | False |

## Canonical artifacts

| Path | Type | Existed before | Action |
|---|---|---|---|
| prisma-support-resolver\README.md | DOCUMENT | True | USE_AS_IS |
| prisma-support-resolver\AUTHORITY_MAP.md | DOCUMENT | True | USE_AS_IS |
| prisma-support-resolver\DUPLICATE_MAP.md | DOCUMENT | True | USE_AS_IS |
| prisma-support-resolver\DEPRECATION_MAP.md | DOCUMENT | True | USE_AS_IS |
| prisma-support-resolver\MIGRATION_REPORT.md | DOCUMENT | True | USE_AS_IS |
| prisma-support-resolver\SUPPORT_RESOLVER_FINAL_MANIFEST.json | MANIFEST | False | CREATE_MISSING |
| prisma-support-resolver\SUPPORT_RESOLVER_FINAL_MANIFEST.md | DOCUMENT | False | CREATE_MISSING |
| prisma-support-resolver\SUPPORT_RESOLVER_GAP_REGISTER.json | MANIFEST | False | CREATE_MISSING |
| prisma-support-resolver\SUPPORT_RESOLVER_GAP_REGISTER.md | DOCUMENT | False | CREATE_MISSING |
| prisma-support-resolver\SUPPORT_RESOLVER_UI_HANDOFF.json | MANIFEST | False | CREATE_MISSING |
| prisma-support-resolver\SUPPORT_RESOLVER_UI_HANDOFF.md | DOCUMENT | False | CREATE_MISSING |
| prisma-support-resolver\catalogs\feature-gates.json | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\catalogs\resolver-actions.json | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\catalogs\resolver-actions.md | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\catalogs\support-error-codes.json | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\catalogs\support-error-codes.md | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\catalogs\surface-status-catalog.json | CATALOG | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_CUSTOMER_SETUP_CANONICAL_CONTRACT.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_DEVICE_ACTIVATION_CANONICAL_CONTRACT.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_RUNTIME_CONFIG_CANONICAL_CONTRACT.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_BUNDLE_STANDARD.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_ERROR_CODE_CATALOG.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_RESOLUTION_ACTION_MATRIX.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_RESOLVER_CENTER_CONTRACT.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_SEARCH_AND_CASE_SCHEMA.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\contracts\PRISMA_SUPPORT_SURFACE_STATUS_STANDARD.md | CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\schemas\customer-setup.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\device-identity.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\runtime-config.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\support-bundle.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\support-case.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\support-issue.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\support-resolution-action.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\support-search.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\schemas\surface-status.schema.json | SCHEMA | True | USE_AS_IS |
| prisma-support-resolver\adapters\README.md | ADAPTER | True | USE_AS_IS |
| prisma-support-resolver\adapters\cloud-center-adapter.md | ADAPTER | True | USE_AS_IS |
| prisma-support-resolver\adapters\mobile-surface-adapter.md | ADAPTER | True | USE_AS_IS |
| prisma-support-resolver\adapters\pc-surface-adapter.md | ADAPTER | True | USE_AS_IS |
| prisma-support-resolver\adapters\tablet-surface-adapter.md | ADAPTER | True | USE_AS_IS |
| prisma-support-resolver\evidence\README.md | EVIDENCE_CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\evidence\evidence-export-contract.md | EVIDENCE_CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\evidence\support-bundle-redaction-rules.md | EVIDENCE_CONTRACT | True | USE_AS_IS |
| prisma-support-resolver\fixtures\README.md | FIXTURE | True | USE_AS_IS |
| prisma-support-resolver\fixtures\demo\cross-source-identity-split.support-issue.json | FIXTURE | True | USE_AS_IS |
| prisma-support-resolver\fixtures\demo\license-assignment-wrong-business.support-issue.json | FIXTURE | True | USE_AS_IS |
| prisma-support-resolver\fixtures\demo\surface-status.tablet.blocked.json | FIXTURE | True | USE_AS_IS |
| prisma-support-resolver\fixtures\sanitized\external-licensing-inventory.json | FIXTURE | True | USE_AS_IS |
| prisma-support-resolver\tests\README.md | TEST_ASSET | True | USE_AS_IS |
| prisma-support-resolver\tests\cases\cross-source-identity-split.case.json | TEST_ASSET | True | USE_AS_IS |
| prisma-support-resolver\tests\cases\license-assignment-wrong-business.case.json | TEST_ASSET | True | USE_AS_IS |
| prisma-support-resolver\tests\cases\setup-claim-or-refresh-apply-preflight.case.json | TEST_ASSET | True | USE_AS_IS |
| prisma-support-resolver\tests\cases\setup-claim-or-refresh-guided.case.json | TEST_ASSET | True | USE_AS_IS |
| prisma-support-resolver\generated\ui\README.md | UI_FEED | False | CREATE_MISSING |
| prisma-support-resolver\generated\ui\support-resolver-ui-feed.json | UI_FEED | False | CREATE_MISSING |
| prisma-support-resolver\generated\ui\support-resolver-ui-feed.schema.json | UI_FEED | False | CREATE_MISSING |
| prisma-support-resolver\generated\ui\support-resolver-ui-types.ts | UI_FEED | False | CREATE_MISSING |

## Runtime gaps

Gaps recorded: **50**. Missing canonical artifacts before generation: **8**.

See `SUPPORT_RESOLVER_GAP_REGISTER.md` for item-level classifications.

## UI handoff

Codex must consume `generated/ui/support-resolver-ui-feed.json` and must not invent capabilities absent from the feed.
