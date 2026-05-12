# PRISMA Chart Real Data Source Map

Run date: 2026-05-11
Policy: real data must come through server/API/adapters, never client-side database access.

## Source Classification

- `safe`: existing server/API/view-model source can feed the chart without exposing secrets or inventing backend contracts.
- `partial`: some real fields exist, but the chart still needs fallback for missing dimensions.
- `unavailable`: no safe source exists yet.
- `unsafe`: source would require client DB access, secrets, or unrelated backend redesign.

## Chart Map

| Chart | Intended question | Candidate real source | Safety | Adapter plan | Missing gaps | Fallback |
|---|---|---|---|---|---|---|
| `pc.causal-flow-ribbon` | What causes are producing operational effects and actions? | PC dashboard sync summary plus `shared/tri-db/status.latest.json` | partial | Build ribbons from pending/failed/conflict sync and bridge parity warnings. | No canonical incident causality table yet. | Mock ribbons remain for richer cause/effect examples. |
| `pc.operational-density-field` | Where is pressure concentrated by module/time? | PC dashboard sync summary, bridge status generated time, table counts | partial | Build density cells from real module summaries and mark missing time buckets as fallback. | No canonical time-bucket event density API yet. | Deterministic mock fills visual density. |
| `pc.service-dependency-graph` | Which apps/services depend on which operational sources? | Sanitized bridge status roots plus PC/Tablet/Mobile/Control route metadata | partial | Build graph nodes from known local ports and bridge DB paths; statuses from bridge/dashboard availability. | No live probe service is called from charts. | Mock graph remains for unavailable live health. |
| `pc.inventory-risk-treemap` | Which inventory areas create continuity or money risk? | `getBackofficeDashboard()` top SKUs and low-stock KPI from canonical Prisma | partial | Convert top SKUs and low-stock KPI into risk nodes. | No per-SKU days-cover/revenue-risk source in dashboard yet. | Mock treemap remains when top SKU source is empty. |
| `pc.decision-ledger-timeline` | What decisions/evidence/incidents happened over time? | PC dashboard meta warnings, sync status, bridge status timestamps | partial | Build timeline from generated dashboard/sync events and bridge status. | No canonical decision ledger table exposed to PC page yet. | Mock decision ledger remains for richer audit examples. |
| `pc.financial-operational-waterfall` | How do operations affect net money? | `getBackofficeDashboard()` KPI values and top SKUs | partial | Parse real sales/ticket/low-stock/cancellation KPIs into waterfall steps. | Discounts, refunds, shrink, and cost model incomplete. | Mock steps remain for unavailable financial dimensions. |
| `tablet.shift-pulse-strip` | Can the Tablet keep operating this shift? | `getTabletRuntimeSnapshot()` local sales/outbox/catalog state | safe | Convert runtime snapshot sales and connection state into operational buckets. | No historical bucket endpoint yet. | Mock buckets remain for time-series shape beyond current snapshot. |
| `tablet.sync-outbox-status-matrix` | What local outbox work needs attention now? | Tablet runtime snapshot and pending sync/outbox summaries | safe | Convert pending/failed/conflict counts into matrix cells. | Item-type breakdown requires deeper outbox query. | Mock matrix remains for item-type distribution. |
| `mobile.owner-pulse-timeline` | Is the operation improving or degrading recently? | `/api/mobile/snapshot` data-plane snapshot via `loadMobileDataPlaneState()` and intelligence snapshot | partial | Convert timeline and health score to owner pulse points. | Historical owner pulse beyond current snapshot is limited. | Mock timeline remains when snapshot has insufficient points. |
| `mobile.action-inbox-priority-stack` | Who owns the most urgent open actions? | Mobile snapshot `actionInbox.items` | safe | Group real action inbox items by owner/priority. | None for current open action grouping. | Empty state or deterministic fallback if no actions. |
| `mobile.health-radar-compact` | Which health dimension is weak and why? | Mobile snapshot `healthRadar.dimensions` | safe | Map real health dimensions to six compact radar axes. | Full 10-axis radar is compacted to chart contract’s six axes. | Unknown dimensions become low-confidence/partial, not fake. |
| `mobile.freshness-beacon-grid` | Which source is fresh, stale, offline, or unknown? | Mobile snapshot `dataQuality.sources` and `meta` | safe | Map source statuses into freshness beacons. | TTL is inferred from source freshness and chart defaults. | Unknown source gets `unknown` state. |
| `mobile.incident-spark-cards` | Which incidents have active microtrends? | Mobile snapshot `alertCenter.alerts` and `timeline` | partial | Convert alerts/timeline into incident cards with evidence counts. | True multi-point incident trend history is limited. | Mock spark cards remain if no alert/timeline points exist. |
| `mobile.confidence-meter-bands` | Why can/cannot the owner trust the snapshot? | Mobile snapshot `dataQuality` and `meta.confidence` | safe | Build bands from completeness, recency, consistency, evidence, and coverage. | Evidence dimension is a derived proxy from alerts/actions. | Partial band metadata explains proxy. |

## Wiring Rule

Every chart receives an adapter result with quality metadata. If real source coverage is incomplete, the adapter may blend safe real values with deterministic fallback only when it marks the chart as `partial` or `mock` and explains why. No chart may label fallback data as real.

## Chart Lab Source Map

The machine-readable Lab source map is:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\maps\chart-lab-maps.ts`

Verify it with:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:maps
```
