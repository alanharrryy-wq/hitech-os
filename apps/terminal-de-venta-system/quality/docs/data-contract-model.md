# Data Contract Model — Phase 4

## Definition

A **Data Contract** is a formal specification that defines:

1. **What data exists** in a layer
2. **Who owns the data** (the authoritative source)
3. **How the data can be modified** (mutation policy)
4. **When the data is truth** (trust level)
5. **What evidence proves** the contract is honored

---

## The 5 Contracts

### 1. DC_TABLET_OPERATIONS

**Layer**: Tablet (POS Device)  
**Owner**: Tablet Operator (Cashier)  
**Trust Level**: T0_SOVEREIGN  
**Mutation Policy**: Capture-only (immutable)  
**Source of Truth**: `products/tablet/app/src/data/`

#### Contract Fields

```json
{
  "operation_id": "op_20260512_001",
  "transaction_timestamp": "2026-05-12T10:30:45Z",
  "amount_cents": 5999,
  "item_sku": "SKU-PRODUCT-001"
}
```

#### Rules

- Once recorded on tablet, **cannot be changed**
- Is the **single source of truth** for what happened at the register
- PC governance can approve or reject, but cannot alter the transaction record itself
- Mobile can see it as a read-only snapshot
- Core ledger records it immutably
- Control audit tracks every query

#### Mutation Policy: Capture-Only

```
Tablet Operations:
  ✓ Create new operation event
  ✗ Modify existing event
  ✗ Delete event
  
Result: immutable history of what happened at POS
```

---

### 2. DC_PC_GOVERNANCE

**Layer**: PC (Backoffice)  
**Owner**: Backoffice Authority (Manager/Admin)  
**Trust Level**: T1_CERTIFIED  
**Mutation Policy**: Audit-trail-required (write-once)  
**Source of Truth**: `products/pc/app/src/data/`

#### Contract Fields

```json
{
  "policy_id": "pol_20260512_void_001",
  "approval_timestamp": "2026-05-12T10:35:00Z",
  "governance_decision": "VOID_TRANSACTION",
  "approver_id": "user_manager_001"
}
```

#### Rules

- PC can **write governance decisions** about tablet operations
- Once written, the decision **cannot be modified**
- If a decision needs to be reversed, a new decision entry is created
- Full audit trail of approvals
- Mobile can see governance decisions as read-only
- Core records decisions immutably
- Control audits who approved what and when

#### Mutation Policy: Audit-Trail-Required

```
PC Governance:
  ✓ Write new decision (with timestamp)
  ✓ Reverse a decision (via new entry)
  ✗ Modify existing decision
  ✗ Delete decision
  
Result: Write-once with decision history
```

---

### 3. DC_MOBILE_SUPERVISION

**Layer**: Mobile (Supervisor App)  
**Owner**: Mobile Supervisor (Shift Supervisor)  
**Trust Level**: T2_SUPERVISED  
**Mutation Policy**: Read-only  
**Source of Truth**: Mobile-generated snapshots (not authoritative)

#### Contract Fields

```json
{
  "snapshot_id": "snap_20260512_001",
  "status_timestamp": "2026-05-12T10:00:00Z",
  "visibility_flags": {
    "can_see_tablet": true,
    "can_see_governance": true,
    "can_see_audit": false
  }
}
```

#### Rules

- Mobile **cannot write** to operational or governance data
- Can **only read and report** status
- Snapshots are for supervision purposes, not truth-building
- Cannot affect tablet operations or backoffice decisions
- Core records mobile visibility queries
- Control audits what mobile accessed

#### Mutation Policy: Read-Only

```
Mobile Supervision:
  ✓ Query operations
  ✓ Query governance decisions
  ✓ Generate visibility report
  ✗ Write any data
  ✗ Modify any data
  
Result: Passive supervision, zero write capability
```

---

### 4. DC_CORE_LEDGER

**Layer**: Core (PRISMA Kernel)  
**Owner**: Core Ledger Guard  
**Trust Level**: T0_IMMUTABLE  
**Mutation Policy**: Append-only forever  
**Source of Truth**: `quality/data/`

#### Contract Fields

```json
{
  "ledger_entry_id": "led_20260512_001",
  "evidence_hash": "sha256:abc123...",
  "recorded_timestamp": "2026-05-12T10:30:45Z",
  "verifier_signature": "sig:xyz789..."
}
```

#### Rules

- Core records **everything that happened**, from all layers
- **Never deletes or modifies** entries once recorded
- Is the **ultimate source of truth** for the system's history
- Cannot be directly written to by operators
- Is only written to by the quality system (gates, evidence)
- Mobile cannot access
- Control audits who accessed the ledger

#### Mutation Policy: Append-Only

```
Core Ledger:
  ✓ Append new entry (immutable once written)
  ✗ Modify any entry
  ✗ Delete any entry
  ✗ Truncate ledger
  
Result: Permanent, forensic-replay-capable history
```

---

### 5. DC_CONTROL_AUDIT

