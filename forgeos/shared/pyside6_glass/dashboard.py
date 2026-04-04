from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .appearance import AppearanceProfile, AppearanceSnapshot, EffectsProfile
from .assets import CompactToolbar, FilterChipBar, SearchCommandBar, StatusPill
from .charts import resolve_chart_contract
from .component_governance import mark_component
from .data import DataQuery, DataResult, DataState, RefreshPolicy, execute_data_query
from .primitives import EmptyStateCard, ErrorStateCard, LoadingStateCard, MetricValue, PanelHeader, StatCard
from .rendering import apply_surface_role, install_surface_renderer, sync_surface_renderer


def _clear_layout(layout: QVBoxLayout | QGridLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        child_widget = item.widget()
        child_layout = item.layout()
        if child_widget is not None:
            child_widget.setParent(None)
            continue
        if child_layout is not None:
            while child_layout.count():
                nested_item = child_layout.takeAt(0)
                nested_widget = nested_item.widget()
                if nested_widget is not None:
                    nested_widget.setParent(None)


def _as_text(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _state_to_pill_kind(state: str) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in {DataState.ERROR}:
        return "error"
    if normalized in {DataState.EMPTY, DataState.STALE}:
        return "warning"
    if normalized in {DataState.LOADING}:
        return "pending"
    if normalized in {DataState.READY}:
        return "success"
    return "success"


def _resolve_snapshot_for(widget: QWidget | None) -> AppearanceSnapshot:
    cursor = widget
    while cursor is not None:
        snapshot_getter = getattr(cursor, "appearance_snapshot", None)
        if callable(snapshot_getter):
            try:
                snapshot = snapshot_getter()
            except Exception:  # noqa: BLE001
                snapshot = None
            if isinstance(snapshot, AppearanceSnapshot):
                return snapshot
        cursor = cursor.parentWidget()
    profile = AppearanceProfile(theme_id="silver_frost_cyan")
    return AppearanceSnapshot(
        profile=profile,
        effects=EffectsProfile.from_appearance(profile),
        source="dashboard:fallback_snapshot",
    )


class _DashboardGovernedWidgetMixin:
    _surface_role: str = "panel_data"
    _surface_variant: str = "panel"
    _surface_emphasis: str = "normal"
    _surface_fx_level: str = "soft"

    def _install_visual_contract(self) -> None:
        if not isinstance(self, QWidget):
            return
        existing_key = str(self.property('componentKey') or '').strip().lower()
        mark_component(
            self,
            component_key=existing_key or (self.objectName() or self.__class__.__name__),
        )
        apply_surface_role(
            self,
            role=self._surface_role,
            variant=self._surface_variant,
            emphasis=self._surface_emphasis,
            fx_level=self._surface_fx_level,
        )
        install_surface_renderer(self)
        sync_surface_renderer(self, _resolve_snapshot_for(self))


class _DashboardDataTable(_DashboardGovernedWidgetMixin, QTableWidget):
    _surface_role = "panel_data"
    _surface_variant = "panel"
    _surface_emphasis = "normal"
    _surface_fx_level = "soft"

    def __init__(self, rows: int, columns: int, parent: QWidget | None = None) -> None:
        super().__init__(rows, columns, parent)
        self.setObjectName("DashboardDataTable")
        self.setProperty("card", "clear")
        mark_component(self, component_key='dashboard_table')
        self._install_visual_contract()


class _DashboardFeedList(_DashboardGovernedWidgetMixin, QListWidget):
    _surface_role = "panel_aux"
    _surface_variant = "panel"
    _surface_emphasis = "subtle"
    _surface_fx_level = "soft"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardFeedList")
        self.setProperty("card", "clear")
        mark_component(self, component_key='dashboard_feed')
        self._install_visual_contract()


class _DashboardPayloadViewer(_DashboardGovernedWidgetMixin, QTextEdit):
    _surface_role = "panel_detail"
    _surface_variant = "panel"
    _surface_emphasis = "subtle"
    _surface_fx_level = "soft"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardPayloadViewer")
        self.setProperty("card", "clear")
        self.setReadOnly(True)
        mark_component(self, component_key='dashboard_payload')
        self._install_visual_contract()


@dataclass(slots=True)
class DashboardQuerySpec:
    provider_id: str
    query_id: str = "default"
    title: str = "Data Surface"
    subtitle: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    include_metrics: bool = True
    include_rows: bool = True
    include_feed: bool = True
    include_payload: bool = True
    include_diagnostics: bool = True
    max_metrics: int = 8
    max_rows: int = 100
    max_feed: int = 50
    local_filter_keys: tuple[str, ...] = ("status", "state", "severity", "level")
    enable_search: bool = True
    enable_filter_chips: bool = True
    enable_toolbar: bool = True
    refresh_policy: RefreshPolicy | None = None
    chart_style_id: str | None = None
    chart_palette_id: str | None = None
    experience_mode: str = "dashboard"
    visual_level: str = "standard"

    def build_query(self) -> DataQuery:
        return DataQuery.create(
            provider_id=self.provider_id,
            query_id=self.query_id,
            params=self.params,
            context=self.context,
        )


class DashboardDataSurface(QFrame):
    """Provider-bound reusable dashboard surface.

    The surface keeps data retrieval (`execute_data_query`) separate from rendering and
    can be reused in catalog demos or app-level compositions.
    """

    def __init__(
        self,
        spec: DashboardQuerySpec,
        *,
        parent: QWidget | None = None,
        on_result: Callable[[DataResult], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("card", "clear")
        mark_component(self, component_key='dashboard_data_surface')
        self.spec = spec
        self._on_result = on_result
        self._last_result: DataResult | None = None
        self._reload_in_progress = False
        self._search_text = ""
        self._current_filter = "all"
        self._chart_style = None
        self._chart_palette = None

        root = QVBoxLayout(self)
        root.setContentsMargins(2, 2, 2, 2)
        root.setSpacing(4)

        self.header = PanelHeader(
            spec.title,
            subtitle=spec.subtitle or f"{spec.provider_id} · {spec.query_id}",
            icon_name="activity",
            parent=self,
        )
        self.header.add_action("Refresh", icon_name="refresh-cw", on_click=self.reload)
        root.addWidget(self.header)

        self.toolbar = CompactToolbar("Dashboard Controls", parent=self)
        self.toolbar.setVisible(bool(spec.enable_toolbar))
        self.toolbar.add_action("Refresh", icon_name="refresh-cw", on_click=self.reload)
        self.toolbar.add_action("Clear Filters", icon_name="x-circle", variant="ghost", on_click=self.clear_filters)
        root.addWidget(self.toolbar)

        self.search_bar = SearchCommandBar(
            placeholder="Filter rows/feed locally by text...",
            parent=self,
        )
        self.search_bar.setVisible(bool(spec.enable_search))
        self.search_bar.search_changed.connect(self._on_search_changed)
        root.addWidget(self.search_bar)

        self.filter_chips = FilterChipBar(self)
        self.filter_chips.setVisible(bool(spec.enable_filter_chips))
        self.filter_chips.selection_changed.connect(self._on_filter_changed)
        root.addWidget(self.filter_chips)

        self.status_label = QLabel("Idle", self)
        self.status_label.setProperty("role", "panel_subtitle")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)
        self.status_badges_host = QWidget(self)
        self.status_badges_layout = QHBoxLayout(self.status_badges_host)
        self.status_badges_layout.setContentsMargins(0, 0, 0, 0)
        self.status_badges_layout.setSpacing(4)
        self.state_badge = StatusPill("IDLE", kind="info", parent=self.status_badges_host)
        self.count_badge = StatusPill("0 rows", kind="info", parent=self.status_badges_host)
        self.refresh_badge = StatusPill("manual", kind="info", parent=self.status_badges_host)
        self.filter_badge = StatusPill("no filters", kind="pending", parent=self.status_badges_host)
        self.chart_badge = StatusPill("chart=auto", kind="info", parent=self.status_badges_host)
        for badge in (self.state_badge, self.count_badge, self.refresh_badge, self.filter_badge, self.chart_badge):
            self.status_badges_layout.addWidget(badge, 0)
        self.status_badges_layout.addStretch(1)
        root.addWidget(self.status_badges_host)

        self.body_host = QWidget(self)
        self.body_layout = QVBoxLayout(self.body_host)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(4)
        root.addWidget(self.body_host, 1)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self.reload)
        self._apply_refresh_policy(spec.refresh_policy or RefreshPolicy(mode="manual"))
        self.reload()

    @property
    def last_result(self) -> DataResult | None:
        return self._last_result

    def set_query_params(self, params: dict[str, Any]) -> None:
        self.spec.params = dict(params or {})

    def set_query_context(self, context: dict[str, Any]) -> None:
        self.spec.context = dict(context or {})

    def clear_filters(self) -> None:
        self._search_text = ""
        self._current_filter = "all"
        if self.spec.enable_search:
            self.search_bar.input.clear()
        if self.spec.enable_filter_chips:
            self._rebuild_filter_chips(())
        if self._last_result is not None:
            self._render_result(self._last_result)

    def reload(self) -> None:
        if self._reload_in_progress:
            return
        self._reload_in_progress = True
        try:
            self._render_loading()
            result = execute_data_query(
                self.spec.build_query(),
                fallback_policy=self.spec.refresh_policy or RefreshPolicy(mode="manual"),
            )
            self._last_result = result
            self._apply_refresh_policy(result.refresh_policy)
            self._render_result(result)
            if self._on_result is not None:
                self._on_result(result)
        except Exception as exc:  # noqa: BLE001
            failure = DataResult.failure(
                self.spec.build_query(),
                code="dashboard_render_contract_violation",
                message=str(exc),
                details={
                    "provider_id": self.spec.provider_id,
                    "query_id": self.spec.query_id,
                    "chart_style_id": self.spec.chart_style_id,
                    "chart_palette_id": self.spec.chart_palette_id,
                },
                policy=self.spec.refresh_policy or RefreshPolicy(mode="manual"),
            )
            self._last_result = failure
            self._render_contract_failure(failure, message=str(exc))
            if self._on_result is not None:
                self._on_result(failure)
        finally:
            self._reload_in_progress = False

    def _on_search_changed(self, text: str) -> None:
        self._search_text = str(text or "").strip().lower()
        if self._last_result is not None and not self._reload_in_progress:
            self._render_result(self._last_result)

    def _on_filter_changed(self, selected_values: tuple) -> None:
        selected = [str(item or "").strip().lower() for item in selected_values if str(item or "").strip()]
        self._current_filter = selected[0] if selected else "all"
        if self._last_result is not None and not self._reload_in_progress:
            self._render_result(self._last_result)

    def _apply_refresh_policy(self, policy: RefreshPolicy) -> None:
        normalized = policy.normalized()
        if normalized.mode == "polling":
            self._poll_timer.start(normalized.interval_ms)
        else:
            self._poll_timer.stop()

    def _render_loading(self) -> None:
        _clear_layout(self.body_layout)
        self._resolve_chart_contract(DataState.LOADING)
        self.body_layout.addWidget(
            LoadingStateCard(
                "Loading dashboard data",
                message="Querying provider and preparing render sections.",
                progress=35,
                parent=self.body_host,
            )
        )
        self._update_status_labels(
            state=DataState.LOADING,
            result_counts={"metrics": 0, "rows": 0, "feed": 0},
            filtered_counts={"rows": 0, "feed": 0},
            refreshed_at="",
            refresh_mode="pending",
        )
        self.status_label.setText("Loading data...")

    def _render_contract_failure(self, result: DataResult, *, message: str) -> None:
        _clear_layout(self.body_layout)
        self.chart_badge.setText("chart=contract_error")
        self.chart_badge.setProperty("statusKind", "error")
        self.chart_badge.style().unpolish(self.chart_badge)
        self.chart_badge.style().polish(self.chart_badge)
        self._update_status_labels(
            state=DataState.ERROR,
            result_counts={"metrics": 0, "rows": 0, "feed": 0},
            filtered_counts={"rows": 0, "feed": 0},
            refreshed_at=result.refreshed_at_utc,
            refresh_mode=result.refresh_policy.mode,
        )
        self.body_layout.addWidget(
            ErrorStateCard(
                "Visual contract violation",
                message,
                details="Dashboard requested chart style/palette outside registry constraints.",
                retry=self.reload,
                parent=self.body_host,
            )
        )

    def _collect_filter_values(self, result: DataResult) -> tuple[str, ...]:
        found: set[str] = set()
        for row in result.rows:
            for key in self.spec.local_filter_keys:
                value = row.get(key)
                if value is not None and str(value).strip():
                    found.add(str(value).strip().lower())
        for item in result.feed:
            for key in self.spec.local_filter_keys:
                value = item.get(key)
                if value is not None and str(value).strip():
                    found.add(str(value).strip().lower())
        return tuple(sorted(found))

    def _rebuild_filter_chips(self, values: tuple[str, ...]) -> None:
        if not self.spec.enable_filter_chips:
            return
        self.filter_chips.blockSignals(True)
        self.filter_chips.clear()
        self.filter_chips.add_chip("all", "All", checked=(self._current_filter == "all"))
        for value in values:
            normalized = str(value or "").strip().lower()
            if not normalized or normalized == "all":
                continue
            self.filter_chips.add_chip(normalized, normalized.title(), checked=(self._current_filter == normalized))
        self.filter_chips.blockSignals(False)

    def _resolve_chart_contract(self, state: str) -> tuple[str, str]:
        style, palette = resolve_chart_contract(
            style_id=self.spec.chart_style_id,
            palette_id=self.spec.chart_palette_id,
            data_state=state,
            experience_mode=self.spec.experience_mode,
            visual_level=self.spec.visual_level,
        )
        self._chart_style = style
        self._chart_palette = palette
        self.chart_badge.setText(f"chart={style.style_id} · palette={palette.palette_id}")
        self.chart_badge.setProperty("statusKind", "info")
        self.chart_badge.style().unpolish(self.chart_badge)
        self.chart_badge.style().polish(self.chart_badge)
        return style.style_id, palette.palette_id

    def _apply_local_filters(self, result: DataResult) -> DataResult:
        search_text = self._search_text
        selected_filter = self._current_filter
        rows: list[dict[str, Any]] = []
        feed: list[dict[str, Any]] = []

        for row in result.rows:
            text_blob = " ".join(_as_text(value).lower() for value in row.values())
            if search_text and search_text not in text_blob:
                continue
            if selected_filter and selected_filter != "all":
                matched = any(str(row.get(key, "")).strip().lower() == selected_filter for key in self.spec.local_filter_keys)
                if not matched:
                    continue
            rows.append(dict(row))

        for item in result.feed:
            text_blob = " ".join(_as_text(value).lower() for value in item.values())
            if search_text and search_text not in text_blob:
                continue
            if selected_filter and selected_filter != "all":
                matched = any(str(item.get(key, "")).strip().lower() == selected_filter for key in self.spec.local_filter_keys)
                if not matched:
                    continue
            feed.append(dict(item))

        return result.with_content(rows=rows, feed=feed)

    def _update_status_labels(
        self,
        *,
        state: str,
        result_counts: dict[str, int],
        filtered_counts: dict[str, int],
        refreshed_at: str,
        refresh_mode: str,
    ) -> None:
        stale_note = "stale" if state == DataState.STALE else "fresh"
        self.state_badge.setText(state.upper())
        self.state_badge.setProperty("statusKind", _state_to_pill_kind(state))
        self.state_badge.style().unpolish(self.state_badge)
        self.state_badge.style().polish(self.state_badge)

        rows_count = int(result_counts.get("rows") or 0)
        feed_count = int(result_counts.get("feed") or 0)
        metrics_count = int(result_counts.get("metrics") or 0)
        self.count_badge.setText(f"{metrics_count} metrics · {rows_count} rows · {feed_count} feed")

        self.refresh_badge.setText(f"{refresh_mode} · {stale_note}")
        has_filters = bool(self._search_text or (self._current_filter and self._current_filter != "all"))
        if has_filters:
            self.filter_badge.setText(
                f"filter={self._current_filter or 'all'} · search={self._search_text or '(none)'} · visible rows={filtered_counts.get('rows', 0)}"
            )
            self.filter_badge.setProperty("statusKind", "info")
        else:
            self.filter_badge.setText("no filters")
            self.filter_badge.setProperty("statusKind", "pending")
        self.filter_badge.style().unpolish(self.filter_badge)
        self.filter_badge.style().polish(self.filter_badge)

        refreshed_text = refreshed_at or "n/a"
        self.status_label.setText(
            f"State: {state} · provider={self.spec.provider_id} · query={self.spec.query_id} · refreshed={refreshed_text}"
        )

    def _render_result(self, result: DataResult) -> None:
        filtered_result = self._apply_local_filters(result)
        filter_values = self._collect_filter_values(result)
        self._rebuild_filter_chips(filter_values)

        _clear_layout(self.body_layout)
        state = filtered_result.normalized_state()
        state_for_display = DataState.STALE if filtered_result.is_stale() else state
        self._resolve_chart_contract(state_for_display)
        self._update_status_labels(
            state=state_for_display,
            result_counts={
                "metrics": len(result.metrics),
                "rows": len(result.rows),
                "feed": len(result.feed),
            },
            filtered_counts={
                "rows": len(filtered_result.rows),
                "feed": len(filtered_result.feed),
            },
            refreshed_at=filtered_result.refreshed_at_utc,
            refresh_mode=filtered_result.refresh_policy.mode,
        )

        if state == DataState.LOADING:
            self.body_layout.addWidget(
                LoadingStateCard(
                    "Loading dashboard data",
                    message="Provider query is still running.",
                    progress=35,
                    parent=self.body_host,
                )
            )
            return
        if state == DataState.ERROR:
            message = filtered_result.error.message if filtered_result.error is not None else "Unknown data query error"
            details = ""
            if filtered_result.error is not None and filtered_result.error.details:
                details = f"Error code: {filtered_result.error.code}"
            self.body_layout.addWidget(
                ErrorStateCard(
                    "Data query failed",
                    message,
                    details=details,
                    retry=self.reload,
                    parent=self.body_host,
                )
            )
            self._render_payload_block("Diagnostics", filtered_result.to_payload())
            return
        if state == DataState.EMPTY:
            self.body_layout.addWidget(
                EmptyStateCard(
                    "No data available",
                    "Provider returned no rows/metrics/feed for this query. Try refresh or adjust params.",
                    action_label="Refresh",
                    action=self.reload,
                    parent=self.body_host,
                )
            )
            self._render_payload_block("Summary", filtered_result.summary)
            return

        filters_active = bool(self._search_text or (self._current_filter and self._current_filter != "all"))
        if filters_active and not filtered_result.rows and not filtered_result.feed and not filtered_result.metrics:
            self.body_layout.addWidget(
                EmptyStateCard(
                    "No matches for active filters",
                    "The provider returned data, but current search/filter constraints hide all visible sections.",
                    meta="Clear local filters to restore full provider output.",
                    action_label="Clear Filters",
                    action=self.clear_filters,
                    parent=self.body_host,
                )
            )
            return

        rendered = False
        if self.spec.include_metrics and filtered_result.metrics:
            self.body_layout.addWidget(self._metrics_widget(filtered_result))
            rendered = True
        if self.spec.include_rows and filtered_result.rows:
            self.body_layout.addWidget(self._table_widget(filtered_result), 1)
            rendered = True
        if self.spec.include_feed and filtered_result.feed:
            self.body_layout.addWidget(self._feed_widget(filtered_result), 1)
            rendered = True
        if self.spec.include_payload and filtered_result.payload:
            self._render_payload_block("Payload", filtered_result.payload)
            rendered = True
        if self.spec.include_diagnostics and filtered_result.diagnostics:
            self._render_payload_block("Diagnostics", filtered_result.diagnostics)
            rendered = True
        if not rendered:
            self.body_layout.addWidget(
                EmptyStateCard(
                    "No renderable sections",
                    "The provider answered successfully but no enabled section had content.",
                    parent=self.body_host,
                )
            )

    def _metrics_widget(self, result: DataResult) -> QWidget:
        host = QFrame(self.body_host)
        host.setProperty("card", "clear")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        title = QLabel("Metrics", host)
        title.setProperty("role", "panel_title")
        layout.addWidget(title)

        grid_host = QWidget(host)
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)
        metrics_items = list(result.metrics.items())[: self.spec.max_metrics]
        for idx, (key, value) in enumerate(metrics_items):
            card = StatCard(metric=MetricValue(label=str(key), value=_as_text(value)), parent=grid_host)
            grid.addWidget(card, idx // 3, idx % 3)
        layout.addWidget(grid_host)
        return host

    def _table_widget(self, result: DataResult) -> QWidget:
        host = QFrame(self.body_host)
        host.setProperty("card", "clear")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        title_host = QWidget(host)
        title_layout = QHBoxLayout(title_host)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        title = QLabel("Rows", title_host)
        title.setProperty("role", "panel_title")
        title_layout.addWidget(title, 0)
        title_layout.addStretch(1)
        title_layout.addWidget(StatusPill(f"{len(result.rows)} rows", kind="info", parent=title_host), 0)
        layout.addWidget(title_host)

        table_rows = result.rows[: self.spec.max_rows]
        columns: list[str] = []
        for row in table_rows:
            for key in row.keys():
                if key not in columns:
                    columns.append(str(key))
        if not columns:
            columns = ["value"]
        table = _DashboardDataTable(len(table_rows), len(columns), host)
        table.setHorizontalHeaderLabels(columns)
        for row_idx, row in enumerate(table_rows):
            for col_idx, key in enumerate(columns):
                table.setItem(row_idx, col_idx, QTableWidgetItem(_as_text(row.get(key, ""))))
        table.resizeColumnsToContents()
        layout.addWidget(table, 1)
        return host

    def _feed_widget(self, result: DataResult) -> QWidget:
        host = QFrame(self.body_host)
        host.setProperty("card", "clear")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        title_host = QWidget(host)
        title_layout = QHBoxLayout(title_host)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        title = QLabel("Activity Feed", title_host)
        title.setProperty("role", "panel_title")
        title_layout.addWidget(title, 0)
        title_layout.addStretch(1)
        status_kind = "info"
        if any(str(item.get("level") or item.get("severity") or "").lower() in {"critical", "error"} for item in result.feed):
            status_kind = "error"
        elif any(str(item.get("level") or item.get("severity") or "").lower() in {"warning", "warn"} for item in result.feed):
            status_kind = "warning"
        title_layout.addWidget(StatusPill(f"{len(result.feed)} events", kind=status_kind, parent=title_host), 0)
        layout.addWidget(title_host)

        feed_widget = _DashboardFeedList(host)
        for item in result.feed[: self.spec.max_feed]:
            severity = _as_text(item.get("level") or item.get("severity") or "info").upper()
            timestamp = _as_text(item.get("time") or item.get("created_at_utc") or item.get("created_at") or "")
            message = _as_text(item.get("message") or item.get("event_type") or item)
            source = _as_text(item.get("source") or item.get("service") or "")
            line = f"[{severity}] {timestamp} {message}"
            if source:
                line += f" · {source}"
            feed_widget.addItem(QListWidgetItem(line))
        layout.addWidget(feed_widget, 1)
        return host

    def _render_payload_block(self, title: str, payload: dict[str, Any]) -> None:
        host = QFrame(self.body_host)
        host.setProperty("card", "clear")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        heading = QLabel(title, host)
        heading.setProperty("role", "panel_title")
        layout.addWidget(heading)
        viewer = _DashboardPayloadViewer(host)
        viewer.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
        layout.addWidget(viewer, 1)
        self.body_layout.addWidget(host, 1)
