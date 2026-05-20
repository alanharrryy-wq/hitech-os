# Support Pack

`support-pack` produces a customer-safe evidence run directory and a `CUSTOMER_SUPPORT_PACK_MANIFEST.json`.

What to send to support:

- Zip the full `F:\descargasf\PRISMA_QUALITY_OS_*` run directory.
- Include the manifest, reports, evidence, summaries, checksums, and command logs.
- Do not include raw databases, full `.env` files, customer PII exports, node_modules, or build folders.

Run:

```powershell
node quality/bin/prisma-quality.mjs --profile support-pack --repo-root . --out-dir F:\descargasf
```
