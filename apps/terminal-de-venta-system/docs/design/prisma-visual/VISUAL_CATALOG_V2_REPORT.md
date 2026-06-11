# VISUAL_CATALOG_V2_REPORT

Schema: prisma-visual-catalog-governed-v2
Components: 43
Status counts: {"live":13,"mapped":22,"reserved":7,"deprecated":1}

## Surfaces
| surface | status | role | recipes |
| --- | --- | --- | --- |
| tablet | current | standalone POS / venta táctil | tablet-cloudglass-light, glass-pill, surface-panel, product-commerce |
| pc | current | backoffice/admin/análisis | pc-graphite-glass, data-panel, metric-card, command-panel |
| mobile | current | companion/pulse/alertas | mobile-mist, state-banner, metric-card |
| chart-lab | current | experimental/lab visual | chart-lab-analysis, liquid-panel |
| shared-ui | current | shared component and token authority | shared-ui-foundation, surface-panel, glass-card, action-button |
| visual-os | current | Visual OS recipes, scorecards and release gates | visual-os-governance |
| surface-governor | current | surface policy and promotion authority | surface-governor-policy |
| kiosk | reserved | reserved kiosk surface | reserved-safe-display |
| customer-display | reserved | reserved customer-display surface | reserved-safe-display |
| warehouse-scanner | reserved | reserved warehouse-scanner surface | reserved-safe-display |
| manager-console | reserved | reserved manager-console surface | reserved-safe-display |
| training-mode | reserved | reserved training-mode surface | reserved-safe-display |
| demo-mode | reserved | reserved demo-mode surface | reserved-safe-display |
| public-display | reserved | reserved public-display surface | reserved-safe-display |

## Decision authority
- surface-adapters.json selects role, density, libraries, backgrounds and migration policy.
- domain-contracts.json selects domain components and recipes.
- component-variants.json constrains component usage per surface.
- generator-contracts.json keeps generation dry-run safe by default.
