# PRISMA Quality Operating System

Phase 5: Release, Operator Readiness & Automation Hardening.

This folder is the local-first quality governor for PRISMA. It validates architecture boundaries, contracts, evidence, reportability, data truth, release readiness, and automation claims without requiring Cloudflare or destructive database access.

Core rule:

```text
Tablet opera.
PC gobierna.
Mobile supervisa.
Core registra.
Control audita.
Cloudflare acompana, no manda.
```

Outputs are written to `F:\descargasf\PRISMA_QUALITY_OS_<runId>` by default.

## Main commands

```powershell
node quality/bin/prisma-quality.mjs --self-test --repo-root .
node quality/bin/prisma-quality.mjs --profile phase5 --repo-root . --out-dir "F:\descargasf"
node quality/bin/prisma-quality.mjs --profile release --repo-root . --out-dir "F:\descargasf"
node quality/bin/prisma-quality.mjs --list-profiles --repo-root .
```

## What changed in this hardened bundle

- Canonical gate result normalization.
- Phase 5 blockers/warnings become real findings.
- JSON outputs are parseable by machine consumers.
- `--repo-root` is respected by Phase 5 gates.
- Q31 validates the 100-item automation improvement catalog.
- Reports include machine summary, run manifest, profile matrix, normalization audit, output validation, and next actions.


## v5.3 install-safe calibration

Installer verification now separates quality package health from full repo release readiness. Use `--strict-phase5` to make external repo Phase 5 blockers rollback the install.
