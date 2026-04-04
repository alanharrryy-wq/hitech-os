from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..assets import (
    CollapsibleSection,
    CompactToolbar,
    ControlCard,
    EnhancedSlider,
    FilterChipBar,
    GlassIconButton,
    GlassSegmentedControl,
    HeroPanel,
    MiniLegend,
    ParameterPanel,
    SearchCommandBar,
    StatPill,
    StatusPill,
    TogglePill,
)
from ..config import get_template_preset
from ..controls import create_button
from ..template import GlassPanelTemplate


@dataclass(frozen=True, slots=True)
class AssetCatalogEntrySpec:
    entry_id: str
    title: str
    subtitle: str
    description: str
    builder: Callable[[QWidget | None], QWidget]
    category: str = "Controls & Assets"
    tags: tuple[str, ...] = ("asset", "component", "gallery")
    status: str = "stable"
    keywords: tuple[str, ...] = ()
    best_for: str = ""
    use_when: str = ""
    sort_order: int = 700
    icon_name: str | None = "sparkles"


def _asset_template(title: str, subtitle: str, parent: QWidget | None = None) -> GlassPanelTemplate:
    return GlassPanelTemplate(
        parent,
        config=get_template_preset("dashboard"),
        title=title,
        subtitle=subtitle,
        eyebrow="ASSETS",
    )


