# PRISMA Quality Data Module

This directory contains the Phase 4 data specifications and contracts for PRISMA Quality Operating System.

## Overview

The data module is part of the **Phase 4: Data Truth, Evidence Ledger & Audit Hardening** initiative.

### Key Files

- **data-contract-registry.json** - Registry of all data contracts across layers (Tablet, PC, Mobile, Core, Control)
- Evidence ledger files (generated at runtime)
- Audit trail records (generated at runtime)

## Architecture

### Data Contracts

PRISMA enforces **5 data contracts** across operational layers:

| Layer | Contract | Owner | Trust Level | Mutation |
|-------|----------|-------|-------------|----------|
| Tablet | DC_TABLET_OPERATIONS | Operator | T0_SOVEREIGN | Capture-only |
| PC | DC_PC_GOVERNANCE | Backoffice | T1_CERTIFIED | Audit-trail-required |
| Mobile | DC_MOBILE_SUPERVISION | Supervisor | T2_SUPERVISED | Read-only |
| Core | DC_CORE_LEDGER | Ledger Guard | T0_IMMUTABLE | Never |
| Control | DC_CONTROL_AUDIT | Auditor | T0_IMMUTABLE | Capture-only |

### Trust Levels

- **T0_SOVEREIGN**: Tablet operator truth, immutable once recorded
- **T1_CERTIFIED**: PC governance, write-once with audit trail
- **T2_SUPERVISED**: Mobile visibility, read-only queries allowed
- **T0_IMMUTABLE**: Core and Control layers, append-only forever

## Rules

### No Fake Green

All data contract assertions must have real verifiable evidence. Phase 4 gates (Q21-Q25) enforce this strictly.

### Mutation Policy

Only immutable (`append-only`) or captured (`capture-only`) modes are allowed in critical layers.

### Audit Trail

Every data mutation must be recorded in the Control audit layer with timestamp, actor, and action type.

### Evidence Contract

Evidence files themselves must be cryptographically signed at generation time.

## Gates Using This Module

- **Q21**: Data Contract Registry - Validate all contracts exist and have evidence
- **Q22**: Evidence Ledger Integrity - Verify ledger structure and cryptography
- **Q23**: Freshness & Confidence Model - Check data age and trustworthiness
- **Q24**: Schema Drift & Migration Guard - Detect schema mutations
- **Q25**: Audit Trail Completeness - Ensure all actions are recorded

## Runtime Generation

During `pnpm quality:phase4`:

1. Q21 audits the data contract registry against actual layer implementations
2. Q22 validates evidence ledger format and checksums
3. Q23 checks when each contract was last verified
4. Q24 scans for schema migrations that could violate contracts
5. Q25 ensures audit trails are complete for all recorded mutations

## Not Included Here

- Product data models (see `products/*/src/data/`)
- Runtime data state (ephemeral)
- Personal identifiable information (PII) - all evidence is redacted
- Cloudflare worker data (optional layer)

## References

- [Phase 4 Data Truth](../docs/phase-4-data-truth.md)
- [Evidence Ledger Hardening](../docs/evidence-ledger-hardening.md)
- [Data Contract Model](../docs/data-contract-model.md)
