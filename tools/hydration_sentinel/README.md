# Hydration Sentinel

Guardrail de hydration para HITECH-OS.

## Scripts

- `pnpm hydration:scan`
- `pnpm hydration:scan:strict`
- `pnpm hydration:baseline:update`

## Salidas

- `_reports/hydration_sentinel/hydration_sentinel_report.md`
- `_reports/hydration_sentinel/hydration_sentinel_summary.json`
- `_reports/hydration_sentinel/hydration_sentinel_findings.json`
- `_reports/hydration_sentinel/hydration_sentinel_recommendations.json`

## Qué detecta

- `dynamic(..., { ssr:false })`
- `suppressHydrationWarning`
- browser APIs en archivos sin `'use client'`
- `'use client'` en `page/layout/template`
- imports relativos hacia archivos client como hint de revisión
- firmas típicas de mutación externa antes de hydration

## Notas

- Excluye por default tests, generated, codex runs/worktrees y carpetas de output para bajar ruido.
- `server_to_client_import_hint` es solo hint. En Next puede ser válido.
- Usa `baseline.json` para congelar findings conocidos y enfocarte en regresiones.
