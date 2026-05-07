# PRISMA Mobile Future Edit Map

## Purpose

This file is the navigation map for future Codex and human edits to PRISMA Mobile/PWA. It points to the visual ownership boundaries for **PRISMA Crystal Command Mobile** without changing API, sync, cache, PWA, or business contracts.

## Main Visual Ownership

| Area | Owner file | Owns |
| --- | --- | --- |
| Mobile app shell, compact header, command card | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileDashboard.tsx` | Main pulse layout, brand header, primary metric, top KPI strip, loading/error shells |
| Premium navigation and tab surfaces | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobilePremiumNavigator.tsx` | Resumen/Caja/Alertas/Inventario/Sync routing inside the mobile dashboard |
| Decision command center | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileCommandCenter.tsx` | Owner decision queue, data quality summary, follow-up list |
| KPI cards | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileMetricCard.tsx` | Repeated KPI card shell only |
| Review-first panel | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobilePanels.tsx` | Quick actions, sales chart, cash, inventory, alerts, reports, branches panels |
| Action inbox | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileActionInbox.tsx` | Prioritized owner action inbox |
| Daily brief | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileDailyBrief.tsx` | Shareable executive brief |
| Decision ledger | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileDecisionLedger.tsx` | Auditable owner decision list |
| Pulse timeline | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobilePulseTimeline.tsx` | Operational timeline |
| Health radar | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobileHealthRadar.tsx` | Health score and axes |
| PWA install card/page | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobilePwaInstallCard.tsx` and `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\PrismaMobilePwaInstallPage.tsx` | Android/iOS PWA install guidance and WhatsApp install route surface |

## CSS Ownership

| CSS file | Visual zones |
| --- | --- |
| `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\app\prisma-mobile-pulse-binding.css` | App-level light Crystal binding, body/background color scheme, global mobile shell guards |
| `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\prisma-mobile-dashboard.module.css` | Crystal tokens, app shell, brand header, command card, KPI grid, review-first panel, dashboard states, responsive behavior |
| `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\prisma-mobile-pwa.module.css` | PWA install page/card, install guide, PWA states, install route responsive behavior |

## data-prisma-zone Registry

| Zone | Component/file | Purpose | Safe edits | Forbidden edits |
| --- | --- | --- | --- | --- |
| `mobile-app-shell` | `PrismaMobileDashboard.tsx` | Main Mobile/PWA surface boundary | Layout spacing, background tone, dashboard shell classes | Fetching, snapshot contract, cache behavior |
| `mobile-brand-header` | `PrismaMobileDashboard.tsx` | Compact PRISMA identity | Logo size, subtitle, status chip placement | Replacing business data with fake copy |
| `mobile-logo` | `PrismaMobileDashboard.tsx` | Logo image and compact mark | Image dimensions, local styling | PWA manifest icon contract |
| `mobile-status-chip` | `PrismaMobileDashboard.tsx` | Current health/readiness signal | Chip color, border, wording from existing values | Hard-coded health states |
| `mobile-command-card` | `PrismaMobileDashboard.tsx`, `PrismaMobileCommandCenter.tsx` | Main owner command card and deeper command center | Card hierarchy, compact metric presentation | Command model generation |
| `mobile-primary-metric` | `PrismaMobileDashboard.tsx` | Venta de hoy focus | Typography, spacing, context line | Sales calculation |
| `mobile-kpi-grid` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | KPI layout | Grid density, responsive columns | KPI data contract |
| `mobile-kpi-card` | `PrismaMobileDashboard.tsx`, `PrismaMobileMetricCard.tsx` | Repeated KPI card | Surface, value sizing, status accent | Metric labels or values unless data contract changes |
| `mobile-action-inbox` | `PrismaMobileActionInbox.tsx` | Prioritized action inbox | Card density, lane layout | Action ranking logic |
| `mobile-review-first` | `PrismaMobilePanels.tsx`, `PrismaMobileCommandCenter.tsx` | Que revisar primero | Order presentation, chip styling | Priority scoring and owners |
| `mobile-daily-brief` | `PrismaMobileDailyBrief.tsx` | Shareable daily brief | Share box styling, brief card density | WhatsApp/mail body generation |
| `mobile-decision-ledger` | `PrismaMobileDecisionLedger.tsx` | Decision audit trail | Timeline card styling | Ledger construction |
| `mobile-pulse-timeline` | `PrismaMobilePulseTimeline.tsx` | Pulse of the day | Timeline spacing and markers | Timeline event generation |
| `mobile-health-radar` | `PrismaMobileHealthRadar.tsx` | Health score and axes | Radar card styling, track colors | Health score calculation |
| `mobile-pwa-install` | `PrismaMobilePwaInstallCard.tsx`, `PrismaMobilePwaInstallPage.tsx` | PWA install surface | Install instructions layout, Android/iOS guide styling | Service worker, manifest, install event handlers |
| `mobile-offline-state` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | Offline/blocked readiness | Visible copy and danger styling | Hiding offline/errors |
| `mobile-sync-state` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | Source/sync/pending state | Sync chip layout and copy derived from data | Sync/outbox/event contracts |
| `mobile-error-state` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | Error and warning visibility | Error panel spacing, retry button styling | Suppressing errors |
| `mobile-empty-state` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | Empty readiness | Empty-state guidance presentation | Fake placeholder business data |
| `mobile-loading-state` | `PrismaMobileDashboard.tsx` | Loading shell | Skeleton shape and copy | Layout jump caused by loading |
| `mobile-success-state` | `PrismaMobileDashboard.tsx`, `PrismaMobilePremiumNavigator.tsx` | Ready state | Success styling and green accents | False success when data is stale/failed |

## How To Change Common Things Later

- Change logo size: edit `.brandLogo` and `.brandLogo img` in `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\components\prisma-app\prisma-mobile-dashboard.module.css`.
- Change background tone: edit the token block under `PRISMA Crystal Command Mobile: tokens` in `prisma-mobile-dashboard.module.css`.
- Change KPI card look: edit `.commandSecondaryGrid article` and `.metricCard` in `prisma-mobile-dashboard.module.css`.
- Change "Que revisar primero": edit the presentation in `PrismaMobilePanels.tsx` and the visual styles under `PRISMA Crystal Command Mobile: review-first panel`.
- Change status chips: edit `.statusChip`, `.healthOk`, `.healthReview`, `.healthUrgent`, and `.healthOffline`.
- Change PWA install card: edit `PrismaMobilePwaInstallCard.tsx` for visible instructions and `prisma-mobile-pwa.module.css` for the install surface.
- Adjust mobile spacing: edit the `max-width: 860px` and `max-width: 520px` responsive sections in `prisma-mobile-dashboard.module.css`.
- Adjust desktop preview width: edit `.dashboardShell` width in `prisma-mobile-dashboard.module.css`.

## Do Not Touch

- API calls.
- Data fetching contracts.
- Sync, outbox, and event contracts.
- Service worker behavior.
- PWA install behavior.
- Business logic.
- KPI calculations.
- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared-kernel`.
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc`.
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet`.

## Validation Checklist

- Run `pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run typecheck`.
- Run `pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run build`.
- Run `pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run check:all` if time allows.
- Run `node F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\tools\verify_prisma_mobile_future_edit_map.mjs` from the mobile app root.
- Screenshot 390x844, 430x932, 768x1024, and 1366x900 when browser tooling is available.
- Confirm no horizontal overflow.
- Confirm important `data-prisma-zone` markers are present.
- Smoke public URLs: Tablet, PC, Mobile, Mobile install, and EIT.
