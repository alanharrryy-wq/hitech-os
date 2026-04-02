from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import GlassTemplateConfig, get_template_preset
from ..runtime import (
    GlassRuntimeContext,
    GlassVisibilityPolicy,
    GlassVisibilityRule,
    GlassWorkspaceRuntime,
)
from ..template import GlassPanelTemplate, GlassWorkspaceTabSpec


def _section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "panel_title")
    return label


def build_form_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("form_console"))
    form_host = QWidget(template)
    form_layout = QFormLayout(form_host)
    form_layout.setContentsMargins(0, 0, 0, 0)
    form_layout.setSpacing(8)
    form_layout.addRow("Name", QLineEdit(form_host))
    form_layout.addRow("Email", QLineEdit(form_host))
    notes = QTextEdit(form_host)
    notes.setPlaceholderText("Notes")
    form_layout.addRow("Notes", notes)
    template.slots.main_slot.addWidget(_section_label("Capture"))
    template.slots.main_slot.addWidget(form_host)

    sidebar = QListWidget(template)
    sidebar.addItems(["Validation checks", "Pending items", "Submission history"])
    template.slots.side_slot.addWidget(_section_label("Checklist"))
    template.slots.side_slot.addWidget(sidebar, 1)
    template.set_status_text("Form example loaded.")
    return template


def build_dashboard_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"))
    tiles = QWidget(template)
    grid = QGridLayout(tiles)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(10)
    grid.setVerticalSpacing(10)
    metrics = [("Throughput", "92/s"), ("Errors", "1.2%"), ("Latency", "134ms"), ("Queue", "27")]
    for idx, (name, value) in enumerate(metrics):
        card = QWidget(tiles)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.addWidget(QLabel(name, card))
        value_label = QLabel(value, card)
        value_label.setProperty("role", "title")
        card_layout.addWidget(value_label)
        grid.addWidget(card, idx // 2, idx % 2)

    table = QTableWidget(4, 3, template)
    table.setHorizontalHeaderLabels(["Service", "Status", "Trend"])
    rows = [
        ("api-gateway", "healthy", "up"),
        ("jobs", "warning", "flat"),
        ("billing", "healthy", "up"),
        ("webhooks", "degraded", "down"),
    ]
    for row_idx, row in enumerate(rows):
        for col_idx, value in enumerate(row):
            table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    template.slots.main_slot.addWidget(_section_label("KPI Surface"))
    template.slots.main_slot.addWidget(tiles)
    template.slots.main_slot.addWidget(table, 1)

    progress = QProgressBar(template)
    progress.setRange(0, 100)
    progress.setValue(72)
    template.slots.side_slot.addWidget(_section_label("Execution"))
    template.slots.side_slot.addWidget(progress)
    template.set_status_text("Dashboard example loaded.")
    return template


def build_inspector_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("inspector"))
    events = QListWidget(template)
    events.addItems(
        [
            "session.created",
            "scope.validated",
            "plan.generated",
            "apply.completed",
        ]
    )
    detail = QTextEdit(template)
    detail.setReadOnly(True)
    detail.setPlainText("Select an event to inspect payload details.")
    template.slots.main_slot.addWidget(_section_label("Event Stream"))
    template.slots.main_slot.addWidget(events, 1)
    template.slots.side_slot.addWidget(_section_label("Detail"))
    template.slots.side_slot.addWidget(detail, 1)
    template.set_status_text("Inspector example loaded.")
    return template


def build_tabbed_workspace_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("tabbed_workspace"))
    template.slots.main_slot.addWidget(_section_label("Active Workspace"))
    template.slots.main_slot.addWidget(QTextEdit(template))
    template.slots.side_slot.addWidget(_section_label("Context"))
    template.slots.side_slot.addWidget(QListWidget(template), 1)

    if template.workspace_tabs is not None:
        review_tab = QWidget(template)
        review_layout = QVBoxLayout(review_tab)
        review_layout.setContentsMargins(0, 0, 0, 0)
        review_layout.addWidget(QLabel("Review context on hold.", review_tab))
        template.add_workspace_tab(
            tab_id="review",
            title="Review",
            widget=review_tab,
            state="hold",
            icon_name="clock",
        )

        archive_tab = QWidget(template)
        archive_layout = QVBoxLayout(archive_tab)
        archive_layout.setContentsMargins(0, 0, 0, 0)
        archive_layout.addWidget(QLabel("Archive context currently hidden.", archive_tab))
        template.add_workspace_tab(
            tab_id="archive",
            title="Archive",
            widget=archive_tab,
            state="hidden",
            icon_name="box",
        )
    template.set_status_text("Tabbed workspace with contextual visibility loaded.")
    return template


def build_alternate_preset_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    config = GlassTemplateConfig(
        title="Alternate Preset",
        subtitle="Using obsidian_ice theme with compact density.",
        eyebrow="ALT PRESET",
    )
    template = GlassPanelTemplate(
        parent,
        config=config,
        theme_id="obsidian_ice",
        density="compact",
        typography_scale="sm",
    )
    info = QTextEdit(template)
    info.setReadOnly(True)
    info.setPlainText(
        "This sample demonstrates alternate theme + density without changing framework internals."
    )
    template.slots.main_slot.addWidget(info, 1)
    template.set_status_text("Alternate preset example loaded.")
    return template


