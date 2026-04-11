# Contract / Python Sync Guide

This guide explains the narrow contract-to-Python synchronization guard introduced by this remediation.

## Why this matters

The repository already contains:
- generated contract schemas under `packages/contracts/schemas/generated/`
- a `python-sync-map.json` describing the intended Python-side mapping
- Python models in `services/ai-agent/app/models.py`

That is enough structure for drift to become visible, but without a cheap dedicated check it can still slip through review.

## New check

This remediation adds:

```text
tools/scripts/check_contract_python_parity.py
```

The checker focuses on the generated sync map and Python model presence.

## What it validates

At a conservative level, the checker verifies:
- the generated sync map exists
- referenced schema files exist
- the referenced Python model file exists
- the referenced Python model class names appear in the target file
- the contract-side schema inventory is readable

This is intentionally narrow. It is not a full schema-equivalence theorem prover.

## Why the check is conservative

A stronger semantic validator would require a deeper, more opinionated comparison across TypeScript contracts, generated schemas, and Pydantic models. That is possible later, but this first guard aims to catch obvious drift cheaply and deterministically.

## How to run it

From repo root:

```powershell
py tools/scripts/check_contract_python_parity.py --repo-root . --strict
```

If your `py` launcher is not available:

```powershell
python tools/scripts/check_contract_python_parity.py --repo-root . --strict
```

## CI integration

This remediation also adds a narrow workflow:

```text
.github/workflows/contract-python-parity.yml
```

The workflow runs the same script so contract/Python mapping drift becomes more visible during automation.