def _buttons_gallery(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Buttons Gallery", "Primary, secondary and ghost button variants", parent)
    row = QWidget(template)
    row_layout = QVBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(8)
    row_layout.addWidget(create_button("Primary Action", "primary", parent=row, icon_name="zap"))
    row_layout.addWidget(create_button("Secondary Action", "secondary", parent=row, icon_name="layers"))
    row_layout.addWidget(create_button("Subtle Action", "subtle", parent=row, icon_name="sparkles"))
    row_layout.addWidget(create_button("Ghost Action", "ghost", parent=row, icon_name="search"))
    row_layout.addWidget(create_button("Danger Action", "danger", parent=row, icon_name="alert-triangle"))
    template.slots.main_slot.addWidget(row)
    template.set_status_text("Buttons gallery loaded.")
    return template


def _icon_buttons_gallery(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Icon Buttons", "Compact icon-only controls for dense toolbars", parent)
    toolbar = CompactToolbar("Icon actions", parent=template)
    toolbar.add_icon_action(icon_name="refresh-cw", tooltip="Refresh")
    toolbar.add_icon_action(icon_name="search", tooltip="Inspect")
    toolbar.add_icon_action(icon_name="download", tooltip="Export")
    toolbar.add_icon_action(icon_name="settings", tooltip="Settings")
    toolbar.add_action("Primary", icon_name="check", variant="primary")
    template.slots.main_slot.addWidget(toolbar)
    template.set_status_text("Icon buttons gallery loaded.")
    return template


def _segmented_toggles(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Segmented + Toggles", "Context switching and boolean controls", parent)
    segmented = GlassSegmentedControl(
        (("overview", "Overview"), ("alerts", "Alerts"), ("operations", "Operations")),
        selected="overview",
        parent=template,
    )
    toggle = TogglePill("Auto Refresh", "Paused", checked=True, parent=template)
    state = QLabel("Segment=overview · Auto Refresh=on", template)
    state.setProperty("role", "panel_subtitle")

    segmented.value_changed.connect(lambda value: state.setText(f"Segment={value} · Auto Refresh={'on' if toggle.isChecked() else 'off'}"))
    toggle.toggled_value.connect(lambda checked: state.setText(f"Segment={segmented.value()} · Auto Refresh={'on' if checked else 'off'}"))
    template.slots.main_slot.addWidget(segmented)
    template.slots.main_slot.addWidget(toggle)
    template.slots.main_slot.addWidget(state)
    template.set_status_text("Segmented and toggle controls loaded.")
    return template


def _chips_badges(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Filter Chips + Status Pills", "Filter chips and semantic status badges", parent)
    chips = FilterChipBar(template)
    chips.add_chip("all", "All", checked=True)
    chips.add_chip("healthy", "Healthy")
    chips.add_chip("warning", "Warning")
    chips.add_chip("critical", "Critical")

    legend = MiniLegend(template)
    legend.add_status("Healthy", "success")
    legend.add_status("Warning", "warning")
    legend.add_status("Critical", "error")
    legend.add_status("Pending", "pending")

    template.slots.main_slot.addWidget(chips)
    template.slots.main_slot.addWidget(legend)
    template.slots.main_slot.addWidget(StatusPill("Filter-aware badge", kind="info", parent=template))
    template.set_status_text("Filter chips and status pills loaded.")
    return template


def _slider_gallery(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Enhanced Sliders", "Compact scrubber controls for parameters", parent)
    gain = EnhancedSlider("Gain", minimum=0, maximum=100, value=42, parent=template)
    threshold = EnhancedSlider("Threshold", minimum=0, maximum=100, value=67, parent=template)
    cadence = EnhancedSlider("Cadence", minimum=1, maximum=60, value=15, parent=template)
    template.slots.main_slot.addWidget(gain)
    template.slots.main_slot.addWidget(threshold)
    template.slots.main_slot.addWidget(cadence)
    template.set_status_text("Enhanced slider gallery loaded.")
    return template


def _search_toolbar_gallery(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Search + Toolbar", "Command-style search bar with quick actions", parent)
    search = SearchCommandBar(placeholder="Search resources, events or commands...", parent=template)
    toolbar = CompactToolbar("Quick actions", parent=template)
    toolbar.add_action("Refresh", icon_name="refresh-cw")
    toolbar.add_action("Pin", icon_name="pin")
    toolbar.add_action("Open", icon_name="external-link", variant="ghost")
    template.slots.main_slot.addWidget(search)
    template.slots.main_slot.addWidget(toolbar)
    template.set_status_text("Search bar and compact toolbar loaded.")
    return template


def _stat_micro_kpi(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Stat Pills", "Micro-KPI surfaces for compact headers", parent)
    host = QWidget(template)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(StatPill("Throughput", "214/min", trend="up"))
    layout.addWidget(StatPill("Error Rate", "0.47%", trend="down"))
    layout.addWidget(StatPill("Queue Depth", "31", trend="flat"))
    template.slots.main_slot.addWidget(host)
    template.set_status_text("Stat pills loaded.")
    return template


def _control_cards(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Control Cards", "Reusable card shells for grouped controls", parent)
    card_a = ControlCard("Execution Controls", subtitle="Actions for pipeline operations", parent=template)
    card_a.content.addWidget(create_button("Start", "primary", parent=card_a, icon_name="play"))
    card_a.content.addWidget(create_button("Pause", "secondary", parent=card_a, icon_name="pause"))
    card_a.content.addWidget(create_button("Stop", "danger", parent=card_a, icon_name="square"))

    card_b = ControlCard("Scope Filters", subtitle="Refine the visible dataset", parent=template)
    card_b.content.addWidget(SearchCommandBar(placeholder="Filter scope...", parent=card_b))
    chips = FilterChipBar(card_b)
    chips.add_chip("core", "Core", checked=True)
    chips.add_chip("aux", "Aux")
    chips.add_chip("external", "External")
    card_b.content.addWidget(chips)

    template.slots.main_slot.addWidget(card_a)
    template.slots.main_slot.addWidget(card_b)
    template.set_status_text("Control cards gallery loaded.")
    return template


def _collapsible_sections(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Collapsible Sections", "Foldable sections for compact parameter surfaces", parent)
    section_a = CollapsibleSection("Runtime Parameters", subtitle="Adjust the active runtime profile", collapsed=False, parent=template)
    section_a.body_layout.addWidget(create_button("Apply Preset", "primary", parent=section_a, icon_name="check"))
    section_a.body_layout.addWidget(create_button("Reset", "ghost", parent=section_a, icon_name="rotate-ccw"))

    section_b = CollapsibleSection("Advanced Flags", subtitle="Secondary toggles and debug options", collapsed=True, parent=template)
    section_b.body_layout.addWidget(TogglePill("Enabled", "Disabled", checked=False, parent=section_b))
    section_b.body_layout.addWidget(TogglePill("Trace On", "Trace Off", checked=True, parent=section_b))

    template.slots.main_slot.addWidget(section_a)
    template.slots.main_slot.addWidget(section_b)
    template.set_status_text("Collapsible sections loaded.")
    return template


def _parameter_panel(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Parameter Panel", "Compact parameter panel for dashboard controls", parent)
    panel = ParameterPanel("Runtime Parameters", parent=template)
    panel.add_text_field("Workspace", placeholder="workspace.main")
    panel.add_text_field("Scope", placeholder="core,ops,alerts")
    panel.add_slider("Refresh (s)", minimum=1, maximum=60, value=10)
    panel.add_toggle("Auto Refresh", checked=True)
    template.slots.main_slot.addWidget(panel)
    template.set_status_text("Parameter panel loaded.")
    return template


def _hero_panel(parent: QWidget | None = None) -> GlassPanelTemplate:
    template = _asset_template("Hero Panel", "Reusable hero/header block for showcase screens", parent)
    hero = HeroPanel(
        "Operational Control Center",
        subtitle="Reusable top-level hero panel for dashboard and workstation entry screens.",
        eyebrow="HERO",
        parent=template,
    )
    template.slots.main_slot.addWidget(hero)
    template.slots.main_slot.addWidget(StatusPill("Ready for integration", kind="success", parent=template))
    template.set_status_text("Hero panel asset loaded.")
    return template


def iter_asset_catalog_specs() -> tuple[AssetCatalogEntrySpec, ...]:
    return (
        AssetCatalogEntrySpec(
            entry_id="asset.buttons_gallery",
            title="Buttons Gallery",
            subtitle="Primary/secondary/ghost/danger variants",
            description="Reusable button variants with visual hierarchy and icon support.",
            builder=_buttons_gallery,
            keywords=("button", "primary", "secondary", "ghost"),
            best_for="Action hierarchy and call-to-action affordance design.",
            use_when="you need consistent button variants across screens.",
            sort_order=710,
            icon_name="mouse-pointer-click",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.icon_buttons",
            title="Icon Buttons",
            subtitle="Compact icon-only controls for toolbars",
            description="High-density icon actions for compact dashboard toolbars.",
            builder=_icon_buttons_gallery,
            keywords=("icon", "toolbar", "actions"),
            best_for="Dense command bars and compact action strips.",
            use_when="you need icon-first actions with tight horizontal space.",
            sort_order=720,
            icon_name="circle-dot",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.segmented_toggles",
            title="Segmented + Toggle Controls",
            subtitle="Context switchers and boolean pills",
            description="Segmented control and toggle pills for context/state switching.",
            builder=_segmented_toggles,
            keywords=("segmented", "toggle", "switch"),
            best_for="Mode and boolean state switching controls.",
            use_when="you need explicit context switching and toggle pills.",
            sort_order=730,
            icon_name="toggle-left",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.filter_chips_badges",
            title="Filter Chips + Status Badges",
            subtitle="Chips, badges and mini legends",
            description="Filter chips and semantic status badges for dashboards.",
            builder=_chips_badges,
            keywords=("chip", "badge", "status", "legend"),
            best_for="Filter-oriented dashboards with status semantics.",
            use_when="you need quick filtering and compact status summaries.",
            sort_order=740,
            icon_name="tag",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.enhanced_sliders",
            title="Enhanced Sliders",
            subtitle="Scrubber-style slider controls",
            description="Compact scrubber sliders for runtime and parameter tuning.",
            builder=_slider_gallery,
            keywords=("slider", "scrubber", "parameter"),
            best_for="Numeric tuning controls in operations panels.",
            use_when="you need compact range/scrubber interactions.",
            sort_order=750,
            icon_name="sliders-horizontal",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.search_toolbar",
            title="Search + Toolbar Shell",
            subtitle="Command-style search with quick actions",
            description="Search command bar and compact toolbar pairing for operations panels.",
            builder=_search_toolbar_gallery,
            keywords=("search", "toolbar", "command"),
            best_for="Search-driven surfaces with quick action controls.",
            use_when="you need command-style search + action row together.",
            sort_order=760,
            icon_name="search",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.stat_pills",
            title="Stat Pills / Micro KPI",
            subtitle="Dense KPI chips for compact surfaces",
            description="Micro KPI surfaces for headers and narrow control regions.",
            builder=_stat_micro_kpi,
            keywords=("kpi", "micro", "stat"),
            best_for="Header-level KPI snapshots in dense layouts.",
            use_when="you need micro stats without full cards.",
            sort_order=770,
            icon_name="activity",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.control_cards",
            title="Control Cards",
            subtitle="Reusable cards for grouped controls",
            description="Control card shells with embedded actions and filters.",
            builder=_control_cards,
            keywords=("card", "control", "group"),
            best_for="Grouped interaction modules in dashboard side panes.",
            use_when="you need reusable grouped control blocks.",
            sort_order=780,
            icon_name="square-stack",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.collapsible_sections",
            title="Collapsible Sections",
            subtitle="Foldable sections for dense panels",
            description="Collapsible section headers to manage dense content.",
            builder=_collapsible_sections,
            keywords=("collapsible", "section", "panel"),
            best_for="Managing dense forms/panels with progressive reveal.",
            use_when="you need expandable advanced sections.",
            sort_order=790,
            icon_name="chevrons-up-down",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.parameter_panel",
            title="Parameter Panel",
            subtitle="Compact parameter editor shell",
            description="Reusable parameter panel with text, slider and toggle fields.",
            builder=_parameter_panel,
            keywords=("parameter", "form", "panel"),
            best_for="Compact runtime parameter editing surfaces.",
            use_when="you need text/slider/toggle parameters in one shell.",
            sort_order=800,
            icon_name="settings",
        ),
        AssetCatalogEntrySpec(
            entry_id="asset.hero_panel",
            title="Hero Header Panel",
            subtitle="Reusable showcase/workspace hero",
            description="Top-level hero/header panel for dashboard showcase screens.",
            builder=_hero_panel,
            keywords=("hero", "header", "showcase"),
            best_for="Top-level workspace intros and showcase surfaces.",
            use_when="you need a premium header panel anchor.",
            sort_order=810,
            icon_name="sparkles",
        ),
    )
