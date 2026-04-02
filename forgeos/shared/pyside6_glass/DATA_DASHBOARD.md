# Data and Dashboard Subsystem

This document describes the neutral provider-based dashboard architecture in `pyside6_glass`.

## Goals

- Keep data retrieval separate from dashboard rendering.
- Stay framework-neutral (no product-specific schema).
- Make local development practical with deterministic built-ins.
- Provide extension points for future file, SQLite, service or integration-backed providers.

## Core contracts

Location: `forgeos/shared/pyside6_glass/data.py`

- `DataState`: loading/ready/empty/error/stale
- `RefreshPolicy`: manual vs polling behavior and stale window metadata
- `DataQuery`: provider/query/request envelope for dashboard data fetches
- `DataResult`: normalized response envelope with metrics/rows/feed/payload/diagnostics
- `DataProviderMeta`: provider identity + capabilities metadata
- `DashboardDataProvider`: protocol for provider implementations

Registry APIs:

- `register_data_provider(...)`
- `get_data_provider(...)`
- `list_data_providers()`
- `execute_data_query(...)`
- `data_provider_diagnostics(...)`
- `describe_data_provider(...)`

## Built-in providers

Location: `forgeos/shared/pyside6_glass/data_providers.py`

- `InMemoryDashboardProvider` (`builtin.mock_dashboard`)
- `LocalSQLiteDashboardProvider` (`builtin.local_sqlite`)
- `register_builtin_data_providers(...)`

Default local SQLite path:

- `tools/_local/tmp/pyside6_glass_dashboard.sqlite3`

## Reusable rendering surface

Location: `forgeos/shared/pyside6_glass/dashboard.py`

- `DashboardQuerySpec`: provider/query binding configuration
- `DashboardDataSurface`: provider-bound dashboard panel

Behavior:

- displays loading, empty, error, ready and stale-aware states
- supports refresh action and polling from `RefreshPolicy`
- renders metrics, table rows, feed items, payload, diagnostics
- includes local search/filter controls (search bar + filter chips + toolbar actions)
- includes status badges for state/count/refresh/filter context

## Catalog integration

Location: `forgeos/shared/pyside6_glass/examples/catalog_dashboard_entries.py`

Provider-backed entries are registered into the catalog through the same registry used by all other built-ins. This keeps dashboard entries extensible without modifying the catalog shell.

Current built-in data dashboard entries include:

- Live Metrics Board
- Service Health Monitor
- Alerts and Incidents Surface
- Jobs / Queue Monitor
- Table + Detail Inspector
- Time-Series Placeholder Dashboard
- Operational Overview
- Data Source Diagnostics
- Refreshable KPI Surface (loading/empty/error/stale simulation actions)
- Event Stream / Activity Feed
- Filterable Control Center
- Split View Operations Console

## Extension flow for future apps

1. Implement provider:
   - return `DataResult` envelopes only
   - keep source-specific logic inside provider
2. Register provider:
   - `register_data_provider(...)`
3. Compose dashboard surface:
   - `DashboardDataSurface(DashboardQuerySpec(...))`
4. Optionally register in catalog:
   - `register_catalog_entry(..., builder=...)`

## Notes

- Keep transport/database details out of widgets.
- Use provider metadata + diagnostics for discoverability/debugging.
- Prefer deterministic local data for starter demos.
