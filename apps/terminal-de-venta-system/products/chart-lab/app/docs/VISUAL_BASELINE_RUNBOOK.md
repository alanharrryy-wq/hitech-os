# Visual Baseline Runbook

Status: active, not mandatory yet

Visual baselines come after contracts and adapters. Do not use screenshots to compensate for missing data truth.

Preconditions:

- chart data registry exists.
- sourceMode labels are verified.
- promotion readiness verifier passes.
- no chart required for baseline is still mock-only unless the screenshot is explicitly marked mock.
- sourceMode, freshness and confidence are visible or available in the rendered metadata.

Readiness check:

```powershell
pnpm -C products/chart-lab/app visual-baseline-readiness
```

Output screenshots and ZIPs must go under F:\descargasf or tools\_local\evidence, not src.
