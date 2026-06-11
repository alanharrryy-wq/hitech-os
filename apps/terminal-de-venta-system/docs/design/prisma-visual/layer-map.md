# Layer Map

Tablet layer map is the cleanup compass.

## Source summary

- Routes mapped: `35`
- Layers detected: `3303`
- Files analyzed: `431`
- Background references: `51`

## Layer counts

| Type | Count |
|---|---|
| unknown | 1397 |
| panel | 664 |
| card | 348 |
| shell | 293 |
| navigation | 262 |
| viewport | 144 |
| background | 52 |
| page-surface | 46 |
| state | 46 |
| fx | 45 |
| overlay | 3 |
| grain | 2 |
| scrim | 1 |

## Top blocking routes from layer map

| Route | Blocking layers |
|---|---|
| unknown | 46 |
| /pos;/checkout | 29 |
| * | 14 |
| /sync | 10 |
| /settings/export | 5 |
| /shift | 3 |
| /catalog;/stock | 2 |
| /settings/license | 2 |
| /offline | 2 |
| /sales/today;/sales/history | 2 |
| /returns | 1 |

## Top obstruction routes from Visual QA

| Route | Candidates |
|---|---|
| /checkout | 113 |
| /pos | 113 |
| /screen-standard-preview | 98 |
| /prisma-dark-pos-reference | 65 |
| /settings/data | 53 |
| /settings/license | 53 |
| /sync | 52 |
| /inventory | 46 |
| /stock | 46 |
| /existencias | 45 |
| /catalog | 44 |
| /shift | 40 |

## Budget rule

Each critical route gets a layer budget in `maps/layer-budget.json`. `/pos` and `/checkout` are first because they have both layer-map blockers and Visual QA obstruction candidates.
