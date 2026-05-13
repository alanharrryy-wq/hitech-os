# Phase 4: Data Truth — PRISMA Quality OS

## Overview

Phase 4 establishes **PRISMA as a Knowledge OS**, not just a Point-of-Sale system. Data Truth is the foundation that enforces:

1. **Tablet Sovereignty** — tablet operations are the source of truth and immutable
2. **PC Governance** — backoffice approvals are write-once with full audit trail
3. **Mobile Supervision** — mobile can only read and report, never write
4. **Core Ledger** — core records are append-only and immutable
5. **Control Audit** — every action is captured with cryptographic proof

---

## Core Principle: The Rule Mother (Regla Madre)

```
Tablet opera.
PC gobierna.
Mobile supervisa.
Core registra.
Control audita.
```

This is not a preference. This is the **architectural invariant** of PRISMA.

---

## Data Contract Model

All data flows through **5 explicit contracts**:

### DC_TABLET_OPERATIONS (T0_SOVEREIGN)

**Owner**: Tablet Operator  
**Trust Level**: T0_SOVEREIGN (immutable once recorded)  
**Mutation Policy**: Capture-only (no writes, only events)

```json
{
  "required_fields": [
    "operation_id",
    "transaction_timestamp",
    "amount_cents",
    "item_sku"
  ],
  "integrity_mode": "immutable"
}
```

Once a transaction is captured on tablet, it **cannot be modified**. It can only be audited.

### DC_PC_GOVERNANCE (T1_CERTIFIED)

**Owner**: Backoffice Authority  
**Trust Level**: T1_CERTIFIED (write-once)  
**Mutation Policy**: Audit-trail-required

```json
{
  "required_fields": [
    "policy_id",
    "approval_timestamp",
    "governance_decision"
  ],
  "integrity_mode": "write-once"
}
```

PC can write governance decisions **once**. Changes require a new decision entry with timestamp.

### DC_MOBILE_SUPERVISION (T2_SUPERVISED)

**Owner**: Mobile Supervisor  
**Trust Level**: T2_SUPERVISED (read-only)  
**Mutation Policy**: Read-only

```json
{
  "required_fields": [
    "snapshot_id",
    "status_timestamp",
    "visibility_flags"
  ],
  "integrity_mode": "queryable"
}
```

Mobile has **read-only access**. It can query and report, but never write.

### DC_CORE_LEDGER (T0_IMMUTABLE)

**Owner**: Core Ledger Guard  
**Trust Level**: T0_IMMUTABLE (append-only)  
**Mutation Policy**: Never

```json
{
  "required_fields": [
    "ledger_entry_id",
    "evidence_hash",
    "recorded_timestamp",
    "verifier_signature"
  ],
  "integrity_mode": "append-only"
}
```

Core ledger is **append-only forever**. No deletion, no modification.

### DC_CONTROL_AUDIT (T0_IMMUTABLE)

**Owner**: Control Auditor  
**Trust Level**: T0_IMMUTABLE (append-only)  
**Mutation Policy**: Capture-only

```json
{
  "required_fields": [
    "audit_id",
    "action_timestamp",
    "actor",
    "action_type",
    "target_data"
  ],
  "integrity_mode": "append-only"
}
```

Control audit captures **every action** with cryptographic proof. Cannot be modified.

---

## Gates That Enforce Data Truth

### Q21: Data Contract Registry

Validates that all 5 contracts exist, are properly defined, and have verifiable evidence.

**Failure**: Any contract missing, undefined, or lacking evidence = S1 BLOCKED.

### Q22: Evidence Ledger Integrity

Scans the evidence ledger file itself for corruption, truncation, or hash mismatches.

**Failure**: Ledger truncation, missing entries, or invalid signatures = S0 BLOCKED.

### Q23: Freshness & Confidence Model

Checks when each contract was last verified and calculates trustworthiness.

**Failure**: Stale data (>24h old) without fresh evidence = S2 WARNING.

### Q24: Schema Drift & Migration Guard

Detects schema changes that could violate data contracts.

**Failure**: Unauthorized schema mutation = S1 BLOCKED.

### Q25: Audit Trail Completeness

Ensures every recorded mutation has a corresponding audit entry.

**Failure**: Missing audit entry for known mutation = S1 BLOCKED.

---

## No Fake Green

Phase 4 **forbids fake green status**:

- ✅ **READY** = Contracts exist AND have real evidence AND are verifiable
- ❌ **READY** = Contracts are assumed to exist
- ❌ **READY** = Contracts passed in a previous run (evidence must be fresh)

Every gate must produce fresh evidence during the run. No caching of previous verdicts.

---

## Mutation Policy Enforcement

| Layer | Can Write? | Can Read? | Mutation Allowed? | Audit Required? |
|-------|-----------|----------|-------------------|-----------------|
| Tablet | Yes (capture) | Yes | No | Yes |
| PC | Yes (once) | Yes | Trail required | Yes |
| Mobile | No | Yes | Never | N/A |
| Core | No (append) | Yes | Append only | Yes |
| Control | No (append) | Yes | Append only | Yes |

---

## Evidence Requirements

All Phase 4 gates produce **cryptographic evidence**:

```json
{
  "schemaVersion": "1.0",
  "runId": "run-2026-05-12-xyz",
  "evidenceId": "Q21_data_contract_registry_0",
  "gateId": "Q21",
  "type": "data_contract_validation",
  "summary": "5/5 contracts valid, all have evidence",
  "createdAt": "2026-05-12T10:00:00Z",
  "payload": {
    "contracts_registered": 5,
    "contracts_with_evidence": 5,
    "contracts_valid": 5,
    "contracts": [...]
  }
}
```

Evidence is **redacted** (no secrets, no PII) and **immutable** once written.

---

## No Data Mutations During Quality Runs

Phase 4 is **inspection-only**:

- ❌ No INSERT, UPDATE, DELETE
- ❌ No schema migrations
- ❌ No data resets
- ❌ No test data seeding

Only **READ and ANALYZE**.

---

## References

- [Data Contract Model](./data-contract-model.md)
- [Evidence Ledger Hardening](./evidence-ledger-hardening.md)
- [quality/data/README.md](../data/README.md)
- [Data Truth Policy](../policies/data-truth-policy.json)
