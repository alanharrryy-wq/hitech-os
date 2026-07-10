# Code Atlas Support Resolver Consumer V01

Current implementation version: `1.1.0`.

## Purpose

Consume the canonical `prisma-support-resolver` contracts and compare them with the current repository without rebuilding existing support capabilities.

## Classification corrections in 1.1.0

- Verifiers and smoke/E2E scripts under `tools/` and `scripts/` are recognized as test evidence.
- Direct code references and catalog-wide verifier evidence are reported separately.
- Importers and consumers of `support_resolver_api` are no longer counted as duplicate implementations.
- `supportUiRouteMap` contains only real `UI_ROUTE` and `API_ROUTE` artifacts.
- Security findings include severity, confidence, blocking state and line number, never values or matching source text.
- Policy mentions such as “private key” or “authorization” are not blockers by themselves.

## Outputs

- `supportResolverSummary`
- `supportCapabilityMatrix`
- `supportErrorCodeCoverage`
- `supportActionCoverage`
- `supportUiRouteMap`
- `supportE2eCoverage`
- `supportDuplicateImplementations`
- `supportDoNotRebuildMap`
- `supportContractCoverage`
- `supportSecurityRisks`

Every dataset is exported as JSON, CSV and Markdown under `support_resolver/` and projected into the Operational Evidence Atlas viewer.

## Hard rules

- Existing support, licensing, Customer Setup and incident capabilities are classified before any BUILD decision.
- The 68 canonical support codes are measured against active source, direct tests and catalog-wide verifiers without conflating those evidence levels.
- Canonical `Prisma Cloud Ctr` and deprecated `prisma-control-center` implementations are reported separately.
- Duplicate authority is based on concrete implementation files or class definitions, not imports or text mentions.
- Secret values and matching source lines are never exported.
- Missing evidence produces a partial or blocked status. It never produces fake green.
- This consumer is read-only during Atlas execution.
