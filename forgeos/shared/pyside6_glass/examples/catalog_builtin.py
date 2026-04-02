from __future__ import annotations

import json
from typing import Any, Callable

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..catalog import register_catalog_entry
from ..config import get_template_preset
from ..data_providers import register_builtin_data_providers
from ..integration import InProcessIntegrationAdapter, create_reference_workspace_service
from ..primitives import (
    DashboardWidgetShell,
    EmptyStateCard,
    ErrorStateCard,
    FormSectionShell,
    LoadingStateCard,
    MetricValue,
    PanelHeader,
    QuickActionsStrip,
    StatCard,
)
from ..template import GlassPanelTemplate
from ..theme import get_theme_manifest, list_theme_ids
from .compositions import (
    build_alternate_preset_example,
    build_dashboard_example,
    build_form_example,
    build_inspector_example,
    build_orchestration_example,
    build_tabbed_workspace_example,
)
from .catalog_dashboard_entries import build_dashboard_catalog_entry, iter_dashboard_catalog_specs
from .catalog_assets_entries import iter_asset_catalog_specs


_BUILTINS_DONE = False


def _note_block(text: str, parent: QWidget | None = None) -> QTextEdit:
    editor = QTextEdit(parent)
    editor.setReadOnly(True)
    editor.setPlainText(text)
    return editor


def _template_for_preset(preset_id: str, parent: QWidget | None = None) -> GlassPanelTemplate:
    config = get_template_preset(preset_id)
    template = GlassPanelTemplate(
        parent,
        config=config,
        title=f"Preset: {preset_id}",
        subtitle=config.subtitle,
        eyebrow="PRESET",
    )
    template.slots.main_slot.addWidget(
        _note_block(
            f"Preset '{preset_id}'\n\n"
            f"Title: {config.title}\n"
            f"Density: {config.theme.density}\n"
            f"Experience mode: {config.theme.experience_mode}\n"
            f"Layout: {config.layout.active_layout}\n"
            f"Tabs enabled: {config.tabs.enabled}\n",
            template,
        ),
        1,
    )
    actions = QuickActionsStrip(template)
    actions.add_action("Compact", icon_name="minimize-2", on_click=lambda: template.set_density("compact"))
    actions.add_action("Comfortable", icon_name="square", on_click=lambda: template.set_density("comfortable"))
    actions.add_action("Spacious", icon_name="maximize-2", on_click=lambda: template.set_density("spacious"))
    template.slots.side_slot.addWidget(actions)
    template.set_status_text(f"Preset preview for '{preset_id}' loaded.")
    return template


def _template_for_theme(theme_id: str, parent: QWidget | None = None) -> GlassPanelTemplate:
    manifest = get_theme_manifest(theme_id)
    template = GlassPanelTemplate(
        parent,
        config=get_template_preset("neutral"),
        title=f"Theme: {theme_id}",
        subtitle=manifest.description or "Theme preview",
        eyebrow="THEME",
        theme_id=theme_id,
    )

    stats_host = QWidget(template)
    stats_layout = QVBoxLayout(stats_host)
    stats_layout.setContentsMargins(0, 0, 0, 0)
    stats_layout.setSpacing(8)
    stats_layout.addWidget(
        StatCard(metric=MetricValue("Primary Text", manifest.palette.text_primary, "token"), parent=stats_host)
    )
    stats_layout.addWidget(
        StatCard(metric=MetricValue("Accent", manifest.palette.accent, "token"), parent=stats_host)
    )
    stats_layout.addWidget(
        StatCard(metric=MetricValue("Card Border", manifest.palette.card_border, "token"), parent=stats_host)
    )
    template.slots.main_slot.addWidget(stats_host)
    template.slots.main_slot.addWidget(
        _note_block(
            f"Theme id: {manifest.theme_id}\n"
            f"Description: {manifest.description}\n"
            f"Parent: {manifest.parent_theme_id or '(none)'}\n",
            template,
        ),
        1,
    )
    template.set_status_text(f"Theme preview '{theme_id}' loaded.")
    return template


