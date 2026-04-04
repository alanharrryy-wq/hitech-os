from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QWidget

from ..assets import GlassSegmentedControl, ParameterPanel
from ..config import get_template_preset
from ..dashboard import DashboardDataSurface, DashboardQuerySpec
from ..data import DataResult, describe_data_provider
from ..data_providers import default_local_dashboard_db_path, register_builtin_data_providers
from ..primitives import QuickActionsStrip
from ..template import GlassPanelTemplate


@dataclass(frozen=True, slots=True)
class DashboardCatalogEntrySpec:
    entry_id: str
    title: str
    subtitle: str
    description: str
    provider_id: str
    query_id: str
    category: str = "Data Dashboards"
    tags: tuple[str, ...] = ("dashboard", "data", "provider")
    preset_hint: str | None = "dashboard"
    theme_hint: str | None = None
    status: str = "stable"
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 500
    icon_name: str | None = "activity"
    query_params: dict[str, Any] = field(default_factory=dict)
    query_context: dict[str, Any] = field(default_factory=dict)
    special_builder: Callable[[QWidget | None], QWidget] | None = None


def _detail_panel(spec: DashboardCatalogEntrySpec, parent: QWidget | None = None) -> QTextEdit:
    details = {
        "entry_id": spec.entry_id,
        "provider_id": spec.provider_id,
        "query_id": spec.query_id,
        "query_params": spec.query_params,
        "query_context": spec.query_context,
        "local_sqlite_path": str(default_local_dashboard_db_path()),
        "provider_info": describe_data_provider(spec.provider_id),
    }
    widget = QTextEdit(parent)
    widget.setReadOnly(True)
    widget.setPlainText(json.dumps(details, indent=2, ensure_ascii=True, default=str))
    return widget


def _build_data_dashboard_entry(spec: DashboardCatalogEntrySpec, parent: QWidget | None = None) -> GlassPanelTemplate:
    register_builtin_data_providers()
    preset = spec.preset_hint or "dashboard"
    template = GlassPanelTemplate(
        parent,
        config=get_template_preset(preset),
        title=spec.title,
        subtitle=spec.subtitle,
        eyebrow="DATA DASHBOARD",
        theme_id=spec.theme_hint,
    )

    status_line = QLabel("Provider-bound dashboard surface", template)
    status_line.setProperty("role", "panel_subtitle")
    status_line.setWordWrap(True)
    template.slots.main_slot.addWidget(status_line)

    def _on_result(result: DataResult) -> None:
        state = result.normalized_state()
        rows_count = len(result.rows)
        feed_count = len(result.feed)
        metrics_count = len(result.metrics)
        template.set_status_text(
            f"{spec.provider_id}:{spec.query_id} -> {state} · metrics={metrics_count} · rows={rows_count} · feed={feed_count}"
        )
        status_line.setText(
            f"Provider {spec.provider_id} · query {spec.query_id} · state {state} · refreshed {result.refreshed_at_utc}"
        )

    surface = DashboardDataSurface(
        DashboardQuerySpec(
            provider_id=spec.provider_id,
            query_id=spec.query_id,
            title=spec.title,
            subtitle=spec.description,
            params=dict(spec.query_params),
            context=dict(spec.query_context),
        ),
        parent=template,
        on_result=_on_result,
    )
    template.slots.main_slot.addWidget(surface, 1)
    template.slots.side_slot.addWidget(_detail_panel(spec, template), 1)
    template._dashboard_surface = surface  # keep alive for callbacks
    return template


def _build_refreshable_kpi_entry(parent: QWidget | None = None) -> GlassPanelTemplate:
    spec = DashboardCatalogEntrySpec(
        entry_id="data.refreshable_kpi_surface",
        title="Refreshable KPI Surface",
        subtitle="Manual refresh + simulated loading/empty/error states",
        description="Interactive state lab for data-driven cards and operational behavior.",
        provider_id="builtin.mock_dashboard",
        query_id="refreshable_kpi",
        keywords=("refresh", "states", "loading", "empty", "error"),
        icon_name="refresh-cw",
        sort_order=590,
    )
    template = _build_data_dashboard_entry(spec, parent)
    surface: DashboardDataSurface = template._dashboard_surface

    strip = QuickActionsStrip(template)
    strip.add_action("Ready", icon_name="check", on_click=lambda: _set_state(surface, None))
    strip.add_action("Empty", icon_name="minus-circle", on_click=lambda: _set_state(surface, "empty"))
    strip.add_action("Error", icon_name="alert-triangle", on_click=lambda: _set_state(surface, "error"))
    strip.add_action("Loading", icon_name="loader", on_click=lambda: _set_state(surface, "loading"))
    strip.add_action("Stale", icon_name="clock", on_click=lambda: _set_state(surface, "stale"))
    strip.add_action("Refresh", icon_name="refresh-cw", on_click=surface.reload)
    template.slots.side_slot.insertWidget(0, strip)
    template.set_status_text("Use the state actions to simulate loading/empty/error/stale and refresh cycles.")
    return template


