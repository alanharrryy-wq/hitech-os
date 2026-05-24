# PC UI/UX Governance

Generated: 2026-05-23T21:39:40

This folder contains the minimum governance layer for PRISMA PC UI/UX simplification.

## Files

- `page-contracts.ts`: every PC page classified with human intent.
- `route-map.ts`: route classification for primary, secondary, lab and internal pages.
- `copy-dictionary.ts`: shared human terms for status and technical translations.
- `status-translator.ts`: helper functions to translate technical state into human-facing UI labels.
- `pc-uiux-baseline.json`: no-downgrade baseline.

## Current route count

`55`

## Rule

Visible PC UI should be human-first. Technical language belongs inside evidence, diagnostics or internal docs.
