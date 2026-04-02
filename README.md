# HITECH OS 12 — Tables as Law (JSON Canon)

**Generated:** 2026-03-01T12:00:00 (America/Mexico_City)

This bundle turns constitution tables into **versioned, validated, machine-executable JSON contracts**.

## What's inside
- `docs/constitution/tables/*.json` — canonical tables (source of truth)
- `docs/constitution/tables/_schema/table_spec.schema.json` — JSON Schema that validates all tables
- `tools/hos/constitution/validate_tables.py` — validator CLI (schema + invariants)
- `scripts/constitution_check.ps1` — Windows wrapper (PowerShell) to run the validator

## Quick run
### Python
```bash
python tools/hos/constitution/validate_tables.py --root .
```

### PowerShell
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/constitution_check.ps1 -RepoRoot "F:\repos\hitech-os"
```

## Design rules (hard)
- Every table must have: `table_id`, `version`, `status`, `authority_level`, `scope`, `columns`, `rows`, `change_policy`
- `table_id` must start with `TBL_`
- `version` must be semver `X.Y.Z`
- Columns must have unique names
- Enum columns must declare `enum_values`
- Rows must contain only declared columns (no extras)
- Required columns must exist in every row (unless `row_defaults` provides them)

## Tables included
- `TBL_TOKENS_TAXONOMY`
- `TBL_GOVERNANCE_SCALE`
- `TBL_DASHBOARD_STRUCTURE`
- `TBL_VRT_POLICY`

## External Interaction Template

A new sibling web template is available at:

- `apps/external_interaction_template`

Purpose:

- external collect/review/update/approve/dispatch/sync flows
- schema-driven and domain-neutral
- companion surface for external actors while desktop templates remain unchanged
