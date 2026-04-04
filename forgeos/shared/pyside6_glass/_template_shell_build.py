from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSplitter, QVBoxLayout, QWidget

from .chrome import WindowChromeBar
from .controls import create_button
from .rendering import apply_surface_role
from .scene import build_glass_dialog_scene
from .visual_contracts import set_visual_properties
from ._template_layout import GlassPanelSlotHost, GlassTemplateActions, GlassTemplateCards, GlassTemplateSlots
from ._template_panels import GlassPanelFrame
from ._template_specs import GlassPanelSpec, GlassWorkspaceTabSpec
from ._template_tabs import GlassWorkspaceTabs


class _GlassPanelTemplateBuildMixin:
    def _card(self, card_kind: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setProperty("card", card_kind)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(6, 5, 6, 5)
        card_layout.setSpacing(4)
        return card, card_layout


    def _build(self) -> tuple[GlassTemplateSlots, GlassTemplateCards, GlassTemplateActions]:
        outer, content, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant=self._variant,
            apply_stylesheet=False,
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content)
        scene_layout.setContentsMargins(2, 2, 2, 2)
        scene_layout.setSpacing(0)

        shell = QFrame(self)
        shell.setObjectName("Shell")
        shell.setProperty("variant", self._variant)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(4, 4, 4, 4)
        shell_layout.setSpacing(4)

        if self._with_chrome:
            host = self.window() if isinstance(self.window(), QWidget) else self
            chrome = WindowChromeBar(host, title=self._title)
            shell_layout.addWidget(chrome)

        hero_card, hero_layout = self._card("hero")
        shell_layout.addWidget(hero_card)
        self._eyebrow_label = QLabel(self._eyebrow, hero_card)
        self._eyebrow_label.setProperty("role", "eyebrow")
        self._eyebrow_label.setAccessibleName("glass_hero_eyebrow")
        self._title_label = QLabel(self._title, hero_card)
        self._title_label.setProperty("role", "title")
        self._title_label.setAccessibleName("glass_hero_title")
        self._subtitle_label = QLabel(self._subtitle, hero_card)
        self._subtitle_label.setProperty("role", "subtitle")
        self._subtitle_label.setAccessibleName("glass_hero_subtitle")
        self._subtitle_label.setWordWrap(True)
        hero_layout.addWidget(self._eyebrow_label)
        hero_layout.addWidget(self._title_label)
        hero_layout.addWidget(self._subtitle_label)

        body = QWidget(shell)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(2)

        tabs: GlassWorkspaceTabs | None = None
        body_host_layout: QVBoxLayout = body_layout
        if self._enable_workspace_tabs:
            tabs = GlassWorkspaceTabs(
                shell,
                tabs_closable=self._tabs_closable,
                movable=self._tabs_movable,
                document_mode=self._tabs_document_mode,
                placement=self._tabs_placement,
                density=self._tabs_density,
                variant=self._tabs_variant,
                icon_mode=self._tabs_icon_mode,
                hide_if_single_visible=self._tabs_hide_single,
                overflow_scroll_buttons=self._tabs_overflow_scroll,
            )
            body_layout.addWidget(tabs, 1)
            workspace_page = QWidget(tabs)
            workspace_layout = QVBoxLayout(workspace_page)
            workspace_layout.setContentsMargins(0, 0, 0, 0)
            workspace_layout.setSpacing(2)
            tabs.add_workspace_tab(
                GlassWorkspaceTabSpec(
                    tab_id=self._default_tab_id,
                    title=self._default_tab_title,
                    state="visible",
                    icon_name="layers",
                ),
                workspace_page,
                make_current=True,
            )
            body_host_layout = workspace_layout
            self.workspace_tabs = tabs

        split = QSplitter(Qt.Horizontal, body)
        split.setChildrenCollapsible(False)
        body_host_layout.addWidget(split, 1)

        main_panel = GlassPanelFrame(
            GlassPanelSpec(
                panel_id="main",
                title="Main Panel",
                role="workspace",
                subtitle="Primary work context.",
                card_kind="true",
            ),
            split,
        )
        side_panel = GlassPanelFrame(
            GlassPanelSpec(
                panel_id="side",
                title="Side Panel",
                role="detail",
                subtitle="Secondary or inspection context.",
                card_kind="muted",
            ),
            split,
        )
        split.addWidget(main_panel)
        split.addWidget(side_panel)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        main_panel.setProperty("slotShell", True)
        side_panel.setProperty("slotShell", True)
        set_visual_properties(main_panel, role="panel_workspace", variant="panel", emphasis="normal", fx_level="normal")
        set_visual_properties(side_panel, role="panel_detail", variant="panel", emphasis="normal", fx_level="normal")
        self._slot_shell_ids = {"main", "side"}
        main_slot_host = GlassPanelSlotHost("main", main_panel)
        side_slot_host = GlassPanelSlotHost("side", side_panel)
        main_panel.set_content_widget(main_slot_host)
        side_panel.set_content_widget(side_slot_host)
        self.layout_controller.register_splitter(
            "main_side",
            split,
            default_sizes=self._default_main_side_sizes,
        )
        for layout_name, payload in self._layout_named_presets.items():
            self.layout_controller.default_sizes.setdefault(
                f"named::{layout_name}",
                [int(v) for v in payload.get("main_side", self._default_main_side_sizes)]
                if isinstance(payload, dict)
                else list(self._default_main_side_sizes),
            )
        if not self._show_side:
            self.layout_controller.set_collapsed("main_side", 1, True)

        footer = QFrame(self)
        footer.setProperty("card", "footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(6, 4, 6, 4)
        footer_layout.setSpacing(4)
        shell_layout.addWidget(footer)
        if not self._show_footer or not self._include_default_actions:
            footer.hide()

        status = QFrame(self)
        status.setProperty("card", "muted")
        status.setProperty("panelRole", "aux")
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(6, 4, 6, 4)
        status_layout.setSpacing(4)
        shell_layout.addWidget(status)
        status.hide()

        shell_layout.insertWidget(shell_layout.count() - 2, body, 1)

        self._status_label = QLabel("", status)
        self._status_label.setProperty("role", "hint")
        self._status_label.setAccessibleName("glass_status_message")
        self._status_label.setWordWrap(True)
        self._status_label.hide()
        status_layout.addWidget(self._status_label)

        cancel_button: QPushButton | None = None
        submit_button: QPushButton | None = None
        if self._show_footer:
            footer_layout.addStretch(1)
            if self._include_default_actions:
                cancel_button = create_button(
                    self._cancel_text,
                    self._cancel_variant,
                    parent=footer,
                    icon_name="x",
                    icon_size="small",
                )
                submit_button = create_button(
                    self._submit_text,
                    self._submit_variant,
                    parent=footer,
                    icon_name="check",
                    icon_size="small",
                )
                cancel_button.setShortcut(self._secondary_shortcut)
                submit_button.setShortcut(self._primary_shortcut)
                cancel_button.setAccessibleName("glass_action_cancel")
                submit_button.setAccessibleName("glass_action_submit")
                footer_layout.addWidget(cancel_button, 0, Qt.AlignRight)
                footer_layout.addWidget(submit_button, 0, Qt.AlignRight)

        self._panels["main"] = main_panel
        self._panels["side"] = side_panel

        slots = GlassTemplateSlots(
            hero_slot=hero_layout,
            main_slot=main_slot_host.host_layout,
            side_slot=side_slot_host.host_layout,
            footer_slot=footer_layout,
            status_slot=status_layout,
            workspace_tabs=tabs,
        )
        cards = GlassTemplateCards(
            shell=shell,
            hero=hero_card,
            main=main_panel,
            side=side_panel,
            footer=footer,
            status=status,
            body=body,
        )
        actions = GlassTemplateActions(
            cancel_button=cancel_button,
            submit_button=submit_button,
        )
        return slots, cards, actions

__all__ = ["_GlassPanelTemplateBuildMixin"]