def _primitive_stat_cards(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title="Primitive: Stat Cards")
    host = QWidget(template)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(StatCard(metric=MetricValue("Throughput", "124/s", "up"), parent=host))
    layout.addWidget(StatCard(metric=MetricValue("Pending", "17", "stable"), parent=host))
    layout.addWidget(StatCard(metric=MetricValue("Errors", "0.3%", "down"), parent=host))
    template.slots.main_slot.addWidget(host, 1)
    template.set_status_text("Stat cards primitive gallery loaded.")
    return template


def _primitive_quick_actions(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("neutral"), title="Primitive: Quick Actions")
    strip = QuickActionsStrip(template)
    strip.add_action("Refresh", icon_name="refresh-cw")
    strip.add_action("Focus", icon_name="target")
    strip.add_action("Export", icon_name="download")
    strip.add_action("Inspect", icon_name="search")
    template.slots.main_slot.addWidget(strip)
    template.slots.main_slot.addWidget(_note_block("QuickActionsStrip supports dense, reusable command rows.", template), 1)
    template.set_status_text("Quick actions strip primitive loaded.")
    return template


def _primitive_panel_header(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("inspector"), title="Primitive: Panel Header")
    header = PanelHeader(
        "Runtime Health",
        subtitle="Header with actions and semantic icon.",
        icon_name="activity",
        parent=template,
    )
    header.add_action("Refresh", icon_name="refresh-cw")
    header.add_action("Open", icon_name="external-link")
    template.slots.main_slot.addWidget(header)
    template.slots.main_slot.addWidget(_note_block("PanelHeader can be reused for cards, shells and side panes.", template), 1)
    template.set_status_text("Panel header primitive loaded.")
    return template


def _primitive_form_section(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("form_console"), title="Primitive: Form Section")
    section = FormSectionShell("Contact", subtitle="Reusable form grouping shell", parent=template)
    section.content.addWidget(QLineEdit(section))
    section.content.addWidget(QLineEdit(section))
    section.content.addWidget(QLineEdit(section))
    template.slots.main_slot.addWidget(section, 1)
    template.set_status_text("Form section shell primitive loaded.")
    return template


def _primitive_state_cards(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("neutral"), title="Primitive: State Cards")
    template.slots.main_slot.addWidget(LoadingStateCard("Loading assets", progress=68, parent=template))
    template.slots.main_slot.addWidget(EmptyStateCard("No results", "Try changing your filters.", parent=template))
    template.slots.main_slot.addWidget(ErrorStateCard("Connection issue", "Endpoint unreachable.", parent=template))
    template.set_status_text("Loading/empty/error state cards loaded.")
    return template


