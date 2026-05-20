# PRISMA Customer Assurance Layer

Purpose: turn `quality` into the customer-facing assurance layer for demos, installs, support, upgrades, drift watch, and evidence.

This layer is read-only. It does not sell, sync, migrate, mutate a real database, start required services, or make PC/Mobile/Cloudflare mandatory.

Canonical operating rule:

```text
Tablet operates and sells alone.
PC governs if present.
Mobile supervises.
Shared/Core records and validates contracts.
Control audits.
Quality certifies with evidence.
```

Customer Assurance adds these profiles:

- `client-readiness`: full customer promotion gate.
- `demo`: demo/training isolation and redaction proof.
- `first-run`: first customer machine readiness.
- `support-pack`: support export manifest and redaction proof.
- `upgrade`: backup, rollback, and migration safety.
- `pilot`: one-pass pilot-site readiness.

Run example:

```powershell
node quality/bin/prisma-quality.mjs --profile client-readiness --repo-root . --out-dir F:\descargasf
```

Outputs stay in `F:\descargasf\PRISMA_QUALITY_OS_*`.
