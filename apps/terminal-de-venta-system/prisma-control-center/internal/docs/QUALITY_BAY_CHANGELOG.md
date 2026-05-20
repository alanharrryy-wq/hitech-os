# PRISMA Control Center · Quality Bay V1

## Added

- Independent **Quality Bay** interface selected from the top Control Center bar.
- Premium command-tile UX for PRISMA Quality profiles.
- Local Quality API under `/api/quality/*`.
- Evidence summary panel, findings panel, install strip, and latest-run ledger.
- External `quality_bay.css` and `quality_bay.js` assets, compatible with current CSP.

## Preserved

- Existing operation cockpit remains available as **Operación**.
- Quality remains a CLI engine; the UI only wraps it safely.
- Tablet independence and PRISMA operating rule remain intact.

## Runtime behavior

- The API resolves repo root as the parent of `prisma-control-center`.
- The API expects `quality` as a sibling folder.
- Windows evidence output defaults to `F:\descargasf`.
- Non-Windows test environments use `_quality_out` or `PRISMA_QUALITY_OUT_DIR`.