def _primitive_dashboard_widget(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(parent, config=get_template_preset("dashboard"), title="Primitive: Dashboard Widget")
    widget_shell = DashboardWidgetShell("Revenue Trend", subtitle="Widget shell composition", parent=template)
    widget_shell.content.addWidget(_note_block("Drop chart/table/metric content here.", widget_shell))
    template.slots.main_slot.addWidget(widget_shell, 1)
    template.set_status_text("Dashboard widget shell primitive loaded.")
    return template


def _integration_runtime_catalog_entry(parent: QWidget | None = None) -> GlassPanelTemplate:
    return build_orchestration_example(parent)


def _integration_contracts_catalog_entry(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = GlassPanelTemplate(
        parent,
        config=get_template_preset("tabbed_workspace"),
        title="Integration Contracts Showcase",
        subtitle="Command/query/snapshot/event flow through neutral integration service.",
        eyebrow="INTEGRATION",
    )
    service, _ = create_reference_workspace_service(debug=False, namespace="workspace")
    adapter = InProcessIntegrationAdapter(service)
    contracts = adapter.contracts()
    command_response = adapter.command(
        {
            "command": "workspace.item.upsert",
            "payload": {"item_id": "catalog", "item": {"label": "Catalog Entry"}},
            "context": {"client_id": "catalog", "capabilities": ["workspace.write"]},
            "idempotency_key": "catalog-item-upsert",
        }
    )
    query_response = adapter.query({"query": "workspace.summary.get", "params": {}, "context": {"client_id": "catalog"}})
    snapshot_response = adapter.snapshot({"snapshot_id": "workspace", "selector": {}, "context": {"client_id": "catalog"}})
    events = adapter.poll_events(since_sequence=0, limit=20)

    template.slots.main_slot.addWidget(
        _note_block(
            json.dumps(
                {
                    "contracts": contracts,
                    "command": command_response,
                    "query": query_response,
                    "snapshot": snapshot_response,
                    "events": events,
                },
                indent=2,
                ensure_ascii=True,
            ),
            template,
        ),
        1,
    )
    template.set_status_text("Integration contracts showcase loaded.")
    return template


def _register_entry(
    entry_id: str,
    title: str,
    *,
    subtitle: str,
    description: str,
    category: str,
    tags: tuple[str, ...],
    builder: Callable[[QWidget | None], QWidget],
    preset_hint: str | None = None,
    theme_hint: str | None = None,
    status: str = "stable",
    keywords: tuple[str, ...] = (),
    best_for: str = "",
    use_when: str = "",
    sort_order: int = 100,
    icon_name: str | None = None,
) -> None:
    register_catalog_entry(
        entry_id=entry_id,
        title=title,
        subtitle=subtitle,
        description=description,
        category=category,
        tags=tags,
        builder=builder,
        preset_hint=preset_hint,
        theme_hint=theme_hint,
        status=status,
        keywords=keywords,
        best_for=best_for,
        use_when=use_when,
        sort_order=sort_order,
        icon_name=icon_name,
        override=True,
    )


def register_builtin_catalog_entries(*, force: bool = False) -> None:
    global _BUILTINS_DONE
    if _BUILTINS_DONE and not force:
        return
    register_builtin_data_providers(force=force)

    example_entries = [
        (
            "example.form",
            "Form Example",
            "Structured capture workspace",
            "Form-oriented starter composition with side checklist.",
            "Compositions",
            ("example", "workspace", "forms"),
            build_form_example,
            "form_console",
            None,
            "stable",
            ("capture", "input", "workflow"),
            "Form-heavy workspaces and structured data capture flows.",
            "you are building input-first operational screens.",
            10,
            "file-text",
        ),
        (
            "example.dashboard",
            "Dashboard Example",
            "KPI-oriented operational view",
            "Dashboard composition with metrics, table and execution panel.",
            "Compositions",
            ("example", "dashboard", "metrics"),
            build_dashboard_example,
            "dashboard",
            None,
            "stable",
            ("kpi", "analytics", "monitoring"),
            "Operational KPI boards and summary-first monitoring surfaces.",
            "you need a starter layout for metrics + table + side execution pane.",
            20,
            "activity",
        ),
        (
            "example.inspector",
            "Inspector Example",
            "Event and detail inspection view",
            "Inspector composition with stream list and detail panel.",
            "Compositions",
            ("example", "inspector", "detail"),
            build_inspector_example,
            "inspector",
            None,
            "stable",
            ("inspect", "detail", "events"),
            "Detail inspection and event-to-payload debugging surfaces.",
            "you need a main list + detail side panel flow.",
            30,
            "search",
        ),
        (
            "example.workspace",
            "Tabbed Workspace Example",
            "Context-based workspace tabs",
            "Tabbed workspace with hold/hidden states for contextual visibility.",
            "Compositions",
            ("example", "tabs", "workspace"),
            build_tabbed_workspace_example,
            "tabbed_workspace",
            None,
            "stable",
            ("tabs", "visibility", "contexts"),
            "Multi-context workspaces with controlled visibility states.",
            "you want hold/hidden tabs for secondary contexts.",
            40,
            "layers",
        ),
        (
            "example.alternate_preset",
            "Alternate Preset Example",
            "Theme+density variant sample",
            "Demonstrates alternate theme and compact density without changing core internals.",
            "Compositions",
            ("example", "theme", "density"),
            build_alternate_preset_example,
            "neutral",
            "obsidian_ice",
            "stable",
            ("preset", "variant", "theme"),
            "Quickly testing theme+density alternatives without core rewrites.",
            "you need to validate visual variants rapidly.",
            50,
            "palette",
        ),
        (
            "example.runtime_orchestration",
            "Runtime Orchestration Example",
            "Preset/layout/visibility runtime flow",
            "Shows runtime controls, persistence and visibility policy in action.",
            "Compositions",
            ("example", "runtime", "orchestration"),
            build_orchestration_example,
            "tabbed_workspace",
            None,
            "stable",
            ("runtime", "policy", "persistence"),
            "Runtime policy validation and persistence behavior checks.",
            "you want to test orchestration controls and workspace lifecycle.",
            60,
            "cpu",
        ),
    ]

    for entry in example_entries:
        _register_entry(
            entry[0],
            entry[1],
            subtitle=entry[2],
            description=entry[3],
            category=entry[4],
            tags=entry[5],
            builder=entry[6],
            preset_hint=entry[7],
            theme_hint=entry[8],
            status=entry[9],
            keywords=entry[10],
            best_for=entry[11],
            use_when=entry[12],
            sort_order=entry[13],
            icon_name=entry[14],
        )

    preset_descriptions = {
        "neutral": "Balanced baseline preset for general-purpose workstation surfaces.",
        "form_console": "Structured data-entry and form-heavy workflows.",
        "dashboard": "KPI and monitoring-oriented panel rhythm.",
        "inspector": "Detail-first inspection workflows with contextual side panel.",
        "tabbed_workspace": "Multi-context workflows with explicit tab states.",
        "compact_operator": "High-density operator mode with keyboard-first ergonomics.",
        "presentation": "Larger typography and spacing for demos/reviews.",
    }
    for index, preset_id in enumerate(
        ("neutral", "form_console", "dashboard", "inspector", "tabbed_workspace", "compact_operator", "presentation"),
        start=1,
    ):
        _register_entry(
            f"preset.{preset_id}",
            f"Preset: {preset_id}",
            subtitle="Built-in preset profile",
            description=preset_descriptions.get(preset_id, "Built-in preset."),
            category="Presets",
            tags=("preset", "built-in"),
            builder=lambda parent, pid=preset_id: _template_for_preset(pid, parent),
            preset_hint=preset_id,
            status="stable",
            keywords=("preset", "config", "starter"),
            best_for="Applying a coherent configuration baseline for a new screen.",
            use_when="you need consistent layout/theme/density defaults with minimal setup.",
            sort_order=100 + index,
            icon_name="sliders",
        )

    theme_descriptions = {
        "silver_frost_cyan": "Low-saturation silver/cyan glass, default calm workstation tone.",
        "obsidian_ice": "Cool dark glass variant with obsidian/ice contrast.",
    }
    for index, theme_id in enumerate(list_theme_ids(), start=1):
        _register_entry(
            f"theme.{theme_id}",
            f"Theme: {theme_id}",
            subtitle="Built-in theme profile",
            description=theme_descriptions.get(theme_id, get_theme_manifest(theme_id).description or "Built-in theme."),
            category="Themes",
            tags=("theme", "built-in"),
            builder=lambda parent, tid=theme_id: _template_for_theme(tid, parent),
            theme_hint=theme_id,
            status="stable",
            keywords=("theme", "palette", "tokens"),
            best_for="Selecting visual identity tokens for a full surface.",
            use_when="you need to validate readability/contrast and style direction.",
            sort_order=200 + index,
            icon_name="droplets",
        )

    primitive_entries = [
        (
            "primitive.stat_cards",
            "Primitive: Stat Cards",
            "Metric values and trends",
            "Showcase for reusable `StatCard` component.",
            _primitive_stat_cards,
            "activity",
        ),
        (
            "primitive.quick_actions_strip",
            "Primitive: Quick Actions Strip",
            "Dense command/action row",
            "Showcase for reusable quick actions command strip.",
            _primitive_quick_actions,
            "zap",
        ),
        (
            "primitive.panel_header",
            "Primitive: Panel Header",
            "Header with icon and actions",
            "Showcase for reusable `PanelHeader` component.",
            _primitive_panel_header,
            "heading",
        ),
        (
            "primitive.form_section_shell",
            "Primitive: Form Section Shell",
            "Structured form grouping",
            "Showcase for reusable `FormSectionShell` component.",
            _primitive_form_section,
            "list",
        ),
        (
            "primitive.state_cards",
            "Primitive: State Cards",
            "Empty/loading/error reusable states",
            "Showcase for `LoadingStateCard`, `EmptyStateCard`, and `ErrorStateCard`.",
            _primitive_state_cards,
            "alert-circle",
        ),
        (
            "primitive.dashboard_widget_shell",
            "Primitive: Dashboard Widget Shell",
            "Container shell for dashboard blocks",
            "Showcase for reusable `DashboardWidgetShell` composition.",
            _primitive_dashboard_widget,
            "grid",
        ),
    ]
    for index, item in enumerate(primitive_entries, start=1):
        _register_entry(
            item[0],
            item[1],
            subtitle=item[2],
            description=item[3],
            category="Primitives",
            tags=("primitive", "component"),
            builder=item[4],
            status="stable",
            keywords=("component", "gallery", "starter"),
            best_for="Reusing a focused primitive in multiple screens.",
            use_when="you are composing UI from small reusable building blocks.",
            sort_order=300 + index,
            icon_name=item[5],
        )

    _register_entry(
        "runtime.integration_orchestration",
        "Runtime Orchestration",
        subtitle="Visibility/layout/persistence in one sample",
        description="Runtime orchestration showcase with policies and workspace state behavior.",
        category="Runtime & Integration",
        tags=("runtime", "integration", "orchestration"),
        builder=_integration_runtime_catalog_entry,
        status="stable",
        keywords=("runtime", "visibility", "persistence"),
        best_for="Validating runtime coordination behavior and persistence policies.",
        use_when="you need to test orchestration flows, not just static visuals.",
        sort_order=401,
        icon_name="cpu",
    )
    _register_entry(
        "runtime.integration_contracts",
        "Integration Contracts Showcase",
        subtitle="Command/query/snapshot/event payloads",
        description="In-process integration contract flow with structured payload output.",
        category="Runtime & Integration",
        tags=("runtime", "integration", "contracts"),
        builder=_integration_contracts_catalog_entry,
        status="stable",
        keywords=("contracts", "service", "adapter"),
        best_for="Inspecting neutral command/query/snapshot/event contract flow.",
        use_when="you need to debug integration payloads end-to-end.",
        sort_order=402,
        icon_name="link",
    )

    for spec in iter_dashboard_catalog_specs():
        _register_entry(
            spec.entry_id,
            spec.title,
            subtitle=spec.subtitle,
            description=spec.description,
            category=spec.category,
            tags=spec.tags,
            builder=lambda parent, entry_spec=spec: build_dashboard_catalog_entry(entry_spec, parent),
            preset_hint=spec.preset_hint,
            theme_hint=spec.theme_hint,
            status=spec.status,
            keywords=spec.keywords,
            best_for=getattr(spec, "best_for", ""),
            use_when=getattr(spec, "use_when", ""),
            sort_order=spec.sort_order,
            icon_name=spec.icon_name,
        )

    for spec in iter_asset_catalog_specs():
        _register_entry(
            spec.entry_id,
            spec.title,
            subtitle=spec.subtitle,
            description=spec.description,
            category=spec.category,
            tags=spec.tags,
            builder=spec.builder,
            status=spec.status,
            keywords=spec.keywords,
            best_for=getattr(spec, "best_for", ""),
            use_when=getattr(spec, "use_when", ""),
            sort_order=spec.sort_order,
            icon_name=spec.icon_name,
        )

    _BUILTINS_DONE = True
