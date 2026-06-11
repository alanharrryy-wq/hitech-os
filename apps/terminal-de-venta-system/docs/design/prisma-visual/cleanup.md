# Cleanup

This is not a bulk edit list. It is cleanup order and risk.

## First cleanup order

1. `/pos` and `/checkout`: highest obstruction + operational risk.
2. `/sync`: high panel/background obstruction from sync panel.
3. `/catalog`, `/stock`, `/inventory`: medium-high evidence, important business screens.
4. `/settings/license`, `/release-gate`, `/offline`: validate carefully, do not flatten gate states blindly.
5. Visual OS / Pulse: no-touch unless explicitly scoped.

## Top files to review

| Path | Blocking | Risk | Status |
|---|---|---|---|
| products/tablet/app/components/pos/pos.module.css | 28 | high | candidate |
| products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css | 14 | high | candidate |
| products/tablet/app/components/sync/pending-offline-sync-panel.module.css | 10 | high | candidate |
| products/tablet/app/app/prisma-tablet-light-premium-final.css | 9 | medium | candidate |
| products/tablet/app/components/prisma-dark-pos/prisma-dark-pos.module.css | 9 | medium | candidate |
| products/tablet/app/app/globals.css | 7 | medium | candidate |
| products/tablet/app/components/tablet-home/tablet-home.module.css | 7 | medium | candidate |
| products/tablet/app/components/tablet-pos/touch-pos.module.css | 5 | medium | candidate |
| products/tablet/app/app/prisma-tablet-light-shell.module.css | 3 | medium | candidate |
| products/tablet/app/app/checkout/prisma-checkout-light-safe-shell.module.css | 3 | medium | candidate |
| products/tablet/app/app/pos/prisma-pos-light-safe-shell.module.css | 3 | medium | candidate |
| products/tablet/app/components/shift/shift-cash-closure.module.css | 3 | medium | candidate |
| products/tablet/app/components/catalog/catalog.module.css | 2 | low | candidate |
| products/tablet/app/components/license/license-ui.module.css | 2 | low | candidate |
| products/tablet/app/components/offline/offline-export-audit.module.css | 2 | low | candidate |
| products/tablet/app/components/reports/contextual-export.module.css | 2 | low | candidate |
| products/tablet/app/components/sales/sales.module.css | 2 | low | candidate |
| products/tablet/app/app/prisma-pulse/prisma-tablet-pulse.module.css | 1 | low | blocked-no-touch |
| products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css | 1 | low | blocked-no-touch |
| products/tablet/app/components/pos/pos.visual.tokens.generated.css | 1 | low | candidate |

## Cleanup rule

Do not transparentar globally. Every change must target a route/component and preserve legibility.