**Layer**: Control (PRISMA Auditor)  
**Owner**: Control Auditor  
**Trust Level**: T0_IMMUTABLE  
**Mutation Policy**: Capture-only (append-only)  
**Source of Truth**: `quality/data/audit-trails/`

#### Contract Fields

```json
{
  "audit_id": "aud_20260512_001",
  "action_timestamp": "2026-05-12T10:30:45Z",
  "actor": "user_manager_001",
  "action_type": "QUERY_OPERATIONS",
  "target_data": "DC_TABLET_OPERATIONS"
}
```

#### Rules

- Control audits **every access to every layer**
- Records **who did what, when, and to what data**
- **Never modifies or deletes** audit entries
- Is the **forensic proof** of system activity
- Cannot be accessed by any layer except Control itself
- Must be cryptographically signed
- Used for compliance, forensics, and security analysis

#### Mutation Policy: Capture-Only

```
Control Audit:
  ✓ Record action (with timestamp, actor, type)
  ✗ Modify audit entry
  ✗ Delete audit entry
  
Result: Cryptographic proof of who accessed what
```

---

## Trust Levels

### T0_SOVEREIGN

**Used by**: Tablet, Core Ledger, Control Audit  
**Meaning**: The source of truth; immutable once recorded  
**Properties**:
- Cannot be modified after creation
- Is the single authoritative source
- Modifiable only by append (ledger/audit only)
- Requires highest evidence standard

### T1_CERTIFIED

**Used by**: PC Governance  
**Meaning**: Certified decision with write-once semantics  
**Properties**:
- Can be written once
- Can be overridden by a new decision (new entry, not modification)
- Requires audit trail for all changes
- Requires approver signature

### T2_SUPERVISED

**Used by**: Mobile  
**Meaning**: Read-only supervision, not authoritative  
**Properties**:
- Cannot write any data
- Is derivative from other contracts
- Used for real-time visibility only
- No long-term truth claim

---

## Mutation Policy Reference

| Policy | Write | Modify | Delete | Use Case |
|--------|-------|--------|--------|----------|
| **Immutable** | No | No | No | Tablet operations, ledger entries |
| **Write-Once** | Yes | No | No | PC governance decisions |
| **Append-Only** | Yes | No | No | Core ledger, control audit |
| **Capture-Only** | Yes | No | No | Tablet events, audit entries |
| **Read-Only** | No | No | No | Mobile supervision |

---

## Evidence Requirements

Every contract must provide **verifiable evidence** that it is honored:

### DC_TABLET_OPERATIONS Evidence

```json
{
  "evidence_type": "data_contract_validation",
  "contract_id": "DC_TABLET_OPERATIONS",
  "contracts_found": 5,
  "required_fields_present": true,
  "sample_transactions": [
    {
      "operation_id": "op_...",
      "is_immutable": true,
      "verified_at": "2026-05-12T10:00:00Z"
    }
  ]
}
```

### DC_PC_GOVERNANCE Evidence

```json
{
  "evidence_type": "data_contract_validation",
  "contract_id": "DC_PC_GOVERNANCE",
  "governance_decisions_found": 12,
  "all_signed": true,
  "audit_trail_complete": true
}
```

### DC_MOBILE_SUPERVISION Evidence

```json
{
  "evidence_type": "data_contract_validation",
  "contract_id": "DC_MOBILE_SUPERVISION",
  "read_only_enforced": true,
  "write_attempts": 0,
  "queries_logged": 234
}
```

### DC_CORE_LEDGER Evidence

```json
{
  "evidence_type": "ledger_integrity_check",
  "contract_id": "DC_CORE_LEDGER",
  "ledger_entries": 1247,
  "append_only_enforced": true,
  "hashes_verified": 1247,
  "hash_mismatches": 0
}
```

### DC_CONTROL_AUDIT Evidence

```json
{
  "evidence_type": "audit_trail_completeness",
  "contract_id": "DC_CONTROL_AUDIT",
  "audit_entries": 4892,
  "all_signed": true,
  "chronological_violations": 0
}
```

---

## Validation Hierarchy

When Phase 4 runs, it validates contracts in this order:

```
1. Q21: Data Contract Registry
   └─ Do all 5 contracts exist?
   └─ Are they defined correctly?

2. Q22: Evidence Ledger Integrity
   └─ Is the ledger append-only?
   └─ Do hashes match?

3. Q23: Freshness & Confidence
   └─ Is each contract recently verified?
   └─ How old is the evidence?

4. Q24: Schema Drift Guard
   └─ Have any schemas changed?
   └─ Do changes violate contracts?

5. Q25: Audit Trail Completeness
   └─ Is every action recorded?
   └─ Are all audit entries signed?
```

---

## References

- [Phase 4 Data Truth](./phase-4-data-truth.md)
- [Evidence Ledger Hardening](./evidence-ledger-hardening.md)
- [quality/data/data-contract-registry.json](../data/data-contract-registry.json)
