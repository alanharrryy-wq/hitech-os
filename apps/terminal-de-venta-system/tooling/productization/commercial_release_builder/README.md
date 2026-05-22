# PRISMA Commercial Release Builder 01 Fixed

Builds customer-facing PRISMA Commerce release packages from the dev repo without shipping the raw repo.

## Prime directive

Tablet operates and sells alone. PC, Mobile, Remote Care, cloud, internet, and canonical DB must never become required for Tablet sale, payment, shift close, offline operation, or startup.

## Fixes in this version

- Excludes legacy `tablet-pc-required` fixture paths from commercial packages.
- Uses external temporary work folders so `_staging` is not included in final commercial release ZIP.
- Keeps evidence ZIP light by writing release packages to `ReleaseOutRoot`, not into the evidence bundle.

## Run

```powershell
py -3 tooling\productization\commercial_release_builder\commercial_release_builder.py --repo-root F:epos\hitech-ospps	erminal-de-venta-system --out-root F:\descargasf\PRISMA_COMMERCIAL_RELEASES
```
