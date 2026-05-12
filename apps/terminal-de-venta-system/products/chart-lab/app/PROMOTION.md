# PRISMA Chart Lab Promotion Guide

Chart Lab is the staging workshop. Product apps remain the operational owners. The local workshop URL is `http://localhost:3000`.

## Product ownership

| Target | Role | Promotion rule |
|---|---|---|
| PC | Governs | Promote governance, audit, dependency, risk, and decision visuals. |
| Tablet | Operates | Promote only immediate operator continuity visuals. |
| Mobile | Supervises | Promote compact, read-only owner supervision visuals. |
| Web | General surface | Promote marketing/public-safe or neutral operational visuals. |
| Control | Audits | Promote evidence, traceability, status, and history visuals only. |

## Files by responsibility

| Layer | Belongs in |
|---|---|
| Shared chart contract | `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\prisma-charts` |
| Shared mock or deterministic fallback | `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\prisma-charts` or lab-local mock during design |
| Lab-only component | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts` |
| Product wrapper | Target product app, for example PC / Tablet / Mobile |
| Real data adapter | Server/API/shared adapter for the target product |
| Documentation | Chart passport, Chart Lab docs, product surface docs |

## Promotion flow

1. Finish the visual in Chart Lab using explicit mock data.
2. Add or confirm the shared contract.
3. Add a safe adapter for real data, server-side when needed.
4. Move only the reusable visual core or option builder into shared code.
5. Add a product wrapper in PC, Tablet, Mobile, Web, or Control.
6. Keep product feature flags off by default unless that product already has a preview mechanism.
7. Run Chart Lab verification and target product validation.

Do not paste the entire lab shell into a product app. The lab is a workshop, not a runtime dependency for operating surfaces.

## Chart Promotion Bridge

Dry-run:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=pc.causal-flow-ribbon --target=pc --dry-run
```

The bridge writes evidence under `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\_local\evidence\chart-lab`.

Apply is blocked by default until a product-wrapper file and feature flag are explicitly approved. This preserves:

- Tablet operates.
- PC governs.
- Mobile supervises.
- Core records.
- Control audits.

## Cloudflare note

Cloudflare Pages and Tunnel are configured as preview-only, public-safe paths. Do not route Chart Lab through existing Mobile or Control origins.
