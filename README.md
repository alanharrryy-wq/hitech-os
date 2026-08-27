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

## Multi-app local run (Keystone + Operator + Forms)

Ports:
- Keystone: `http://127.0.0.1:3100`
- Operator UI (`external_interaction_template`): `http://127.0.0.1:3110`
- Public Forms (`external_interaction_forms`): `http://127.0.0.1:3200`

Commands:
```powershell
pnpm run dev:keystone
pnpm run dev:operator
pnpm run dev:forms
pnpm run dev:multi-app
```

Production URL targets:
- Keystone: `https://engine.hitechrts.com`
- Forms: `https://forms.hitechrts.com`
- Operator UI: keep private/non-public unless explicitly protected

Cloudflare multi-host setup command:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/infra/cloudflare/setup_tunnel_forever.ps1
```

## PRISMA Chart Lab

The dedicated PRISMA Chart Lab runs locally on port `3000` as a visual workshop for ECharts-based operational charts.

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" install
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:dev
```

Open `http://localhost:3000`.

Cloudflare is not configured for Chart Lab yet. Treat it as a local workshop unless a separate public-safe preview route is explicitly added.

## Source code license

Current HITECH-authored PRISMA / HITECH OS source is governed by the proprietary root [`LICENSE`](./LICENSE), subject to the historical Apache 2.0 boundary and third-party license exceptions documented in [`PRISMA_SOURCE_CODE_LICENSING_POLICY.md`](./apps/terminal-de-venta-system/docs/productization/PRISMA_SOURCE_CODE_LICENSING_POLICY.md).

The historical public baseline through commit `615d6732fd733696a60bb549bc88b23c0b573de4` was previously made available under Apache License 2.0. The proprietary cutover does not revoke rights validly granted for those historical versions. Third-party components remain governed by their respective licenses and notices.
