# Promotion Readiness

Status: active

Promotion Bridge must stay dry-run first and apply-blocked by default.

Readiness checks:

- 14 ChartOps charts are listed.
- Each chart has data source metadata.
- mock charts are never treated as live-real.
- feature flags default to false/off.
- rollback manifest path exists in the promotion plan.
- dry-run commands exist.
- target surface matches product law.

Verification:

```powershell
pnpm -C products/chart-lab/app verify:promotion-readiness
```