def _set_state(surface: DashboardDataSurface, state: str | None) -> None:
    params = dict(surface.spec.params)
    if state:
        params["simulate_state"] = state
    else:
        params.pop("simulate_state", None)
    surface.set_query_params(params)
    surface.reload()


def _build_filterable_control_center(parent: QWidget | None = None) -> GlassPanelTemplate:
    spec = DashboardCatalogEntrySpec(
        entry_id="data.filterable_control_center",
        title="Filterable Control Center",
        subtitle="Filter chips, search and segmented context over provider data",
        description="Control-center surface with built-in local filtering controls on top of provider data.",
        provider_id="builtin.mock_dashboard",
        query_id="alerts_incidents",
        keywords=("filterable", "control", "alerts"),
        icon_name="sliders-horizontal",
        sort_order=610,
    )
    template = _build_data_dashboard_entry(spec, parent)
    segmented = GlassSegmentedControl(
        (("alerts_incidents", "Alerts"), ("service_health", "Health"), ("event_feed", "Feed")),
        selected="alerts_incidents",
        parent=template,
    )
    surface: DashboardDataSurface = template._dashboard_surface

    def _switch(query_id: str) -> None:
        surface.spec.query_id = query_id
        surface.reload()

    segmented.value_changed.connect(_switch)
    template.slots.side_slot.insertWidget(0, segmented)
    template.set_status_text("Use segmented control + local filters to inspect provider states.")
    return template


def _build_split_view_operations_console(parent: QWidget | None = None) -> GlassPanelTemplate:
    register_builtin_data_providers()
    template = GlassPanelTemplate(
        parent,
        config=get_template_preset("tabbed_workspace"),
        title="Split View Operations Console",
        subtitle="Main data surface + side parameters powered by provider model",
        eyebrow="DATA DASHBOARD",
    )
    left_surface = DashboardDataSurface(
        DashboardQuerySpec(
            provider_id="builtin.local_sqlite",
            query_id="operational_overview",
            title="Operational Overview",
            subtitle="SQLite-backed local operations dataset",
        ),
        parent=template,
    )
    right_surface = DashboardDataSurface(
        DashboardQuerySpec(
            provider_id="builtin.mock_dashboard",
            query_id="event_feed",
            title="Live Event Feed",
            subtitle="Mock provider event stream",
            include_metrics=False,
            include_payload=False,
            include_diagnostics=False,
        ),
        parent=template,
    )

    split_host = QWidget(template)
    split_layout = QHBoxLayout(split_host)
    split_layout.setContentsMargins(0, 0, 0, 0)
    split_layout.setSpacing(8)
    split_layout.addWidget(left_surface, 3)
    split_layout.addWidget(right_surface, 2)
    template.slots.main_slot.addWidget(split_host, 1)

    params = ParameterPanel("Operations Parameters", parent=template)
    scope = params.add_text_field("Scope", placeholder="core,queue,alerts")
    params.add_slider("Refresh Interval (s)", minimum=1, maximum=60, value=8)
    params.add_toggle("Auto Refresh", checked=True)
    template.slots.side_slot.addWidget(params, 1)

    def _on_scope_changed() -> None:
        value = scope.text().strip()
        left_surface.set_query_params({"scope": value} if value else {})
        left_surface.reload()

    scope.editingFinished.connect(_on_scope_changed)
    template.set_status_text("Split-view operations console loaded.")
    return template


