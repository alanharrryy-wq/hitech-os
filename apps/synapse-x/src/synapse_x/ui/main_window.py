
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine
from visuals.common.types import ActionSpec, ChipSpec, TemplateConsoleConfig
from visuals.screens.template_console import TemplateConsoleWindow

from .controllers import AppController
from .panels import ControlsPanel, DetailPanel, MetricsPanel, ResultsPanel


def _build_config() -> TemplateConsoleConfig:
    return TemplateConsoleConfig(
        window_title="synapse-x Operations Deck",
        theme_id="silver_frost_cyan",
        ui_scale="100",
        hero_eyebrow="Operational Memory",
        hero_title="synapse-x Operations Deck",
        hero_subtitle=(
            "Live glass host for indexed search, session drill-down, ingest operations, "
            "telemetry charts, and graceful fallbacks when optional chart extras are missing."
        ),
        hero_icon="workspace",
        hero_chips=[
            ChipSpec("synapse-x", tone="accent", icon="spark"),
            ChipSpec("Operations Deck", tone="neutral", icon="overview"),
            ChipSpec("Indexed Memory", tone="neutral", icon="search"),
        ],
        toolbar_title="Command Rail",
        toolbar_actions=[
            ActionSpec("refresh", "Refresh", icon="refresh", variant="secondary"),
            ActionSpec("focus_search", "Search", icon="search", variant="secondary"),
            ActionSpec("load_recent", "Recent", icon="overview", variant="secondary"),
            ActionSpec("ingest_sample", "Ingest", icon="spark", variant="secondary"),
            ActionSpec("load_demo", "Demo", icon="spark", variant="secondary"),
            ActionSpec("repair_storage", "Repair", icon="settings", variant="secondary"),
            ActionSpec("toggle_sidebar", "Sidebar", icon="panel", variant="secondary"),
            ActionSpec("toggle_charts", "Charts", icon="overview", variant="secondary", checkable=True, checked=True),
        ],
        panel_order=("sidebar", "main", "aux"),
        show_sidebar=True,
        show_aux=True,
        sidebar_title="Controls",
        main_title="Results + Detail",
        aux_title="Live Metrics",
        show_sidebar_builtin_controls=False,
        sidebar_hint="Search, ingest, refresh, repair, and runtime context live here.",
        main_hint="Recent and searched records stay on top while the detail inspector hydrates below.",
        aux_hint="Metrics, telemetry trends, and fallback diagnostics render here.",
        footer_hint="run_ui.py is the real UI entrypoint. starter.py remains a shell/demo launcher.",
    )


class SynapseXMainWindow(TemplateConsoleWindow):
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        engine: SynapseEngine | None = None,
        boot_demo: bool = False,
    ) -> None:
        self.settings = settings or Settings()
        self.engine = engine or SynapseEngine(self.settings)
        self.boot_demo = bool(boot_demo)
        self._shortcuts: list[QShortcut] = []
        super().__init__(config=_build_config())

        self.controls_panel = ControlsPanel(self)
        self.results_panel = ResultsPanel(self)
        self.detail_panel = DetailPanel(self)
        self.metrics_panel = MetricsPanel(self)

        self._mount_product_surfaces()
        self._install_shortcuts()
        self.controller = AppController(self, settings=self.settings, engine=self.engine, boot_demo=self.boot_demo)
        self.controller.bootstrap()

    def _mount_product_surfaces(self) -> None:
        self.set_slot_widget("sidebar", self.controls_panel)

        main_surface = QWidget(self)
        main_layout = QVBoxLayout(main_surface)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical, main_surface)
        splitter.addWidget(self.results_panel)
        splitter.addWidget(self.detail_panel)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([420, 280])
        main_layout.addWidget(splitter, 1)

        self.set_slot_widget("main", main_surface)
        self.set_chart_widget(self.metrics_panel)

    def _install_shortcuts(self) -> None:
        bindings = {
            "Ctrl+R": self.refresh_dashboard,
            "Ctrl+L": self.focus_search,
            "Ctrl+Shift+C": self.toggle_chart_visibility,
            "Ctrl+E": self.repair_storage,
            "Ctrl+D": self.load_demo_state,
            "Ctrl+I": self.ingest_sample,
        }
        for sequence, callback in bindings.items():
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)

    def focus_search(self) -> None:
        self.controls_panel.focus_query()
        self._set_footer_state("Search focused", "accent")

    def refresh_dashboard(self) -> None:
        self.controller.refresh_dashboard()

    def repair_storage(self) -> None:
        self.controller.repair_storage()

    def ingest_sample(self) -> None:
        self.controller.ingest_sample()

    def load_demo_state(self) -> None:
        self.controller.load_demo_state()

    def load_recent_rows(self) -> None:
        self.controller.load_recent_rows()

    def run_search(self, query: str | None = None) -> None:
        self.controller.run_search(query)

    def _on_toolbar_action(self, action_id: str) -> None:
        if action_id == "refresh":
            self.refresh_dashboard()
            return
        if action_id == "focus_search":
            self.focus_search()
            return
        if action_id == "load_recent":
            self.load_recent_rows()
            return
        if action_id == "ingest_sample":
            self.ingest_sample()
            return
        if action_id == "load_demo":
            self.load_demo_state()
            return
        if action_id == "repair_storage":
            self.repair_storage()
            return
        super()._on_toolbar_action(action_id)