def build_orchestration_example(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(
        parent,
        config=get_template_preset("tabbed_workspace"),
        title="Runtime Orchestration",
        subtitle="Theme, density, layout and visibility policies from runtime layer.",
        eyebrow="RUNTIME",
    )

    info = QTextEdit(template)
    info.setReadOnly(True)
    info.setPlainText(
        "This view demonstrates:\n"
        "- runtime preset activation\n"
        "- role/capability visibility policy\n"
        "- layout switching\n"
        "- workspace persistence save/load\n"
        "- keyboard routing defaults\n"
    )
    template.slots.main_slot.addWidget(info, 1)

    controls = QWidget(template)
    controls_layout = QVBoxLayout(controls)
    controls_layout.setContentsMargins(0, 0, 0, 0)
    controls_layout.setSpacing(8)
    controls_layout.addWidget(_section_label("Runtime Controls"))

    btn_row = QHBoxLayout()
    btn_row.setContentsMargins(0, 0, 0, 0)
    btn_row.setSpacing(8)

    apply_focus = QPushButton("Focus Layout", controls)
    apply_inspect = QPushButton("Inspect Layout", controls)
    to_dashboard = QPushButton("Preset: Dashboard", controls)
    to_operator = QPushButton("Preset: Operator", controls)
    save_state = QPushButton("Save State", controls)
    load_state = QPushButton("Load State", controls)
    for button in (
        apply_focus,
        apply_inspect,
        to_dashboard,
        to_operator,
        save_state,
        load_state,
    ):
        btn_row.addWidget(button)
    controls_layout.addLayout(btn_row)

    runtime_log = QTextEdit(controls)
    runtime_log.setReadOnly(True)
    runtime_log.setPlainText("Runtime events:\n")
    controls_layout.addWidget(runtime_log, 1)
    template.slots.side_slot.addWidget(controls, 1)

    if template.workspace_tabs is not None:
        ops_view = QTextEdit(template)
        ops_view.setReadOnly(True)
        ops_view.setPlainText("Operations context")
        template.add_workspace_tab(
            tab_id="ops",
            title="Operations",
            state="visible",
            widget=ops_view,
            icon_name="activity",
            badge="3",
        )
        review_view = QTextEdit(template)
        review_view.setReadOnly(True)
        review_view.setPlainText("Review queue")
        template.add_workspace_tab(
            tab_id="review",
            title="Review",
            state="hold",
            widget=review_view,
            icon_name="clock",
            badge="1",
        )
        admin_view = QTextEdit(template)
        admin_view.setReadOnly(True)
        admin_view.setPlainText("Admin-only tab")
        template.add_workspace_tab(
            tab_id="admin",
            title="Admin",
            state="hidden",
            widget=admin_view,
            icon_name="shield",
            pinned=True,
        )

    policy = GlassVisibilityPolicy(
        rules=[
            GlassVisibilityRule("tab", "admin", visible_state="visible", required_capabilities=("admin",)),
            GlassVisibilityRule("tab", "review", visible_state="hold", allowed_roles=("operator", "reviewer")),
            GlassVisibilityRule("panel", "side", visible_state="visible", allowed_modes=("default", "review")),
        ]
    )
    runtime = GlassWorkspaceRuntime(template, preset="tabbed_workspace", visibility_policy=policy)
    runtime.register_layout("focus", {"main_side": [980, 220]})
    runtime.register_layout("inspect", {"main_side": [620, 620]})
    runtime.apply_resolved_config()
    runtime.bind_default_shortcuts(template)
    runtime.apply_visibility_context(GlassRuntimeContext(role="operator", mode="default", capabilities=frozenset({"ops"})))

    workspace_path = "tools/_local/tmp/glass_runtime_demo_workspace.json"

    def _log(line: str) -> None:
        runtime_log.append(line)
        template.set_status_text(line)

    def _apply_focus() -> None:
        runtime.apply_layout("focus")
        _log("Applied layout: focus")

    def _apply_inspect() -> None:
        runtime.apply_layout("inspect")
        _log("Applied layout: inspect")

    def _to_dashboard() -> None:
        runtime.activate_preset("dashboard")
        _log("Activated preset: dashboard")

    def _to_operator() -> None:
        runtime.activate_preset("compact_operator")
        _log("Activated preset: compact_operator")

    def _save_state() -> None:
        saved = runtime.save_workspace_state(workspace_path)
        _log(f"Workspace state saved: {saved}")

    def _load_state() -> None:
        loaded = runtime.load_workspace_state(workspace_path)
        if loaded is None:
            _log("No persisted state found to load.")
            return
        _log("Workspace state loaded from persisted storage.")

    apply_focus.clicked.connect(_apply_focus)
    apply_inspect.clicked.connect(_apply_inspect)
    to_dashboard.clicked.connect(_to_dashboard)
    to_operator.clicked.connect(_to_operator)
    save_state.clicked.connect(_save_state)
    load_state.clicked.connect(_load_state)

    template.add_footer_action("Ops Role", "secondary", on_click=lambda: runtime.apply_visibility_context(
        GlassRuntimeContext(role="operator", mode="default", capabilities=frozenset({"ops"}))
    ))
    template.add_footer_action("Admin Role", "secondary", on_click=lambda: runtime.apply_visibility_context(
        GlassRuntimeContext(role="admin", mode="review", capabilities=frozenset({"ops", "admin"}))
    ))
    template.set_status_text("Runtime orchestration example loaded.")
    template._runtime = runtime  # keep runtime alive for shortcut/handler ownership
    return template


class GlassExampleCatalog(QWidget):
    """
    Backward-compatible entry point.

    Legacy imports keep working while the implementation is delegated to
    the richer registry-based catalog shell.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from .catalog_shell import GlassCatalogShell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._catalog = GlassCatalogShell(self)
        layout.addWidget(self._catalog, 1)