def iter_dashboard_catalog_specs() -> tuple[DashboardCatalogEntrySpec, ...]:
    return (
        DashboardCatalogEntrySpec(
            entry_id="data.live_metrics_board",
            title="Live Metrics Board",
            subtitle="Provider-backed KPI board for throughput, latency and queue depth",
            description="High-signal KPI surface intended for operational dashboards.",
            provider_id="builtin.mock_dashboard",
            query_id="live_metrics",
            keywords=("kpi", "metrics", "throughput", "latency"),
            best_for="Operational KPI monitoring with quick health signal checks.",
            use_when="you need fast read of throughput/latency/error posture.",
            sort_order=510,
            icon_name="activity",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.service_health_monitor",
            title="Service Health Monitor",
            subtitle="Health rows + status distribution",
            description="Service-level health monitor with summary counts and status table.",
            provider_id="builtin.mock_dashboard",
            query_id="service_health",
            keywords=("health", "service", "status"),
            best_for="Service-level health posture and degradation overview.",
            use_when="you need status rows plus summary counts by health level.",
            sort_order=520,
            icon_name="heart",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.alerts_incidents_surface",
            title="Alerts and Incidents Surface",
            subtitle="Alerts table and incident feed",
            description="Operational alerts surface with incident table and recent feed.",
            provider_id="builtin.mock_dashboard",
            query_id="alerts_incidents",
            keywords=("alerts", "incidents", "events"),
            best_for="Alert triage and incident-first operations workflows.",
            use_when="you need to track critical/warning items and latest signals.",
            sort_order=530,
            icon_name="alert-circle",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.jobs_queue_monitor",
            title="Jobs / Queue Monitor",
            subtitle="Queue backlog and execution state",
            description="Queue monitor backed by local SQLite provider to model local dev workflows.",
            provider_id="builtin.local_sqlite",
            query_id="jobs_queue",
            keywords=("queue", "jobs", "sqlite"),
            best_for="Local queue behavior inspection without remote dependencies.",
            use_when="you are validating backlog/running/retry status locally.",
            sort_order=540,
            icon_name="list",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.table_detail_inspector",
            title="Table + Detail Inspector",
            subtitle="Records table with selected-detail payload",
            description="Inspector-style surface combining tabular overview and structured detail payload.",
            provider_id="builtin.local_sqlite",
            query_id="table_detail",
            preset_hint="inspector",
            keywords=("table", "detail", "inspector"),
            best_for="Master-detail workflows over tabular provider datasets.",
            use_when="you need table context plus focused payload detail.",
            sort_order=550,
            icon_name="search",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.time_series_placeholder_dashboard",
            title="Time-Series Placeholder Dashboard",
            subtitle="Payload-based placeholder series for charts",
            description="Neutral placeholder for chart-ready time-series payloads.",
            provider_id="builtin.mock_dashboard",
            query_id="time_series_placeholder",
            keywords=("timeseries", "chart", "placeholder"),
            best_for="Wiring chart-ready payload contracts before chart integration.",
            use_when="you need a neutral time-series payload surface first.",
            sort_order=560,
            icon_name="trending-up",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.operational_overview",
            title="Operational Overview",
            subtitle="Combined metrics, rows and feed summary",
            description="Overview panel that combines key metrics and runtime summaries.",
            provider_id="builtin.local_sqlite",
            query_id="operational_overview",
            keywords=("overview", "operations", "summary"),
            best_for="Cross-domain operational pulse from one surface.",
            use_when="you want summary metrics + rows + feed context.",
            sort_order=570,
            icon_name="layout-dashboard",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.data_source_diagnostics",
            title="Data Source Diagnostics",
            subtitle="Provider diagnostics and data-source metadata",
            description="Diagnostics-focused surface with provider metadata and registry status.",
            provider_id="builtin.local_sqlite",
            query_id="data_source_diagnostics",
            preset_hint="tabbed_workspace",
            keywords=("diagnostics", "provider", "metadata"),
            best_for="Data source and registry diagnostics inspection.",
            use_when="you need provider metadata + refresh diagnostics quickly.",
            sort_order=580,
            icon_name="cpu",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.refreshable_kpi_surface",
            title="Refreshable KPI Surface",
            subtitle="Manual refresh + simulated loading/empty/error states",
            description="Interactive state lab for data-driven cards and operational behavior.",
            provider_id="builtin.mock_dashboard",
            query_id="refreshable_kpi",
            keywords=("refresh", "states", "loading", "empty", "error"),
            best_for="State behavior testing of provider-driven widgets.",
            use_when="you need to validate loading/empty/error interactions.",
            sort_order=590,
            icon_name="refresh-cw",
            special_builder=_build_refreshable_kpi_entry,
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.event_stream_activity_feed",
            title="Event Stream / Activity Feed",
            subtitle="Provider-backed activity stream",
            description="Event feed reference surface for timeline-like operational updates.",
            provider_id="builtin.mock_dashboard",
            query_id="event_feed",
            keywords=("feed", "events", "timeline"),
            best_for="Recent activity monitoring and event timeline context.",
            use_when="you need a lightweight feed-focused operations panel.",
            sort_order=600,
            icon_name="clock",
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.filterable_control_center",
            title="Filterable Control Center",
            subtitle="Filter chips and segmented control over provider data",
            description="Filter-first operations surface that drives multiple provider query contexts.",
            provider_id="builtin.mock_dashboard",
            query_id="alerts_incidents",
            keywords=("filter", "control_center", "segmented"),
            best_for="Filter-first operations control surfaces.",
            use_when="you need segmented contexts with local filter tooling.",
            sort_order=610,
            icon_name="sliders-horizontal",
            special_builder=_build_filterable_control_center,
        ),
        DashboardCatalogEntrySpec(
            entry_id="data.split_view_operations_console",
            title="Split View Operations Console",
            subtitle="Two synchronized provider surfaces in split layout",
            description="Operations console with main overview, feed side, and compact parameter panel.",
            provider_id="builtin.local_sqlite",
            query_id="operational_overview",
            keywords=("split_view", "operations", "console"),
            best_for="Split-view operations consoles with side controls.",
            use_when="you need synchronized overview and feed panels.",
            sort_order=620,
            icon_name="panel-right",
            special_builder=_build_split_view_operations_console,
        ),
    )


def build_dashboard_catalog_entry(spec: DashboardCatalogEntrySpec, parent: QWidget | None = None) -> QWidget:
    if spec.special_builder is not None:
        return spec.special_builder(parent)
    return _build_data_dashboard_entry(spec, parent)
