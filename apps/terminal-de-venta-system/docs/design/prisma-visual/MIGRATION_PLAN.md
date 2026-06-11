# MIGRATION_PLAN

Migration is tiered and route-based. No production route was rewritten by this pass.

| surface | route | tier | complexity | confidence | nextAction |
| --- | --- | --- | --- | --- | --- |
| tablet | /prisma-visual-catalog | tier-1-wrapper | low | 0.72 | visual-evidence-next; then migrate existing low-risk route |
| tablet | / | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /catalog | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /events/outbox | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /existencias | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /inventory | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /inventory/low-stock | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /offline | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /prisma-dark-pos-reference | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |
| tablet | /prisma-pulse | tier-1-wrapper | medium | 0.72 | eligible-for-catalog-migration-after-visual-review |

## Blocked
| surface | route | reason |
| --- | --- | --- |
| tablet | /checkout | noTouch or high layer risk |
| tablet | /pos | noTouch or high layer risk |
| tablet | /settings/license | noTouch or high layer risk |
| pc | /license-runtime | noTouch or high layer risk |
| pc | /settings/license | noTouch or high layer risk |
