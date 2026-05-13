# Evidence Ledger Hardening — Phase 4

## Overview

The Evidence Ledger is PRISMA's **immutable record of all quality gates**.

Phase 4 hardens the ledger against:

- Corruption
- Truncation
- Deletion
- Modification
- Tampering

---

## Ledger Structure

### File: `QUALITY_EVIDENCE_LEDGER.jsonl`

A **JSON Lines** file where each line is an immutable ledger entry.

```jsonl
{"evidenceId":"Q21_data_contract_registry_0","gateId":"Q21","type":"data_contract_validation","path":"evidence/Q21_data_contract_registry_0.json","sha256":"abc123...","summary":"5/5 contracts valid"}
{"evidenceId":"Q22_ledger_integrity_0","gateId":"Q22","type":"ledger_integrity_check","path":"evidence/Q22_ledger_integrity_0.json","sha256":"def456...","summary":"Ledger valid, no truncation"}
```

### Properties

- **evidenceId**: Unique identifier for this evidence
- **gateId**: Which gate produced this evidence
- **type**: Evidence category (e.g., `data_contract_validation`, `audit_trail_check`)
- **path**: Relative path to the full evidence JSON file
- **sha256**: SHA256 hash of the full evidence payload
- **summary**: Human-readable one-liner

---

## Hardening Rules

### Rule 1: Append-Only

✅ **ALLOWED**:
```bash
echo '{"evidenceId":"Q25_audit_trail_0",...}' >> QUALITY_EVIDENCE_LEDGER.jsonl
```

❌ **FORBIDDEN**:
```bash
sed -i '1d' QUALITY_EVIDENCE_LEDGER.jsonl    # Delete line
sed -i '1s/.*/new line/' ...                 # Modify line
rm QUALITY_EVIDENCE_LEDGER.jsonl             # Delete file
```

### Rule 2: Chronological Order

Every entry must have a timestamp in its payload that is >= the previous entry's timestamp.

Q22 validates this during each run.

### Rule 3: No Entry Deletion

Once an entry exists in the ledger, it **cannot be removed**.

If evidence is withdrawn, it must be marked `WITHDRAWN` in the evidence file itself, but the ledger entry persists.

### Rule 4: Cryptographic Hashing

Each ledger entry includes the SHA256 of its corresponding evidence file.

Q22 re-calculates these hashes to detect tampering.

### Rule 5: Immutable Path Reference

The `path` field points to the evidence file location and **must never change**.

If evidence files are moved or reorganized, the ledger path references become stale.

---

## Evidence File Format

### Location: `evidence/{evidenceId}.json`

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
    "contracts": [
      {
        "contractId": "DC_TABLET_OPERATIONS",
        "layer": "Tablet",
        "status": "ACTIVE",
        "evidence_count": 1,
        "last_verified": "2026-05-12T09:00:00Z"
      }
    ]
  }
}
```

### Properties

- **schemaVersion**: Always "1.0"
- **runId**: Unique identifier for this quality run
- **evidenceId**: Same as ledger entry
- **gateId**: Which gate produced this
- **type**: Category
- **summary**: One-liner for humans
- **createdAt**: ISO 8601 timestamp
- **payload**: Gate-specific data (varies by evidence type)

---

## Redaction

All evidence is **automatically redacted** before writing:

### Redacted Patterns

- API keys: `REDACTED_API_KEY`
- Secrets: `REDACTED_SECRET`
- Personal data: `REDACTED_PII`
- Database credentials: `REDACTED_DB_URL`
- Internal IPs: `REDACTED_IP`
- Session tokens: `REDACTED_TOKEN`

### Example

**Before**:
```json
{
  "database_url": "postgresql://user:secretpass@internal.db:5432/prisma",
  "api_key": "sk_live_abc123xyz789..."
}
```

**After**:
```json
{
  "database_url": "REDACTED_DB_URL",
  "api_key": "REDACTED_SECRET"
}
```

---

## Ledger Validation (Q22)

Q22 runs these checks every time:

### Check 1: Ledger File Exists

```bash
✓ QUALITY_EVIDENCE_LEDGER.jsonl exists
```

### Check 2: File Not Truncated

```bash
✓ Line count = 25 entries
✓ Last entry is complete JSON (not cut off)
```

### Check 3: Chronological Order

```bash
✓ All timestamps are in ascending order
✓ No future-dated entries
```

### Check 4: Hash Verification

For each entry:

```bash
sha256(evidence_file) == entry.sha256
```

### Check 5: No Duplicate IDs

```bash
✓ Each evidenceId is unique
```

### Check 6: All References Valid

For each entry:

```bash
✓ evidence/{evidenceId}.json exists
✓ evidenceId in file matches ledger entry
✓ gateId in file matches ledger entry
```

---

## Failure Scenarios

### Ledger Truncation

**Symptom**: Last entry is incomplete JSON or is missing the final newline.

**Severity**: S0 BLOCKED

**Fix**: Restore from backup. Do not attempt to repair manually.

### Hash Mismatch

**Symptom**: `sha256(evidence_file) != entry.sha256`

**Severity**: S1 BLOCKED

**Cause**: Evidence file was modified after creation.

**Fix**: Restore evidence file from backup.

### Missing Entry

**Symptom**: Ledger references evidence file that does not exist.

**Severity**: S1 BLOCKED

**Cause**: Evidence file was deleted or moved without updating ledger.

**Fix**: Restore evidence file or remove ledger entry manually (requires operator approval).

### Chronology Violation

**Symptom**: Entry N has timestamp < Entry N-1

**Severity**: S1 BLOCKED

**Cause**: Entries were reordered or an entry was inserted out of order.

**Fix**: Restore from backup.

---

## Usage

### Check Ledger Health

```bash
pnpm quality:audit
```

This runs Q22 and Q25 specifically, checking ledger integrity and audit trail completeness.

### View Ledger

```bash
cat QUALITY_EVIDENCE_LEDGER.jsonl | jq .
```

### Query by Gate

```bash
grep '"gateId":"Q21"' QUALITY_EVIDENCE_LEDGER.jsonl
```

### Count Entries

```bash
wc -l QUALITY_EVIDENCE_LEDGER.jsonl
```

---

## References

- [Phase 4 Data Truth](./phase-4-data-truth.md)
- [Data Contract Model](./data-contract-model.md)
- [Evidence Ledger Policy](../policies/evidence-ledger-policy.json)
